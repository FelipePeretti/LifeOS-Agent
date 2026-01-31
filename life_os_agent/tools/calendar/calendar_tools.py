"""
Tools do Calendar Agent para integração com o Google Calendar via MCP.

Estas tools são usadas pelo CalendarAgent para realizar operações
no Google Calendar do usuário.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from life_os_agent.database.crud import add_calendar_log

from .date_parser import formatar_data_evento, get_data_atual
from .mcp_client import get_calendar_client


def _format_account_id(whatsapp_number: str) -> str:
    """
    Formata o número do WhatsApp para ser usado como account_id no MCP.
    Remove caracteres especiais e mantém apenas números.
    """
    # Remove tudo que não for número
    clean_number = "".join(filter(str.isdigit, whatsapp_number))
    # Limita a 64 caracteres (limite do MCP)
    return clean_number[:64]


def _format_datetime(dt_str: str) -> str:
    """
    Formata string de data/hora para o padrão ISO 8601 sem timezone.
    O MCP espera formato: YYYY-MM-DDTHH:MM:SS
    """
    if not dt_str:
        return dt_str

    # Remove 'Z' se presente
    dt_str = dt_str.replace("Z", "")

    # Se já tem +/- timezone, remove
    if "+" in dt_str:
        dt_str = dt_str.split("+")[0]
    if dt_str.count("-") > 2:  # Tem timezone com -
        parts = dt_str.rsplit("-", 1)
        if len(parts[1]) <= 5:  # É timezone, não data
            dt_str = parts[0]

    return dt_str


def parse_event_datetime(texto: str) -> Dict[str, Any]:
    """
    Interpreta expressões de data/hora em linguagem natural e retorna
    as datas formatadas para criar um evento no calendário.
    
    USE ESTA TOOL SEMPRE antes de criar um evento quando o usuário usar
    expressões como "hoje", "amanhã", "sexta-feira", "próxima segunda", etc.
    
    Args:
        texto: Texto contendo a data/hora do evento em linguagem natural.
               Exemplos:
               - "hoje às 18h"
               - "amanhã às 14h30"
               - "sexta às 10h"
               - "próxima segunda às 9h"
               - "hoje o dia todo"
               - "amanhã dia inteiro"
    
    Returns:
        Dict com:
        - start: Data/hora de início formatada (ISO 8601 ou só data para all-day)
        - end: Data/hora de término formatada
        - all_day: True se é evento de dia inteiro
        - duracao_horas: Duração em horas (1.0 por padrão)
        - data_referencia: Data usada como referência (hoje)
    
    Exemplos de retorno:
        Para "hoje às 18h":
        {
            "start": "2026-01-31T18:00:00",
            "end": "2026-01-31T19:00:00",
            "all_day": false,
            "duracao_horas": 1.0
        }
        
        Para "amanhã o dia todo":
        {
            "start": "2026-02-01",
            "end": "2026-02-01",
            "all_day": true,
            "duracao_horas": 24.0
        }
    """
    agora = get_data_atual()
    resultado = formatar_data_evento(texto, agora)
    
    return {
        "start": resultado["start"],
        "end": resultado["end"],
        "all_day": resultado["all_day"],
        "duracao_horas": resultado["duracao_horas"],
        "data_referencia": agora.strftime("%Y-%m-%d"),
        "hora_referencia": agora.strftime("%H:%M:%S"),
    }


def check_calendar_auth(whatsapp_number: str) -> Dict[str, Any]:
    """
    Verifica se o usuário tem autenticação ativa no Google Calendar.

    Args:
        whatsapp_number: Número do WhatsApp do usuário

    Returns:
        Dict com:
        - is_authenticated: True se o usuário está autenticado
        - account_id: ID da conta no MCP
        - email: Email da conta Google (se autenticado)
        - calendars: Lista de calendários (se autenticado)
        - auth_url: URL para autenticação (se não autenticado)
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica se a conta existe
    account = client.get_account(account_id)

    if account and account.get("status") == "active":
        return {
            "is_authenticated": True,
            "account_id": account_id,
            "email": account.get("email", ""),
            "calendars": account.get("calendars", []),
        }

    # Conta não existe ou não está ativa - gera URL de autenticação
    auth_result = client.create_auth_url(account_id)

    if "error" in auth_result:
        return {
            "is_authenticated": False,
            "account_id": account_id,
            "error": auth_result["error"],
        }

    return {
        "is_authenticated": False,
        "account_id": account_id,
        "auth_url": auth_result.get("authUrl", ""),
        "message": "Usuário precisa autenticar o Google Calendar",
    }


def list_user_calendars(whatsapp_number: str) -> Dict[str, Any]:
    """
    Lista todos os calendários do usuário.

    Args:
        whatsapp_number: Número do WhatsApp do usuário

    Returns:
        Dict com lista de calendários ou erro
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Primeiro verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    # Calendários já vêm com a conta
    calendars = client.get_calendars_for_account(account_id)

    return {
        "status": "ok",
        "calendars": calendars,
    }


def list_upcoming_events(
    whatsapp_number: str,
    days: int = 7,
    max_results: int = 10,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """
    Lista os próximos eventos do usuário.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        days: Número de dias para frente (default: 7)
        max_results: Número máximo de eventos (default: 10)
        calendar_id: ID do calendário (default: 'primary')

    Returns:
        Dict com lista de eventos ou erro/URL de autenticação
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    # Calcula período (formato sem timezone)
    now = datetime.now()
    time_min = now.strftime("%Y-%m-%dT%H:%M:%S")
    time_max = (now + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")

    result = client.list_events(
        account_id=account_id,
        calendar_id=calendar_id,
        max_results=max_results,
        time_min=time_min,
        time_max=time_max,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    # Processa eventos para formato amigável
    events = result.get("events", [])
    formatted_events = []
    for event in events:
        start = event.get("start", {})
        end = event.get("end", {})
        formatted_events.append(
            {
                "id": event.get("id"),
                "title": event.get("summary", "Sem título"),
                "start": start.get("dateTime", start.get("date", "")),
                "end": end.get("dateTime", end.get("date", "")),
                "location": event.get("location", ""),
                "description": event.get("description", ""),
            }
        )

    return {
        "status": "ok",
        "events": formatted_events,
        "period": {"start": time_min, "end": time_max},
        "total": len(formatted_events),
    }


def create_calendar_event(
    whatsapp_number: str,
    title: str,
    start_datetime: str,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
    all_day: bool = False,
) -> Dict[str, Any]:
    """
    Cria um novo evento no calendário do usuário.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        title: Título do evento
        start_datetime: Data/hora de início. Pode ser:
            - ISO 8601 completo (2026-01-31T18:00:00)
            - Apenas data para eventos de dia inteiro (2026-01-31)
            - Expressão relativa (hoje, amanhã, sexta) - será parseada automaticamente
        end_datetime: Data/hora de término (opcional, default: 1 hora após início)
            Para eventos de dia inteiro, pode ser omitido (usa mesma data do início)
        description: Descrição do evento (opcional)
        location: Local do evento (opcional)
        calendar_id: ID do calendário (default: 'primary')
        all_day: Se True, cria evento de dia inteiro (default: False)

    Returns:
        Dict com dados do evento criado ou erro/URL de autenticação
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    # Tenta usar o parser de datas relativas se não for formato ISO completo
    parsed_data = None
    if not _is_iso_datetime(start_datetime):
        # Combina título + start_datetime para contexto completo
        texto_para_parser = f"{title} {start_datetime}"
        parsed_data = formatar_data_evento(texto_para_parser, get_data_atual())
        
        # Se o parser retornou all_day, usa essa informação
        if parsed_data.get("all_day"):
            all_day = True
    
    # Define as datas de início e fim
    if all_day:
        # Evento de dia inteiro - usa apenas a data (YYYY-MM-DD)
        if parsed_data and parsed_data.get("start"):
            start_formatted = parsed_data["start"]
            end_formatted = parsed_data.get("end", start_formatted)
        else:
            # Extrai apenas a data do start_datetime
            start_formatted = _extract_date(start_datetime)
            end_formatted = _extract_date(end_datetime) if end_datetime else start_formatted
    else:
        # Evento com horário
        if parsed_data and parsed_data.get("start"):
            start_formatted = parsed_data["start"]
            end_formatted = parsed_data.get("end", start_formatted)
        else:
            start_formatted = _format_datetime(start_datetime)
            
            # Se end_datetime não foi informado, usa 1 hora após o início
            if not end_datetime:
                try:
                    start_dt = datetime.fromisoformat(start_formatted)
                    end_dt = start_dt + timedelta(hours=1)
                    end_formatted = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    end_formatted = start_formatted
            else:
                end_formatted = _format_datetime(end_datetime)

    result = client.create_event(
        account_id=account_id,
        summary=title,
        start=start_formatted,
        end=end_formatted,
        calendar_id=calendar_id,
        description=description,
        location=location,
        all_day=all_day,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    event = result.get("event", result)

    # Log no banco de dados local
    try:
        add_calendar_log(
            user_id=whatsapp_number,
            google_event_id=event.get("id"),
            action="created",
            event_summary=event.get("summary"),
        )
    except Exception as e:
        print(f"[CalendarTool] Erro ao salvar log: {e}")

    return {
        "status": "ok",
        "message": f"Evento '{title}' criado com sucesso!",
        "event": {
            "id": event.get("id"),
            "title": event.get("summary"),
            "start": event.get("start", {}).get("dateTime") or event.get("start", {}).get("date", ""),
            "end": event.get("end", {}).get("dateTime") or event.get("end", {}).get("date", ""),
            "link": event.get("htmlLink", ""),
            "all_day": all_day,
        },
    }


def _is_iso_datetime(dt_str: str) -> bool:
    """Verifica se a string está em formato ISO 8601 completo."""
    if not dt_str:
        return False
    # Verifica se tem o formato YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS
    import re
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?', dt_str))


def _extract_date(dt_str: str) -> str:
    """Extrai apenas a data (YYYY-MM-DD) de uma string de data/hora."""
    if not dt_str:
        return datetime.now().strftime("%Y-%m-%d")
    # Se já é só data
    if len(dt_str) == 10:
        return dt_str
    # Se tem T, pega só a parte da data
    if "T" in dt_str:
        return dt_str.split("T")[0]
    return dt_str[:10]


def update_calendar_event(
    whatsapp_number: str,
    event_id: str,
    title: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """
    Atualiza um evento existente no calendário.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        event_id: ID do evento a atualizar
        title: Novo título (opcional)
        start_datetime: Nova data/hora de início (opcional)
        end_datetime: Nova data/hora de término (opcional)
        description: Nova descrição (opcional)
        location: Novo local (opcional)
        calendar_id: ID do calendário

    Returns:
        Dict com dados do evento atualizado ou erro
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    # Prepara argumentos para o MCP
    args = {
        "account": account_id,
        "calendarId": calendar_id,
        "eventId": event_id,
    }

    if title:
        args["summary"] = title
    if start_datetime:
        args["start"] = _format_datetime(start_datetime)
    if end_datetime:
        args["end"] = _format_datetime(end_datetime)
    if description:
        args["description"] = description
    if location:
        args["location"] = location

    result = client.call_tool("update-event", args)

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    event = result.get("event", result)

    # Log no banco de dados local
    try:
        add_calendar_log(
            user_id=whatsapp_number,
            google_event_id=event.get("id"),
            action="updated",
            event_summary=event.get("summary"),
        )
    except Exception as e:
        print(f"[CalendarTool] Erro ao salvar log: {e}")

    return {
        "status": "ok",
        "message": "Evento atualizado com sucesso!",
        "event": event,
    }


def delete_calendar_event(
    whatsapp_number: str,
    event_id: str,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """
    Remove um evento do calendário.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        event_id: ID do evento a remover
        calendar_id: ID do calendário

    Returns:
        Dict com confirmação ou erro
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    result = client.delete_event(
        account_id=account_id,
        event_id=event_id,
        calendar_id=calendar_id,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    # Log no banco de dados local
    try:
        add_calendar_log(
            user_id=whatsapp_number,
            google_event_id=event_id,
            action="deleted",
            event_summary=None,
        )
    except Exception as e:
        print(f"[CalendarTool] Erro ao salvar log: {e}")

    return {
        "status": "ok",
        "message": "Evento removido com sucesso!",
    }


def search_calendar_events(
    whatsapp_number: str,
    query: str,
    max_results: int = 10,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """
    Busca eventos por texto.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        query: Texto a buscar nos eventos
        max_results: Número máximo de resultados
        calendar_id: ID do calendário

    Returns:
        Dict com lista de eventos encontrados ou erro
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    result = client.call_tool(
        "search-events",
        {
            "account": account_id,
            "calendarId": calendar_id,
            "query": query,
            "maxResults": max_results,
        },
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    events = result.get("events", [])
    formatted_events = []
    for event in events:
        start = event.get("start", {})
        formatted_events.append(
            {
                "id": event.get("id"),
                "title": event.get("summary", "Sem título"),
                "start": start.get("dateTime", start.get("date", "")),
            }
        )

    return {
        "status": "ok",
        "query": query,
        "events": formatted_events,
        "total": len(formatted_events),
    }


def check_availability(
    whatsapp_number: str,
    start_datetime: str,
    end_datetime: str,
    calendar_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Verifica disponibilidade em um período.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        start_datetime: Início do período (ISO 8601)
        end_datetime: Fim do período (ISO 8601)
        calendar_ids: Lista de calendários a verificar (opcional)

    Returns:
        Dict com informações de disponibilidade ou erro
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    # Prepara lista de calendários
    if not calendar_ids:
        calendar_ids = ["primary"]

    calendars = [{"id": cal_id} for cal_id in calendar_ids]

    result = client.call_tool(
        "get-freebusy",
        {
            "account": account_id,
            "calendars": calendars,
            "timeMin": _format_datetime(start_datetime),
            "timeMax": _format_datetime(end_datetime),
        },
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    # Processa resultado
    calendars_busy = result.get("calendars", {})
    is_available = True
    busy_periods = []

    for cal_id, cal_data in calendars_busy.items():
        for busy in cal_data.get("busy", []):
            is_available = False
            busy_periods.append(
                {
                    "calendar": cal_id,
                    "start": busy.get("start"),
                    "end": busy.get("end"),
                }
            )

    return {
        "status": "ok",
        "is_available": is_available,
        "period": {
            "start": start_datetime,
            "end": end_datetime,
        },
        "busy_periods": busy_periods,
    }


def get_event_details(
    whatsapp_number: str,
    event_id: str,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """
    Obtém detalhes de um evento específico.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        event_id: ID do evento
        calendar_id: ID do calendário

    Returns:
        Dict com detalhes do evento ou erro
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    result = client.call_tool(
        "get-event",
        {
            "account": account_id,
            "calendarId": calendar_id,
            "eventId": event_id,
        },
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    event = result.get("event", result)
    start = event.get("start", {})
    end = event.get("end", {})

    return {
        "status": "ok",
        "event": {
            "id": event.get("id"),
            "title": event.get("summary", "Sem título"),
            "start": start.get("dateTime", start.get("date", "")),
            "end": end.get("dateTime", end.get("date", "")),
            "location": event.get("location", ""),
            "description": event.get("description", ""),
            "attendees": event.get("attendees", []),
            "link": event.get("htmlLink", ""),
        },
    }
