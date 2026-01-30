"""
Cliente HTTP para comunicação com o MCP Google Calendar.

Este módulo fornece funções para comunicar com o servidor MCP do Google Calendar
via HTTP, seguindo o protocolo JSON-RPC 2.0.
"""

import os
from typing import Any, Dict, List, Optional

import requests

# URL do MCP Google Calendar (configurável via variável de ambiente)
MCP_CALENDAR_URL = os.getenv("GOOGLE_CALENDAR_MCP_URL", "http://localhost:3001")


class CalendarMCPClient:
    """Cliente para comunicação com o MCP Google Calendar."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or MCP_CALENDAR_URL
        self._request_id = 0

    def _get_request_id(self) -> int:
        """Gera um ID único para cada requisição."""
        self._request_id += 1
        return self._request_id

    def _make_request(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Faz uma requisição JSON-RPC para o MCP.

        Args:
            method: Nome do método MCP (ex: 'tools/call')
            params: Parâmetros da requisição

        Returns:
            Resposta do MCP

        Raises:
            Exception: Se a requisição falhar
        """
        payload = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": method,
            "params": params or {},
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao conectar com o MCP Calendar: {str(e)}"}

    def health_check(self) -> Dict[str, Any]:
        """Verifica se o MCP está saudável."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    # ==================== API de Contas ====================

    def list_accounts(self) -> Dict[str, Any]:
        """Lista todas as contas autenticadas no MCP."""
        try:
            response = requests.get(f"{self.base_url}/api/accounts", timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e), "accounts": []}

    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma conta específica pelo ID."""
        result = self.list_accounts()
        accounts = result.get("accounts", [])
        for account in accounts:
            if account.get("id") == account_id:
                return account
        return None

    def account_exists(self, account_id: str) -> bool:
        """Verifica se uma conta existe."""
        return self.get_account(account_id) is not None

    def create_auth_url(self, account_id: str) -> Dict[str, Any]:
        """
        Gera URL de autenticação OAuth para uma nova conta.

        Args:
            account_id: ID da conta (usar whatsapp_number como ID)

        Returns:
            Dict com 'authUrl' e 'accountId' ou 'error'
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/accounts",
                json={"accountId": account_id},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def remove_account(self, account_id: str) -> Dict[str, Any]:
        """Remove uma conta autenticada."""
        try:
            response = requests.delete(
                f"{self.base_url}/api/accounts/{account_id}", timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # ==================== Tools do Calendar ====================

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chama uma tool do MCP Calendar.

        Args:
            tool_name: Nome da tool (ex: 'list-events', 'create-event')
            arguments: Argumentos da tool
            account_id: ID da conta a usar (opcional, usa default se não informado)

        Returns:
            Resultado da tool ou erro
        """
        if account_id:
            arguments["account"] = account_id

        result = self._make_request(
            "tools/call", {"name": tool_name, "arguments": arguments}
        )

        if "error" in result:
            return result

        # Extrai o resultado da resposta MCP
        return result.get("result", result)

    def list_calendars(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Lista todos os calendários disponíveis."""
        return self.call_tool("list-calendars", {}, account_id)

    def list_events(
        self,
        calendar_id: str = "primary",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 10,
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Lista eventos de um calendário.

        Args:
            calendar_id: ID do calendário (default: 'primary')
            start_date: Data inicial (ISO 8601)
            end_date: Data final (ISO 8601)
            max_results: Número máximo de resultados
            account_id: ID da conta
        """
        args = {
            "calendarId": calendar_id,
            "maxResults": max_results,
        }
        if start_date:
            args["timeMin"] = start_date
        if end_date:
            args["timeMax"] = end_date

        return self.call_tool("list-events", args, account_id)

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cria um novo evento no calendário.

        Args:
            summary: Título do evento
            start_time: Horário de início (ISO 8601)
            end_time: Horário de término (ISO 8601)
            description: Descrição do evento (opcional)
            location: Local do evento (opcional)
            calendar_id: ID do calendário (default: 'primary')
            account_id: ID da conta
        """
        args = {
            "calendarId": calendar_id,
            "summary": summary,
            "start": start_time,
            "end": end_time,
        }
        if description:
            args["description"] = description
        if location:
            args["location"] = location

        return self.call_tool("create-event", args, account_id)

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Atualiza um evento existente.

        Args:
            event_id: ID do evento a atualizar
            summary: Novo título (opcional)
            start_time: Novo horário de início (opcional)
            end_time: Novo horário de término (opcional)
            description: Nova descrição (opcional)
            location: Novo local (opcional)
            calendar_id: ID do calendário
            account_id: ID da conta
        """
        args = {
            "calendarId": calendar_id,
            "eventId": event_id,
        }
        if summary:
            args["summary"] = summary
        if start_time:
            args["start"] = start_time
        if end_time:
            args["end"] = end_time
        if description:
            args["description"] = description
        if location:
            args["location"] = location

        return self.call_tool("update-event", args, account_id)

    def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Remove um evento do calendário.

        Args:
            event_id: ID do evento a remover
            calendar_id: ID do calendário
            account_id: ID da conta
        """
        args = {
            "calendarId": calendar_id,
            "eventId": event_id,
        }
        return self.call_tool("delete-event", args, account_id)

    def search_events(
        self,
        query: str,
        calendar_id: str = "primary",
        max_results: int = 10,
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Busca eventos por texto.

        Args:
            query: Texto a buscar
            calendar_id: ID do calendário
            max_results: Número máximo de resultados
            account_id: ID da conta
        """
        args = {
            "calendarId": calendar_id,
            "query": query,
            "maxResults": max_results,
        }
        return self.call_tool("search-events", args, account_id)

    def get_freebusy(
        self,
        start_time: str,
        end_time: str,
        calendar_ids: Optional[List[str]] = None,
        account_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verifica disponibilidade em um período.

        Args:
            start_time: Início do período (ISO 8601)
            end_time: Fim do período (ISO 8601)
            calendar_ids: Lista de calendários a verificar
            account_id: ID da conta
        """
        args = {
            "timeMin": start_time,
            "timeMax": end_time,
        }
        if calendar_ids:
            args["calendars"] = calendar_ids

        return self.call_tool("get-freebusy", args, account_id)


# Instância global do cliente
_client: Optional[CalendarMCPClient] = None


def get_calendar_client() -> CalendarMCPClient:
    """Retorna a instância global do cliente MCP Calendar."""
    global _client
    if _client is None:
        _client = CalendarMCPClient()
    return _client
