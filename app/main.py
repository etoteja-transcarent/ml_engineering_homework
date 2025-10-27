from fastapi import FastAPI, File, UploadFile
from app.models import ParseResponse, Form1040DynamicFields
from app.textract_helper import analyze_1040
from app.vlm_helper import extract_fields_with_vlm
from dotenv import load_dotenv
from typing import Dict, List
import re

load_dotenv()

app = FastAPI()

# Keep numeric values, decimals, and signs
numeric_regex = re.compile(r"[^\d\.\-]")
# Normalize whitespace
whitespace_regex = re.compile(r"\s+")

def parse_money(text: str | None) -> float | None:
    """Parse monetary strings into float values"""
    if not text:
        return None
    cleaned = numeric_regex.sub("", text)
    # Handle invalid cases, should be integer or float
    if cleaned in ("", "-", ".", "-."):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None

def build_block_index(blocks: List[dict]) -> dict:
    """Index blocks by ID for easy and fast lookup"""
    return {b["Id"]: b for b in blocks}

def child_text_retriever(idx: Dict[str, dict], block: dict) -> str:
    """
    Get readable text for all CHILD elements of a block
    Uses LINE text if available
    Otherwise use WORD text
    """
    # If no block or no relationships, return empty text
    if not block or "Relationships" not in block:
        return ""
    
    # Collect text from LINEs or WORDs
    line_texts: List[str] = []
    word_texts: List[str] = []
    
    # Inspect each relationship in this block
    for relationship in block.get("Relationships", []):
        # Only care about CHILD relationships
        if relationship.get("Type") != "CHILD":
            continue
        # Each CHILD has an ID pointing to another block
        for child_id in relationship.get("Ids", []):
            child = idx.get(child_id)
            if not child:
                continue
            block_type = child.get("BlockType")
            if block_type == "LINE":
                child_text = child.get("Text", "")
                if child_text:
                    line_texts.append(child_text)
            elif block_type == "WORD":
                child_text = child.get("Text", "")
                if child_text:
                    word_texts.append(child_text)

    # Prefer LINE text if available, otherwise use WORD text
    if line_texts:
        total_text = " ".join(line_texts)
    else:
        total_text = " ".join(word_texts)

    # Normalize whitespace and return clean string
    return whitespace_regex.sub(" ", total_text).strip()

def value_text_retriever(idx: Dict[str, dict], key_block: dict) -> str:
    """Get the text connected to a KEY block"""
    # Look at each relationship the key block has
    for rel in key_block.get("Relationships", []):
        # Only care about VALUE relationships
        if rel.get("Type") == "VALUE":
            # Go through all the value block IDs connected to this key
            for value_id in rel.get("Ids", []):
                # Look up the value block by ID in our index
                value_block = idx.get(value_id)
                if value_block:
                    # Extract text from the value block
                    v = child_text_retriever(idx, value_block)
                    if v:
                        # Stop at the first one
                        return v.strip()
    
    # If no value found, return empty string
    return ""


def textract_to_dict(blocks: List[dict]) -> Dict[str, str]:
    """
    Convert Textract Blocks into dictionary
    """
    textract_dict = {}
    idx = build_block_index(blocks)
    for block in blocks:
        if block.get("BlockType") == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
            key_text = child_text_retriever(idx, block).lower().strip()
            value_text = value_text_retriever(idx, block)
            # Only if we have both key and value
            if key_text and value_text:
                textract_dict[key_text] = value_text
    return textract_dict

def is_line_match(key_text: str, n: int, *need: str) -> bool:
    """Matching line number with required substring(s)"""
    # Makes it easier to match whole words this way
    key_text = " " + key_text.strip().lower() + " "
    # Check if the text starts with the line number
    starts_with_line = key_text.startswith(f" {n} ")
    # Check if it contains "line {n}" in the middle
    contains_line = f" line {n} " in key_text
    # Check if it ends with the line number
    ends_with_line = key_text.endswith(f" {n} ")
    # Combine all three checks
    has_line_number = starts_with_line or contains_line or ends_with_line

    return has_line_number and all(substring in key_text for substring in need)

def fill_commonly_blank_fields(dyn: Form1040DynamicFields, field_name: str, default_value: float) -> None:
    """Fill commonly blank fields with default values"""
    # Most likely filling with 0.0
    if Form1040DynamicFields.get_field(dyn, field_name) is None:
        Form1040DynamicFields.add_field(dyn, field_name, default_value)


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return ParseResponse(success=False, error=str(exc)).__dict__


@app.get("/")
def root():
    return {"message": "1040 Parser API"}


@app.post("/parse-1040")
async def parse_1040(file: UploadFile = File(...)):
    """Parse a 1040 form using AWS Textract"""
    if file.filename and not file.filename.lower().endswith('.pdf'):
        return ParseResponse(success=False, error="Only PDF files are supported")
    
    try:
        doc_bytes = await file.read()
    except Exception as e:
        return ParseResponse(success=False, error=f"Error reading file: {str(e)}")
    
    try:
        textract_response = analyze_1040(doc_bytes)
    except Exception as e:
        return ParseResponse(success=False, error=f"Textract error: {str(e)}")
    
    blocks = textract_response.get('Blocks', [])
    textract_dict = textract_to_dict(blocks)
    dyn = Form1040DynamicFields()
    # Could add textract_dict to dyn fields for less overall compute

    for key_text, value_text in textract_dict.items():
        if is_line_match(key_text, 9, "total", "income") or "9 add lines" in key_text:
            val = parse_money(value_text)
            if val is not None:
                Form1040DynamicFields.add_field(dyn, "line_9", val)
                continue
        if (is_line_match(key_text, 10, "adjustment")
            or (key_text.endswith(' 10') and 'adjustment' in key_text)):
            val = parse_money(value_text)
            if val is not None:
                Form1040DynamicFields.add_field(dyn, "line_10", val)
                continue
        if (is_line_match(key_text, 11, "adjusted", "gross", "income")
            or (is_line_match(key_text, 11) and 'subtract' in key_text)):
            val = parse_money(value_text)
            if val is not None:
                Form1040DynamicFields.add_field(dyn, "line_11", val)
                continue
        if is_line_match(key_text, 12, "deduction") and ("standard" in key_text or "itemized" in key_text):
            val = parse_money(value_text)
            if val is not None:
                Form1040DynamicFields.add_field(dyn, "line_12", val)
                continue
        if is_line_match(key_text, 13, "qualified", "deduction"):
            val = parse_money(value_text)
            # Seemingly commonly left empty, filling with 0.0 if found but empty
            if val is not None:
                Form1040DynamicFields.add_field(dyn, "line_13", val)
            else:
                Form1040DynamicFields.add_field(dyn, "line_13", 0.0)
            continue
        if is_line_match(key_text, 14, "total", "deductions") or "14 add lines" in key_text:
            val = parse_money(value_text)
            if val is not None:
                Form1040DynamicFields.add_field(dyn, "line_14", val)
                continue
    
    # Can absolutely remove this and change validation logic later
    fill_commonly_blank_fields(dyn, "line_13", 0.0)
    
    # VLM Fallback if line content is missing from Textract extraction
    if not all(field_name in dyn.fields for field_name in ("line_9", "line_10", "line_11")):
        try:
            vlm_data = extract_fields_with_vlm(doc_bytes)
            for line in ("line_9", "line_10", "line_11", "line_12", "line_13", "line_14"):
                vlm_value = vlm_data.get(line)
                # Ensures VLM output is numeric
                if vlm_value is not None and isinstance(vlm_value, (int, float)):
                    Form1040DynamicFields.add_field(dyn, line, float(vlm_value))
            Form1040DynamicFields.add_field(dyn, "source", "vlm")
            
        # If both VLM and Textract fail, return error
        except Exception:
            return ParseResponse(success=False, error="Could not parse all required fields")
    else:
        Form1040DynamicFields.add_field(dyn, "source", "textract")
    
    # Final check to ensure required fields are present after VLM extraction
    if not all(name in dyn.fields for name in ("line_9", "line_10", "line_11")):
        return ParseResponse(success=False, error="Could not parse all required fields")
    
    # Include both line 11 and line 14 validation results, requiring both to be valid
    # Can absolutely change to just validating line 11 calculation
    is_valid = (Form1040DynamicFields.validate_line_11_totals(dyn) 
                and Form1040DynamicFields.validate_line_14_totals(dyn))

    Form1040DynamicFields.add_field(dyn, "is_valid", is_valid)
    
    return ParseResponse(success=True, fields=dyn.fields)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
