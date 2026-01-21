from __future__ import annotations
from typing import Dict, Any
import json

def print_transaction_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    print("\n=== WOULD STORE IN DB ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("=== END ===\n")
    return {"status": "success", "printed": True}
