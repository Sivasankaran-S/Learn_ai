# ============================================================
#  langchain_llm.py  —  LLM extraction logic for DocAI
#
#  Key changes from old version:
#  1. All prompt templates moved to prompts.py (clean separation).
#  2. Each doc type now makes ONE llm.invoke() call instead of
#     TWO. Extract + summary are combined in one prompt.
#     This cuts LLM time roughly in half.
#  3. doc_type_check() now uses exact match (strip + upper)
#     instead of single-letter "in" checks which caused wrong
#     routing (e.g. "Passbook" matching "P" → PAN).
#  4. Aadhaar splitlines() was called twice — fixed.
#  5. Driving/Bank summary was receiving a Python list object
#     instead of a string — fixed by joining before passing.
#  6. JSON parse is now a shared helper (parse_llm_json) so
#     it's not copy-pasted in every branch.
# ============================================================

import json
import re
from langchain_ollama import ChatOllama
from Services.prompts import (
    PAN_PROMPT,
    AADHAAR_PROMPT,
    VOTERID_PROMPT,
    DRIVING_PROMPT,
    BANK_PROMPT,
)

# ── LLM model ──────────────────────────────────────────────
llm = ChatOllama(model="gemma3:1b")


# ── Shared JSON parser ──────────────────────────────────────
def parse_llm_json(raw: str) -> dict:
    """
    Strip markdown fences from LLM output and parse JSON.
    Raises ValueError if no valid JSON object is found.
    """
    clean = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in LLM response:\n{raw}")
    return json.loads(match.group())


# ── Doc type router ─────────────────────────────────────────
def doc_type_check(doc: str) -> str:
    mapping = {
        "P":      "PAN",
        "A":  "AADHAAR",
        "V":  "VOTERID",
        "D":  "DRIVING",
        "B":     "BANK",
    }
    return mapping.get(doc.strip().upper(), "UNKNOWN")


# ── Pre-extraction helpers ───────────────────────────────────
def _extract_pan_number(lines: list) -> str | None:
    """
    Find PAN number from OCR lines.
    Looks for the line after 'Permanent Account Number Card'
    and corrects common OCR character mistakes (O→0, I→1, S→5).
    """
    pan_digit_fix = {"O": "0", "I": "1", "S": "5"}
    for i, line in enumerate(lines):
        if "Permanent Account Number Card" in line:
            for candidate in lines[i + 1: i + 3]:
                candidate = candidate.strip()
                if len(candidate) >= 10:
                    chars = list(candidate)
                    for j in range(5, 9):   # positions 5-8 must be digits
                        if chars[j] in pan_digit_fix:
                            chars[j] = pan_digit_fix[chars[j]]
                    return "".join(chars[:10])
    return None


def _extract_aadhaar_number(lines: list) -> str | None:
    """
    Find 12-digit Aadhaar number from OCR lines.
    Skips lines that contain DOB or date separators to avoid
    mistaking date digits for the Aadhaar number.
    """
    for line in lines:
        upper = line.upper()
        if "DOB" in upper or "/" in line:
            continue
        digits = re.sub(r"\D", "", line)
        if len(digits) == 12:
            return digits
    return None


def _extract_voter_id(lines: list) -> str | None:
    """
    Find Voter ID number: exactly 3 uppercase letters + 7 digits.
    """
    for line in lines:
        match = re.fullmatch(r"[A-Z]{3}[0-9]{7}", line.strip())
        if match:
            return match.group()
    return None


# ── Main extraction function ─────────────────────────────────
def extract_details(ocr_txt: str, doc: str) -> dict:
    """
    Route OCR text to the correct extractor based on doc type.
    Returns a dict with keys: Doc_type, Extracted_text, Summary.

    Each branch:
    1. Pre-extracts high-confidence fields (numbers/IDs) with regex
       so the LLM doesn't have to guess them.
    2. Makes ONE llm.invoke() call using the combined prompt.
    3. Parses the returned JSON which includes both fields + summary.
    """
    document_type = doc_type_check(doc)
    lines = ocr_txt.splitlines()          # split once, reuse everywhere
    text = "\n".join(lines)               # clean joined string for prompts

    # ── PAN ────────────────────────────────────────────────
    if document_type == "PAN":
        pan_number = _extract_pan_number(lines)

        formatted = PAN_PROMPT.format(ocr_txt=text, pan_number=pan_number)
        result = llm.invoke(formatted)
        parsed = parse_llm_json(result.content)

        return {
            "Doc_type": document_type,
            "Extracted_text": {
                "NAME":          parsed.get("NAME"),
                "DATE_OF_BIRTH": parsed.get("DATE_OF_BIRTH"),
                "PAN_NUMBER":    parsed.get("PAN_NUMBER", pan_number),
            },
            "Summary": parsed.get("SUMMARY", []),
        }

    # ── AADHAAR ────────────────────────────────────────────
    elif document_type == "AADHAAR":
        aadhaar_no = _extract_aadhaar_number(lines)
        upper_text = text.upper()         # Aadhaar prompt expects uppercase
        print("Aadhar:",upper_text)
        formatted = AADHAAR_PROMPT.format(ocr_txt=upper_text, aadhaar_no=aadhaar_no)
        result = llm.invoke(formatted)
        parsed = parse_llm_json(result.content)
        print("parsed_data:",parsed)
        return {
            "Doc_type": document_type,
            "Extracted_text": {
                "NAME":           parsed.get("NAME"),
                "DATE_OF_BIRTH":  parsed.get("DATE_OF_BIRTH"),
                "GENDER":         parsed.get("GENDER"),
                "AADHAAR_NUMBER": parsed.get("AADHAAR_NUMBER", aadhaar_no),
                "ADDRESS":        parsed.get("ADDRESS"),
            },
            "Summary": parsed.get("SUMMARY", []),
        }

    # ── VOTER ID ───────────────────────────────────────────
    elif document_type == "VOTERID":
        voter_id = _extract_voter_id(lines)

        formatted = VOTERID_PROMPT.format(ocr_txt=text, voter_id=voter_id)
        result = llm.invoke(formatted)
        parsed = parse_llm_json(result.content)

        return {
            "Doc_type": document_type,
            "Extracted_text": {
                "NAME":           parsed.get("NAME"),
                "DATE_OF_BIRTH":  parsed.get("DATE_OF_BIRTH"),
                "GENDER":         parsed.get("GENDER"),
                "VOTERID_NUMBER": parsed.get("VOTERID_NUMBER", voter_id),
            },
            "Summary": parsed.get("SUMMARY", []),
        }

    # ── DRIVING LICENCE ────────────────────────────────────
    elif document_type == "DRIVING":
        formatted = DRIVING_PROMPT.format(ocr_txt=text)
        result = llm.invoke(formatted)
        parsed = parse_llm_json(result.content)

        return {
            "Doc_type": document_type,
            "Extracted_text": {
                "NAME":           parsed.get("NAME"),
                "DATE_OF_BIRTH":  parsed.get("DATE_OF_BIRTH"),
                "LICENCE_NUMBER": parsed.get("LICENCE_NUMBER"),
            },
            "Summary": parsed.get("SUMMARY", []),
        }

    # ── BANK PASSBOOK ──────────────────────────────────────
    elif document_type == "BANK":
        formatted = BANK_PROMPT.format(ocr_txt=text)
        result = llm.invoke(formatted)
        parsed = parse_llm_json(result.content)

        return {
            "Doc_type": document_type,
            "Extracted_text": {
                "NAME":           parsed.get("NAME"),
                "CIF_NUMBER":     parsed.get("CIF_NUMBER"),
                "ACCOUNT_NUMBER": parsed.get("ACCOUNT_NUMBER"),
                "IFSC_CODE":      parsed.get("IFSC_CODE"),
                "BRANCH_CODE":    parsed.get("BRANCH_CODE"),
                "BANK_NAME":      parsed.get("BANK_NAME"),
            },
            "Summary": parsed.get("SUMMARY", []),
        }

    # ── UNKNOWN ────────────────────────────────────────────
    else:
        return {
            "Doc_type":     "UNKNOWN",
            "Extracted_text": None,
            "Summary":      ["Document type not identified."],
        }