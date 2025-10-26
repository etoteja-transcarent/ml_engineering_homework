from typing import Dict, Any

# Prompt for VLM to extract lines 9 to 14 from Form 1040
# Generated with help of OpenAI's ChatGPT
PROMPT_1040_LINES_9_TO_14 = """
You are extracting numeric values from IRS Form 1040 (first page).
Return ONLY a compact JSON object with keys:
line_9, line_10, line_11, line_12, line_13, line_14.

Rules:
- Values must be numbers that are representable as floats (no commas, no $).
- If a line is empty on the form, use 0.0 for that line.
- Do not include any text outside the JSON.
- If the page is not a 1040 or fields are unreadable, return: {"error": "unreadable"}.

Clarifications:
- line_12 = standard deduction OR itemized deductions (whichever is filled).
- line_13 = Qualified business income deduction (commonly 0.0).
- line_14 = total deductions.
- line_11 should equal line_9 - line_10 (but do not compute it if clearly printed).
- line_14 should equal line_12 + line_13 (but do not compute it if clearly printed).
Example output:
{"line_9": 85000.0, "line_10": 5000.0, "line_11": 80000.0,
 "line_12": 12550.0, "line_13": 0.0, "line_14": 12550.0}
"""

def extract_fields_with_vlm(document_bytes: bytes) -> Dict[str, Any]:
    """
    VLM fallback
    Sample code below to call OpenAI's GPT-4o-vision model
    In production, would send document_bytes along with prompt
    Can modify prompt to alter lines extracted or even files extracted into document_bytes
    Response is JSON returned as a dict
    """
    
    # client = openai.Client()
    # response = client.chat.completions.create(
    #     model="gpt-4o-vision-preview",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": PROMPT_1040_LINES_9_TO_14,
    #          "attachments": [{"type": "file", "file": document_bytes}]}
    #     ]
    # )
    # content = response.choices[0].message.content
    # return json.loads(content)
    
    raise RuntimeError("VLM not configured. Mock extract_fields_with_vlm in tests.")
