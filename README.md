# Take-Home Challenge: 1040 Tax Form Parser

## Getting Started

**Important**: Please clone this repository to your own private repo and work there. Do not fork it or submit a PR to this repo. Keep your work private between us.

## Overview

This repository contains a working FastAPI application that uses AWS Textract to parse numeric fields from IRS Form 1040. The code works, but it was written quickly and needs refactoring. Your task is to improve the codebase and add some new functionality.

**Note**: We'll use your solution as the discussion points in follow-up interviews, so be prepared to talk through your design decisions and approach.

**Time Expectation:** ~4.5 hours

## Current State

The application currently:
- Accepts a 1040 PDF document via multipart/form-data file upload
- Calls AWS Textract to extract key-value pairs
- Parses three numeric fields (lines 9, 10, and 11)
- Validates that line 11 equals line 9 minus line 10
- Returns the parsed fields with a validation status

All tests pass and use mocked Textract responses, so no AWS credentials are needed to run them.

## Part 1: Refactor for Extensibility (2 hours)

Take a look at the existing code. It works, but imagine we need to:
- Add support for parsing many more fields from Form 1040 (there are dozens)
- Eventually support other tax forms (Schedule A, Schedule B, etc.)
- Make it easy for other developers to maintain and extend

Refactor the code with these future needs in mind. Focus on making the codebase clean and extensible rather than trying to implement every possible improvement.

**It's completely fine if you don't address everything you'd like to improve.** Just document what you would do next in your SOLUTION.md.

## Part 2: Add More Fields (1 hour)

Now that the code is cleaner, add support for three more fields from the 1040:

- **Line 12**: Standard deduction or itemized deductions
- **Line 13**: Qualified business income deduction  
- **Line 14**: Total deductions

### Test Fixtures

The test fixtures in `tests/fixtures/` contain realistic Textract responses from actual 1040 forms. These fixtures correspond to the PDF files in `example_documents/`:

- `2024_peter_and_paula_professor.json` → `2024_Peter_and_Paula_Professor.pdf`
- `2024_samuel_singletary.json` → `2024 Samuel Singletary.pdf`
- `sample_1040_invalid.json` → A test case for invalid/incomplete Textract responses

You can use these fixtures to develop and test your parsing logic locally - no AWS credentials needed.

## Part 3: Add VLM Fallback (1 hour)

Sometimes Textract fails or returns incomplete data. Add a fallback mechanism that uses a Visual Language Model (GPT-5, GPT-4 Vision or Claude) when Textract doesn't work.

The fallback should:
- Kick in automatically when Textract fails or returns incomplete results
- Use either GPT or Claude (your choice)
- Extract the same fields we're currently parsing
- Indicate in the response which method was used (Textract vs. VLM)

**Important**: Write prompts that would actually parse the document. You can test your prompts using the free tiers of ChatGPT or Claude - both allow you to upload PDFs and test your prompts to see the output. Your prompts don't need to be production-ready, but they should successfully extract the required fields when tested. For testing purposes in your code, mock the API responses so you don't need paid API keys.

## Setup

**Prerequisites**: Python 3.13 or higher and pip

1. Clone this repo to your own private repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the tests: `pytest -v` (they should all pass)
4. Start the API: `uvicorn app.main:app --reload`
5. Check out the interactive docs at `http://localhost:8000/docs`


## What to Submit

Commit your changes directly to the master branch of your cloned repo. When you're done, please include:

- **SOLUTION.md** - a brief write-up covering:
  - What you focused on and why
  - Key design decisions you made
  - What you would do next if you had more time
  - Any trade-offs or assumptions you made

Once you're ready, share the repo with us.

## A Few Notes

- **Don't be afraid to change existing code.** If you see a better way to do something, go ahead and refactor it. Remove code that doesn't make sense, restructure things, whatever you think is best.
- **Feel free to add dependencies** if they make sense - just update `requirements.txt`.
- **Ask questions** if anything is unclear. Reach out to your contact anytime.

## Time Guidelines

- Part 1 (Refactor): ~2 hours
- Part 2 (Additional fields): ~1 hour  
- Part 3 (VLM fallback): ~1 hour
- Write-up: ~15-20 minutes

These are rough guidelines - spend time where you think it makes the most sense.

