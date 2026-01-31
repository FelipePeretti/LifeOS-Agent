from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


def now_ts_iso() -> Dict[str, Any]:
    tz = ZoneInfo("America/Sao_Paulo")
    ts = datetime.now(tz).replace(microsecond=0).isoformat()
    return {"status": "success", "ts_iso": ts}
