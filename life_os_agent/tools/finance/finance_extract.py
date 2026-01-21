from __future__ import annotations
import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any

_amount_pattern = re.compile(
    r"""(?ix)
    (?:r\$\s*)?
    (?:
        \d{1,3}(?:\.\d{3})+
        |\d+
    )
    (?:[,\.]\d{2})?
    """
)

def _to_decimal_brl(s: str) -> Optional[Decimal]:
    s = s.strip().lower().replace("r$", "").strip().replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def extract_amount_brl(text: str, default_currency: str = "BRL") -> Dict[str, Any]:
    if not text:
        return {"status": "error", "error": "empty_text"}
    matches = _amount_pattern.findall(text)
    if not matches:
        return {"status": "success", "amount": None, "currency": default_currency}
    for m in reversed(matches):
        val = _to_decimal_brl(m)
        if val is not None:
            return {"status": "success", "amount": float(val), "currency": default_currency}
    return {"status": "success", "amount": None, "currency": default_currency}

def clean_description(text: str) -> Dict[str, Any]:
    if not text:
        return {"status": "error", "error": "empty_text"}
    cleaned = _amount_pattern.sub(" ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return {"status": "success", "description": cleaned}

def detect_direction(text: str) -> Dict[str, Any]:
    if not text:
        return {"status": "error", "error": "empty_text"}
    t = text.lower()
    income_markers = ["recebi","salário","salario","pix recebido","reembolso","deposito","depósito","renda","entrada"]
    if any(m in t for m in income_markers):
        return {"status": "success", "direction": "income"}
    return {"status": "success", "direction": "expense"}
