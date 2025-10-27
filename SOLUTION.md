# SOLUTION.md

## What I Did

I cleaned up the parser code in main.py, added support for more fields, and put in a VLM placeholder (with commented out code) as a fallback option if Textract doesn’t give us the required lines. I also made sure the pytests cover these changes.

## Focus Areas

1. **Refactoring for Clarity and Reusability**  
   The original code wasn't the easiest to understand, maintain, or add new fields to. I created some helper functions for parsing the Textract output (namely build_block_index, child_text_retriever, value_text_retriever, textract_to_dict, is_line_match, and fill_commonly_blank_fields) so that adding more line items in the future is much simpler. Comments within each helper explain their purpose and function. I also added a REGEX-based helper function to extract the monetary value more cleanly.

2. **Data Model Changes**  
   I used a dynamic dictionary (Form1040DynamicFields) that we can keep adding fields to, as to not limit ourselves to specific line numbers. I also added a "source" field to log whether Textract or VLM was used for the extraction. The API still returns a schema that passes the test cases.

3. **Adding Lines 12–14**  
   - **Line 12:** Standard or Itemized Deductions  
   - **Line 13:** Qualified Business Income Deduction
   - **Line 14:** Total deductions  
   I also added a check that line 14 = line 12 + line 13, alongside the existing line 11 check. I required both to set the is_valid flag to True and added the new lines to the pytest cases.

4. **VLM Fallback**  
   If Textract misses key lines (namely lines 9 through 11), the code now tries a VLM fallback (`extract_fields_with_vlm`). For now, that function just raises an execption, unless mocked in tests, but the hook is in place for production.

---

## Key Decisions

- Used small helper functions to cut down on repeating code and make line matching more digestable to reader
- Didn't change any existing and expected fields in the output of the API
- Didn't alter any existing test cases (apart from adding lines 12 through 14 in the assert statements)
- Validation requires correct totals (within acceptable range) for both lines 11 and 14
- Defaulted line_13 to 0.0 so tests pass and works with cases where the PDFs have empty values for line 13
- Added "source" to the output to make debugging easier

---

## With More Time/Trade-Offs

- Generalize classes and code to work with other tax forms. The line matching in main.py is not significantly more robust than it was before; it's just cleaner and more extensible. I would love to speak with SMEs on better understanding the layouts of these and many other tax-forms.
- Connect to OpenAI for true VLM backup testing. The VLM code is completely mocked and virtually untested, but the prompt did work directly in ChatGPT with the sample files.
- Understand necessity of validation for line 14 and "error" handling for an empty line 13. Defaulting `line_13` to 0.0 was to pass the updated pytest case, but I am not sure if this was the right decision. A blank field might not mean the same as 0.0 value.

---

