from typing import Any, Dict

from life_os_agent.tools.finance.pending_store import (
    clear_pending_transaction,
    get_pending_transaction,
    has_pending_transaction,
    set_pending_transaction,
)
from life_os_agent.tools.finance.transaction_pipeline import (
    apply_confirmation,
    make_transaction_payload,
)


def process_finance_input(user_text: str, user_id: str = "default") -> Dict[str, Any]:
    if not user_text or len(user_text.strip()) < 2:
        return {"status": "ignored", "message": "Input too short coverage"}

    pending_check = has_pending_transaction()
    if pending_check.get("has_pending"):
        pending_payload = get_pending_transaction().get("pending")

        result = apply_confirmation(user_text, pending_payload)

        if result["status"] == "ok":
            clear_pending_transaction()
            result["action"] = "save_transaction"
            return result

        elif result["status"] == "cancelled":
            clear_pending_transaction()
            return result
        else:
            return result

    result = make_transaction_payload(user_text)

    if result["status"] == "ok":
        result["action"] = "save_transaction"
        return result

    elif result["status"] == "need_confirmation":
        set_pending_transaction(result["transaction_payload"])
        return result

    return result
