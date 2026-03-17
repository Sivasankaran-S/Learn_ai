# ============================================================
#  prompts.py  —  All LLM prompt templates for DocAI
#  Each doc type has ONE combined prompt: extract + summary
#  together. This means only 1 LLM call per document instead
#  of 2, which cuts response time roughly in half.
# ============================================================

from langchain_core.prompts import PromptTemplate


# ------------------------------------------------------------
# PAN CARD
# ------------------------------------------------------------
# Fix from old code:
# - Old code had two separate prompts (TMPT + Summary_template)
#   and called llm.invoke() twice.
# - Now extract + summary are merged into one prompt.
# - Old JSON had empty strings "" as defaults — changed to null
#   so the code can do a proper None check.
# - Removed stray "-" bullet at the end of the old summarize rules.
# ------------------------------------------------------------
PAN_TEMPLATE = """You are an expert PAN Card document extractor.

Extract details from the OCR text below.
Do NOT guess. If a value is missing, return null.

OCR TEXT:
{ocr_txt}

EXTRACTION RULES:
- NAME: Appears in UPPERCASE letters.
- DATE_OF_BIRTH: Format DD/MM/YYYY.
- PAN_NUMBER: Use the pre-extracted value provided — do not re-extract from text.

SUMMARY RULES:
- Maximum 5 lines, numbered 1 to 5.
- Use ONLY the extracted values above.
- Plain text only. No markdown, no asterisks, no bold, no symbols.
- No intro sentence like "Here is the summary" — start directly from line 1.
- No paragraphs or assumptions.

Return ONLY this JSON (no markdown, no extra text):

{{
  "NAME": null,
  "DATE_OF_BIRTH": null,
  "PAN_NUMBER": "{pan_number}",
  "SUMMARY": [
    "1. This is a PAN Card approved by GOVT. OF INDIA.",
    "2. Used for Income Tax regulations.",
    "3. Issued by the Income Tax Department.",
    "4. Permanent Account Number: {pan_number}.",
    "5. Considered an official document in India."
  ]
}}
"""

PAN_PROMPT = PromptTemplate(
    template=PAN_TEMPLATE,
    input_variables=["ocr_txt", "pan_number"]
)


# ------------------------------------------------------------
# AADHAAR CARD
# ------------------------------------------------------------
# Fix from old code:
# - Old aadhaar_template had bare values like "NAME": , (invalid JSON).
#   Changed to null as default.
# - Old AADHAAR_SUMMARY_TMPT was a second separate prompt.
#   Merged into one combined prompt.
# - ADDRESS was always passed as empty string "". Kept but noted.
# ------------------------------------------------------------
AADHAAR_TEMPLATE = """You are an expert Aadhaar Card document extractor.

Extract details from the OCR text below.
Do NOT guess. If a value is missing, return null.

OCR TEXT:
{ocr_txt}

EXTRACTION RULES:
- NAME:
  Its a person name.
  It will be in uppercase. 
  It is NOT a keyword like MALE, FEMALE, DOB, UIDAI, or INDIA.
  It appear before the line of DOB.
  Return the value WITHOUT changing spelling, WITHOUT changing case.
  Example:
  OCR: SIVA
  Output: SIVA
- DATE_OF_BIRTH: Format DD/MM/YYYY.
- GENDER: MALE / FEMALE / OTHER.
- AADHAAR_NUMBER: Use the pre-extracted value — do not re-extract.
- ADDRESS: Extract full address if present, else null.

SUMMARY RULES:
- Maximum 3 lines, numbered 1 to 3.
- Use ONLY the extracted values.
- Plain text only. No markdown, no asterisks, no bold, no symbols.
- No intro sentence like "Here is the summary" — start directly from line 1.
- No paragraphs or assumptions.

Return ONLY this JSON (no markdown, no extra text):

{{
  "NAME": null,
  "DATE_OF_BIRTH": null,
  "GENDER": null,
  "AADHAAR_NUMBER": "{aadhaar_no}",
  "ADDRESS": null,
  "SUMMARY": [
    "1. This is an Aadhaar Card issued by UIDAI.",
    "2. Used as identity and address proof in India.",
    "3. Considered an official government document."
  ]
}}
"""

AADHAAR_PROMPT = PromptTemplate(
    template=AADHAAR_TEMPLATE,
    input_variables=["ocr_txt", "aadhaar_no"]
)


# ------------------------------------------------------------
# VOTER ID
# ------------------------------------------------------------
# Fix from old code:
# - voterid_summary_template passed full ocr_txt into the
#   summary prompt — that is raw noisy OCR, not clean data.
#   Now summary is generated from the extracted JSON fields,
#   not raw OCR.
# - Merged into one combined prompt.
# ------------------------------------------------------------
VOTERID_TEMPLATE = """You are an expert Voter ID document extractor.

Extract details from the OCR text below.
Do NOT guess. If a value is missing, return null.

OCR TEXT:
{ocr_txt}

EXTRACTION RULES:
- NAME: Full name of the card holder.
- DATE_OF_BIRTH: Format DD-MM-YYYY.
- GENDER: MALE / FEMALE / OTHER.
- VOTERID_NUMBER: Use the pre-extracted value — do not re-extract.

SUMMARY RULES:
- Maximum 3 lines, numbered 1 to 3.
- Use ONLY the extracted values.
- Plain text only. No markdown, no asterisks, no bold, no symbols.
- No intro sentence like "Here is the summary" — start directly from line 1.
- No paragraphs or assumptions.

Return ONLY this JSON (no markdown, no extra text):

{{
  "NAME": null,
  "DATE_OF_BIRTH": null,
  "GENDER": null,
  "VOTERID_NUMBER": "{voter_id}",
  "SUMMARY": [
    "1. This is a Voter ID Card approved by GOVT. OF INDIA.",
    "2. Used for voting purposes in India.",
    "3. Considered an official identity document."
  ]
}}
"""

VOTERID_PROMPT = PromptTemplate(
    template=VOTERID_TEMPLATE,
    input_variables=["ocr_txt", "voter_id"]
)


# ------------------------------------------------------------
# DRIVING LICENCE
# ------------------------------------------------------------
# Fix from old code:
# - driving_summary_template passed ocr_txt (a list) directly
#   as string — that prints the Python list repr, not clean text.
#   Fixed: summary now comes from extracted fields only.
# - Merged into one combined prompt.
# ------------------------------------------------------------
DRIVING_TEMPLATE = """You are an expert Driving Licence document extractor.

Extract details from the OCR text below.
Do NOT guess. If a value is missing, return null.

OCR TEXT:
{ocr_txt}

EXTRACTION RULES:
- NAME: Person name in capital letters. If more than one name exists, pick the first alphabetic name.
- DATE_OF_BIRTH: Look near keywords like "DOB". Format DD-MM-YYYY.
- LICENCE_NUMBER: Starts with 2 capital letters, followed by 2 digits, then 11 digits (spaces allowed).

SUMMARY RULES:
- Maximum 3 lines, numbered 1 to 3.
- Use ONLY the extracted values.
- Plain text only. No markdown, no asterisks, no bold, no symbols.
- No intro sentence like "Here is the summary" — start directly from line 1.
- No paragraphs or assumptions.

Return ONLY this JSON (no markdown, no extra text):

{{
  "NAME": null,
  "DATE_OF_BIRTH": null,
  "LICENCE_NUMBER": null,
  "SUMMARY": [
    "1. This is a Driving Licence approved by GOVT. OF INDIA.",
    "2. Used as proof of authorization to drive vehicles in India.",
    "3. Considered an official identity document."
  ]
}}
"""

DRIVING_PROMPT = PromptTemplate(
    template=DRIVING_TEMPLATE,
    input_variables=["ocr_txt"]
)


# ------------------------------------------------------------
# BANK PASSBOOK
# ------------------------------------------------------------
# Fix from old code:
# - Old bank_template said "You are an OCR system" — wrong role,
#   confused the model. Changed to document extractor role.
# - bank_summary_tempalte had a typo in the variable name
#   (tempalte). Fixed.
# - Passing ocr_txt list directly to summary prompt was a bug.
#   Merged into one combined prompt using extracted fields.
# ------------------------------------------------------------
BANK_TEMPLATE = """You are an expert Bank Passbook document extractor.

Extract details from the OCR text below.
Do NOT guess. Extract ONLY fields whose exact label is present in the text.
If a value is missing or label not found, return null.

OCR TEXT:
{ocr_txt}

EXTRACTION RULES:
- NAME: Labeled as "Name" in the text.
- CIF_NUMBER: Labeled as "CIF No" in the text. Do NOT confuse with account number.
- ACCOUNT_NUMBER: Labeled as "Account No", "A/C No", or "Account Number".
- IFSC_CODE: Labeled as "IFSC" or "IFSC Code".
- BRANCH_CODE: Labeled as "Branch Code".
- BANK_NAME: Name of the bank if visible.

SUMMARY RULES:
- Maximum 3 lines, numbered 1 to 3.
- Use ONLY the extracted values.
- Plain text only. No markdown, no asterisks, no bold, no symbols.
- No intro sentence like "Here is the summary" — start directly from line 1.
- No paragraphs or assumptions.

Return ONLY this JSON (no markdown, no extra text):

{{
  "NAME": null,
  "CIF_NUMBER": null,
  "ACCOUNT_NUMBER": null,
  "IFSC_CODE": null,
  "BRANCH_CODE": null,
  "BANK_NAME": null,
  "SUMMARY": [
    "1. This is a Bank Passbook.",
    "2. Issued by the bank.",
    "3. Used as proof of account and identity in India."
  ]
}}
"""

BANK_PROMPT = PromptTemplate(
    template=BANK_TEMPLATE,
    input_variables=["ocr_txt"]
)