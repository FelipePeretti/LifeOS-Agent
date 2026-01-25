from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo # Fallback for older python if needed (but 3.12 has it)

def now_ts_iso() -> Dict[str, Any]:
    """Timestamp ISO-8601 (America/Sao_Paulo), ex: 2026-01-20T18:42:33-03:00"""
    tz = ZoneInfo("America/Sao_Paulo")
    ts = datetime.now(tz).replace(microsecond=0).isoformat()
    return {"status": "success", "ts_iso": ts}
