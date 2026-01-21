from __future__ import annotations
from typing import Dict, Any, Optional

# Demo: 1 pendência por processo (bom pra testes locais)
_PENDING: Optional[Dict[str, Any]] = None

def has_pending_transaction() -> Dict[str, Any]:
    return {"status": "success", "has_pending": _PENDING is not None}

def set_pending_transaction(payload: Dict[str, Any]) -> Dict[str, Any]:
    global _PENDING
    _PENDING = payload
    return {"status": "success", "stored": True}

def get_pending_transaction() -> Dict[str, Any]:
    return {"status": "success", "pending": _PENDING}

def clear_pending_transaction() -> Dict[str, Any]:
    global _PENDING
    _PENDING = None
    return {"status": "success", "cleared": True}
