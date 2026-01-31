from typing import Any, Dict, Optional

from life_os_agent.database.crud import get_or_create_user


def get_or_create_user_tool(
    whatsapp_number: str, name: Optional[str] = None
) -> Dict[str, Any]:
    return get_or_create_user(whatsapp_number, name)
