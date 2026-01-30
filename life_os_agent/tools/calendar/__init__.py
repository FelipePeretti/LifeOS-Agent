"""Tools do Calendar - Exporta todas as funções para uso pelo agente."""

from .calendar_tools import (
    check_availability,
    check_calendar_auth,
    create_calendar_event,
    delete_calendar_event,
    list_upcoming_events,
    list_user_calendars,
    search_calendar_events,
    update_calendar_event,
)
from .mcp_client import CalendarMCPClient, get_calendar_client

__all__ = [
    # Tools de alto nível
    "check_calendar_auth",
    "list_user_calendars",
    "list_upcoming_events",
    "create_calendar_event",
    "update_calendar_event",
    "delete_calendar_event",
    "search_calendar_events",
    "check_availability",
    # Cliente MCP
    "get_calendar_client",
    "CalendarMCPClient",
]
