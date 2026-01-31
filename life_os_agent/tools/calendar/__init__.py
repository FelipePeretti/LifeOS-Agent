"""
Tools para integração com Google Calendar via MCP.
"""

from .calendar_tools import (
    check_availability,
    check_calendar_auth,
    create_calendar_event,
    delete_calendar_event,
    get_event_details,
    list_upcoming_events,
    list_user_calendars,
    parse_event_datetime,
    search_calendar_events,
    update_calendar_event,
)
from .date_parser import (
    formatar_data_evento,
    is_dia_inteiro,
    parse_data_relativa,
    parse_duracao,
    parse_horario,
)
from .mcp_client import CalendarMCPClient, get_calendar_client

__all__ = [
    # MCP Client
    "CalendarMCPClient",
    "get_calendar_client",
    # Tools
    "check_calendar_auth",
    "parse_event_datetime",
    "list_user_calendars",
    "list_upcoming_events",
    "create_calendar_event",
    "update_calendar_event",
    "delete_calendar_event",
    "search_calendar_events",
    "check_availability",
    "get_event_details",
    # Date parser helpers
    "formatar_data_evento",
    "parse_data_relativa",
    "parse_horario",
    "parse_duracao",
    "is_dia_inteiro",
]
