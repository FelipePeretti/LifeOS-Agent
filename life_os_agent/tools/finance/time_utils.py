from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any

def now_ts_iso() -> Dict[str, Any]:
    """UTC timestamp ISO-8601, ex: 2026-01-20T21:42:33Z"""
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {"status": "success", "ts_iso": ts}
