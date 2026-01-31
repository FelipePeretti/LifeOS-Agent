from __future__ import annotations

import re
from typing import Any, Dict, List

from life_os_agent.tools.finance.finance_extract import (
    clean_description,
    detect_direction,
    extract_amount_brl,
)
from life_os_agent.tools.finance.finance_ml import predict_category_ptbr
from life_os_agent.tools.finance.time_utils import now_ts_iso

CATEGORIES_PTBR: List[str] = [
    "Renda",
    "Mercado",
    "Moradia",
    "Transporte",
    "Lazer",
    "Saúde",
    "Assinaturas",
    "Educação",
    "Viagem",
    "Outros",
]

_FINANCE_HINTS = [
    "r$",
    "pix",
    "uber",
    "ifood",
    "mercado",
    "aluguel",
    "netflix",
    "spotify",
    "paguei",
    "gastei",
    "comprei",
    "assinatura",
    "boleto",
    "cartão",
    "cartao",
    "recebi",
    "salário",
    "salario",
    "depósito",
    "deposito",
    "transferência",
    "transferencia",
]
_AMOUNT_RE = re.compile(r"(?i)(?:r\$\s*)?\d+(?:[.,]\d{2})?")


def is_finance_related(text: str) -> Dict[str, Any]:
    if not text:
        return {"status": "success", "is_finance": False}
    t = text.lower()
    if any(h in t for h in _FINANCE_HINTS):
        return {"status": "success", "is_finance": True}
    if _AMOUNT_RE.search(t):
        return {"status": "success", "is_finance": True}
    return {"status": "success", "is_finance": False}


def make_transaction_payload(
    raw_text: str, confidence_threshold: float = 0.55
) -> Dict[str, Any]:
    if not raw_text:
        return {"status": "error", "error": "empty_text"}

    amt = extract_amount_brl(raw_text)
    desc = clean_description(raw_text)
    direc = detect_direction(raw_text)
    ts = now_ts_iso()

    description = desc.get("description", raw_text)

    pred = predict_category_ptbr(description)

    payload = {
        "amount": amt.get("amount"),
        "currency": amt.get("currency", "BRL"),
        "direction": direc.get("direction", "expense"),
        "category": pred.get("category", "Outros"),
        "confidence": float(pred.get("confidence", 0.0)),
        "description": description,
        "raw_text": raw_text,
        "ts_iso": ts.get("ts_iso"),
    }

    if payload["amount"] is None:
        return {
            "status": "need_confirmation",
            "transaction_payload": payload,
            "message_draft": "Não encontrei o valor. Qual foi o valor (em R$) desse gasto/receita?",
        }

    if payload["confidence"] < confidence_threshold:
        return {
            "status": "need_confirmation",
            "transaction_payload": payload,
            "message_draft": f"Confirma a categoria '{payload['category']}' para o valor {payload['amount']} {payload['currency']}?",
        }

    return {
        "status": "ok",
        "transaction_payload": payload,
        "message_draft": f"Registrado: {payload['category']} — {payload['amount']} {payload['currency']}.",
    }


def apply_confirmation(
    user_text: str, pending_payload: Dict[str, Any]
) -> Dict[str, Any]:
    if not pending_payload:
        return {"status": "error", "error": "no_pending"}

    t = (user_text or "").strip().lower()

    if any(
        k in t for k in ["cancelar", "cancela", "esquece", "não salva", "nao salva"]
    ):
        return {
            "status": "cancelled",
            "transaction_payload": pending_payload,
            "message_draft": "Ok, cancelei esse lançamento.",
        }

    for cat in CATEGORIES_PTBR:
        if cat.lower() in t:
            pending_payload["category"] = cat
            pending_payload["confidence"] = 1.0
            return {
                "status": "ok",
                "transaction_payload": pending_payload,
                "message_draft": f"Fechado: categoria ajustada para {cat}.",
            }

    m = _AMOUNT_RE.search(t)
    if m:
        s = m.group(0).lower().replace("r$", "").strip()
        s = (
            s.replace(".", "").replace(",", ".")
            if ("," in s and "." in s)
            else s.replace(",", ".")
        )
        try:
            pending_payload["amount"] = float(s)
            return {
                "status": "ok",
                "transaction_payload": pending_payload,
                "message_draft": f"Fechado: valor ajustado para {pending_payload['amount']} {pending_payload['currency']}.",
            }
        except Exception:
            pass

    if any(
        k in t
        for k in ["sim", "confirmo", "confirma", "ok", "pode", "isso", "isso mesmo"]
    ):
        pending_payload["confidence"] = 1.0
        return {
            "status": "ok",
            "transaction_payload": pending_payload,
            "message_draft": "Perfeito, confirmado.",
        }

    return {
        "status": "need_confirmation",
        "transaction_payload": pending_payload,
        "message_draft": "Não entendi. Confirma (sim) ou diga a categoria/valor correto.",
    }
