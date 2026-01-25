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


_STOP_WORDS = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas",
    "com", "por", "para", "pra", "pelo", "pela",
    "e", "ou", "que", "foi",
    "gastei", "paguei", "compra", "comprei", "pagamento", "transferencia", "transferência",
    "valor", "custo", "reais", "real", "r$"
}

def clean_description(text: str) -> Dict[str, Any]:
    if not text:
        return {"status": "error", "error": "empty_text"}
    
    # 1. Remove valores numéricos (preserva texto)
    cleaned = _amount_pattern.sub(" ", text)
    
    # 2. Normalização básica
    cleaned = cleaned.lower()
    
    # 3. Remove stop words e tokens irrelevantes
    tokens = cleaned.split()
    filtered_tokens = [t for t in tokens if t not in _STOP_WORDS]
    
    # Reconstrói string
    cleaned = " ".join(filtered_tokens).strip()
    
    return {"status": "success", "description": cleaned}

def detect_direction(text: str) -> Dict[str, Any]:
    if not text:
        return {"status": "error", "error": "empty_text"}
    t = text.lower()
    income_markers = ["recebi","salário","salario","pix recebido","reembolso","deposito","depósito","renda","entrada"]
    if any(m in t for m in income_markers):
        return {"status": "success", "direction": "income"}
    return {"status": "success", "direction": "expense"}
