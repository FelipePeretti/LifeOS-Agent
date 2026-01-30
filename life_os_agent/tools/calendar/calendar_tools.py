"""
Tools do Calendar Agent para integração com o Google Calendar via MCP.

Estas tools são usadas pelo CalendarAgent para realizar operações
no Google Calendar do usuário.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

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

    # Busca calendários via MCP
    result = client.list_calendars(account_id)

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    return {
        "status": "ok",
        "calendars": auth_check.get("calendars", []),
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

    # Calcula período
    now = datetime.now()
    start_date = now.isoformat() + "Z"
    end_date = (now + timedelta(days=days)).isoformat() + "Z"

    result = client.list_events(
        calendar_id=calendar_id,
        start_date=start_date,
        end_date=end_date,
        max_results=max_results,
        account_id=account_id,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    return {
        "status": "ok",
        "events": result.get("content", result),
        "period": {"start": start_date, "end": end_date},
    }


def create_calendar_event(
    whatsapp_number: str,
    title: str,
    start_datetime: str,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
) -> Dict[str, Any]:
    """
    Cria um novo evento no calendário do usuário.

    Args:
        whatsapp_number: Número do WhatsApp do usuário
        title: Título do evento
        start_datetime: Data/hora de início (ISO 8601 ou natural como "amanhã às 14h")
        end_datetime: Data/hora de término (opcional, default: 1 hora após início)
        description: Descrição do evento (opcional)
        location: Local do evento (opcional)
        calendar_id: ID do calendário (default: 'primary')

    Returns:
        Dict com dados do evento criado ou erro/URL de autenticação
    """
    client = get_calendar_client()
    account_id = _format_account_id(whatsapp_number)

    # Verifica autenticação
    auth_check = check_calendar_auth(whatsapp_number)
    if not auth_check.get("is_authenticated"):
        return auth_check

    # Se end_datetime não foi informado, usa 1 hora após o início
    if not end_datetime:
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace("Z", ""))
            end_dt = start_dt + timedelta(hours=1)
            end_datetime = end_dt.isoformat()
        except ValueError:
            end_datetime = start_datetime  # MCP vai tratar

    result = client.create_event(
        summary=title,
        start_time=start_datetime,
        end_time=end_datetime,
        description=description,
        location=location,
        calendar_id=calendar_id,
        account_id=account_id,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    return {
        "status": "ok",
        "message": f"Evento '{title}' criado com sucesso!",
        "event": result.get("content", result),
    }


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

    result = client.update_event(
        event_id=event_id,
        summary=title,
        start_time=start_datetime,
        end_time=end_datetime,
        description=description,
        location=location,
        calendar_id=calendar_id,
        account_id=account_id,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    return {
        "status": "ok",
        "message": "Evento atualizado com sucesso!",
        "event": result.get("content", result),
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
        event_id=event_id,
        calendar_id=calendar_id,
        account_id=account_id,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

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

    result = client.search_events(
        query=query,
        calendar_id=calendar_id,
        max_results=max_results,
        account_id=account_id,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    return {
        "status": "ok",
        "query": query,
        "events": result.get("content", result),
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

    result = client.get_freebusy(
        start_time=start_datetime,
        end_time=end_datetime,
        calendar_ids=calendar_ids,
        account_id=account_id,
    )

    if "error" in result:
        return {"status": "error", "error": result["error"]}

    return {
        "status": "ok",
        "freebusy": result.get("content", result),
    }
