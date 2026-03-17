# ============================================================
#  doc_validator.py  —  Verify uploaded document matches
#                        the doc type selected by the user.
#
#  APPROACH — dual check (your idea):
#
#  Every document has TWO types of unique identifiers:
#    1. keywords   — text only that doc contains
#                    e.g. "Permanent Account Number", "UIDAI"
#    2. id_pattern — unique number format for that doc
#                    e.g. Aadhaar = 12 digits, PAN = ABCDE1234F
#
#  To confirm a document we check:
#       keyword found   →  VALID  ✓
#       OR
#       id_pattern found  →  VALID  ✓
#       BOTH missing    →  INVALID ✗  (return error to user)
#
#  WHY BOTH?
#  Low quality scans or blurry images may cause OCR to miss
#  keywords like "Aadhaar" but still capture the 12-digit
#  number clearly (numbers OCR better than stylized text).
#  Having both checks makes the validator much more reliable.
# ============================================================

import re


# ── Document signature rules ─────────────────────────────────
#
# keywords   : list of text strings — at least ONE must be
#              present in OCR text (case-insensitive)
#
# id_pattern : regex for the unique ID number of that doc.
#              At least ONE match = document confirmed.
#
# label      : human-readable name shown in error messages

DOC_SIGNATURES = {

    "P": {
        "label": "PAN Card",
        "keywords": [
            "permanent account number",
            "income tax department",
        ],
        # PAN format: 5 letters, 4 digits, 1 letter  e.g. ABCDE1234F
        "id_pattern": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    },

    "A": {
        "label": "Aadhaar Card",
        "keywords": [
            "aadhaar",
            "uidai",
            "unique identification",
            "enrolment no",
        ],
        # Aadhaar: exactly 12 digits (may have spaces like 1234 5678 9012)
        "id_pattern": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    },

    "V": {
        "label": "Voter ID Card",
        "keywords": [
            "election commission",
            "elector",
            "electors photo identity",
            "epic",
        ],
        # Voter ID format: 3 uppercase letters + 7 digits  e.g. ABC1234567
        "id_pattern": r"\b[A-Z]{3}[0-9]{7}\b",
    },

    "D": {
        "label": "Driving Licence",
        "keywords": [
            "driving licence",
            "motor vehicles act",
            "transport department",
            "licence no",
        ],
        # DL format: 2 letters + 2 digits + 11 digits  e.g. MH1220110123456
        "id_pattern": r"\b[A-Z]{2}[0-9]{2}[0-9]{11}\b",
    },

    "B": {
        "label": "Bank Passbook",
        "keywords": [
            "ifsc",
            "account no",
            "a/c no",
            "cif no",
            "passbook",
            "savings account",
            "current account",
        ],
        # IFSC code: 4 letters + 0 + 6 alphanumeric  e.g. SBIN0001234
        # More reliable than account number which varies per bank
        "id_pattern": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    },
}


# ── Helpers ──────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace for keyword matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _keyword_found(normalized_text: str, keywords: list) -> bool:
    """Return True if at least one keyword exists in the text."""
    return any(kw in normalized_text for kw in keywords)


def _id_found(raw_text: str, pattern: str) -> bool:
    """
    Return True if the ID number pattern is found in raw OCR text.
    Uses raw_text (not lowercased) because regex patterns depend
    on uppercase letters like PAN: ABCDE1234F.
    """
    return bool(re.search(pattern, raw_text))


# ── Main validator ───────────────────────────────────────────

def verify_document(ocr_text: str, selected_doctype: str) -> dict:
    """
    Verify the uploaded document matches the user-selected doc type.

    Checks keyword OR id_pattern — either one is enough to confirm.

    Returns:
        { "valid": True,  "matched_doctype": "AADHAAR",
          "match_reason": "keyword" or "id_number" }
        or
        { "valid": False, "error": "clear message for the user" }

    Usage in fast_api.py:
        result = verify_document(text, doctype)
        if not result["valid"]:
            raise HTTPException(status_code=400, detail=result["error"])
    """
    selected = selected_doctype.strip().upper()

    # ── Guard: unknown doc type ──────────────────────────────
    if selected not in DOC_SIGNATURES:
        valid_types = ", ".join(DOC_SIGNATURES.keys())
        return {
            "valid": False,
            "error": f"Unknown document type '{selected_doctype}'. "
                     f"Valid types: {valid_types}."
        }

    rules    = DOC_SIGNATURES[selected]
    normalized = _normalize(ocr_text)

    # ── Check 1: keyword match ───────────────────────────────
    if _keyword_found(normalized, rules["keywords"]):
        return {
            "valid": True,
            "matched_doctype": selected,
            "match_reason": "keyword"
        }

    # ── Check 2: ID number pattern match ────────────────────
    # Runs even if keyword check failed — blurry text may have
    # lost the keyword but numbers are usually still readable.
    if _id_found(ocr_text, rules["id_pattern"]):
        return {
            "valid": True,
            "matched_doctype": selected,
            "match_reason": "id_number"
        }

    # ── Both failed — detect what doc it actually is ─────────
    detected_label = _detect_actual_doctype(ocr_text, normalized, skip=selected)

    if detected_label:
        error_msg = (
            f"You selected '{rules['label']}' but the uploaded document "
            f"looks like a '{detected_label}'. "
            f"Please upload the correct document."
        )
    else:
        error_msg = (
            f"The uploaded document does not appear to be a '{rules['label']}'. "
            f"The document may be unclear or unsupported. "
            f"Please check your file and try again."
        )

    return {"valid": False, "error": error_msg}


def _detect_actual_doctype(raw_text: str, normalized: str, skip: str) -> str | None:
    """
    Scan all other doc types to figure out what was actually uploaded.
    Used only for building a helpful error message.
    """
    for doctype, rules in DOC_SIGNATURES.items():
        if doctype == skip:
            continue
        if _keyword_found(normalized, rules["keywords"]):
            return rules["label"]
        if _id_found(raw_text, rules["id_pattern"]):
            return rules["label"]
    return None