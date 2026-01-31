"""
Cliente para comunicação com o MCP Google Calendar.

Este módulo fornece funções para comunicar com o servidor MCP do Google Calendar
usando requisições HTTP diretas com o protocolo MCP (JSON-RPC sobre HTTP).
"""

import json
import os
from typing import Any, Dict, List, Optional

import httpx

# URL do MCP Google Calendar (configurável via variável de ambiente)
MCP_CALENDAR_URL = os.getenv("GOOGLE_CALENDAR_MCP_URL", "http://localhost:3001")


class CalendarMCPClient:
    """Cliente para comunicação com o MCP Google Calendar."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or MCP_CALENDAR_URL
        self._client = httpx.Client(timeout=30)
        self._request_id = 0

    def _get_request_id(self) -> int:
        """Gera um ID único para cada requisição."""
        self._request_id += 1
        return self._request_id

    def _make_rest_request(
        self, method: str, endpoint: str, json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Faz uma requisição REST para APIs de gerenciamento."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = self._client.get(url)
            elif method == "POST":
                response = self._client.post(url, json=json_data or {})
            elif method == "DELETE":
                response = self._client.delete(url)
            else:
                return {"error": f"Método não suportado: {method}"}

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": f"Erro ao conectar com o MCP Calendar: {str(e)}"}

    def _make_mcp_request(
        self, mcp_method: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Faz uma requisição MCP (JSON-RPC sobre HTTP com SSE).

        Args:
            mcp_method: Método MCP (ex: 'tools/call', 'tools/list')
            params: Parâmetros do método

        Returns:
            Resultado da requisição ou erro
        """
        url = f"{self.base_url}/mcp"
        payload = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": mcp_method,
            "params": params or {},
        }

        try:
            response = self._client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
            )
            response.raise_for_status()

            # Resposta pode ser SSE, precisamos parsear
            text = response.text
            if text.startswith("event:"):
                # Parse SSE response
                for line in text.split("\n"):
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        return json.loads(data)
            else:
                return response.json()

        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": f"Erro na requisição MCP: {str(e)}"}

    def health_check(self) -> Dict[str, Any]:
        """Verifica se o MCP está saudável."""
        return self._make_rest_request("GET", "/health")

    # ==================== API de Contas (REST) ====================

    def list_accounts(self) -> Dict[str, Any]:
        """Lista todas as contas autenticadas no MCP."""
        return self._make_rest_request("GET", "/api/accounts")

    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma conta específica pelo ID."""
        result = self.list_accounts()
        accounts = result.get("accounts", [])
        for account in accounts:
            if account.get("id") == account_id:
                return account
        return None

    def account_exists(self, account_id: str) -> bool:
        """Verifica se uma conta existe e está ativa."""
        account = self.get_account(account_id)
        return account is not None and account.get("status") == "active"

    def create_auth_url(self, account_id: str) -> Dict[str, Any]:
        """
        Gera URL de autenticação OAuth para uma nova conta.

        Args:
            account_id: ID da conta (usar whatsapp_number como ID)

        Returns:
            Dict com 'authUrl' e 'accountId' ou 'error'
        """
        return self._make_rest_request(
            "POST", "/api/accounts", {"accountId": account_id}
        )

    def remove_account(self, account_id: str) -> Dict[str, Any]:
        """Remove uma conta autenticada."""
        return self._make_rest_request("DELETE", f"/api/accounts/{account_id}")

    def reauth_account(self, account_id: str) -> Dict[str, Any]:
        """Gera nova URL de autenticação para uma conta existente."""
        return self._make_rest_request("POST", f"/api/accounts/{account_id}/reauth")

    # ==================== Tools MCP ====================

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chama uma tool do MCP Calendar.

        Args:
            tool_name: Nome da tool (ex: 'list-events', 'create-event')
            arguments: Argumentos da tool

        Returns:
            Resultado da tool ou erro
        """
        result = self._make_mcp_request(
            "tools/call",
            {"name": tool_name, "arguments": arguments},
        )

        if "error" in result:
            return result

        # Extrair resultado da resposta MCP
        if "result" in result:
            mcp_result = result["result"]
            # O resultado pode ter 'content' com a resposta
            if "content" in mcp_result:
                content = mcp_result["content"]
                # Content pode ser uma lista de partes
                if isinstance(content, list) and content:
                    # Pegar o texto da primeira parte
                    text_content = content[0].get("text", "")
                    try:
                        return json.loads(text_content)
                    except json.JSONDecodeError:
                        return {"content": text_content}
                return {"content": content}
            return mcp_result

        return result

    def list_tools(self) -> Dict[str, Any]:
        """Lista todas as tools disponíveis no MCP."""
        return self._make_mcp_request("tools/list")

    # ==================== Métodos de Conveniência ====================

    def list_events(
        self,
        account_id: str,
        calendar_id: str = "primary",
        max_results: int = 10,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Lista eventos de um calendário.

        Args:
            account_id: ID da conta no MCP
            calendar_id: ID do calendário (default: 'primary')
            max_results: Número máximo de resultados
            time_min: Data/hora mínima (ISO 8601)
            time_max: Data/hora máxima (ISO 8601)
        """
        args = {
            "account": account_id,
            "calendarId": calendar_id,
            "maxResults": max_results,
        }
        if time_min:
            args["timeMin"] = time_min
        if time_max:
            args["timeMax"] = time_max

        return self.call_tool("list-events", args)

    def create_event(
        self,
        account_id: str,
        summary: str,
        start: str,
        end: str,
        calendar_id: str = "primary",
        description: Optional[str] = None,
        location: Optional[str] = None,
        all_day: bool = False,
    ) -> Dict[str, Any]:
        """
        Cria um novo evento no calendário.

        Args:
            account_id: ID da conta no MCP
            summary: Título do evento
            start: Data/hora de início (ISO 8601) ou apenas data para all-day (YYYY-MM-DD)
            end: Data/hora de término (ISO 8601) ou apenas data para all-day (YYYY-MM-DD)
            calendar_id: ID do calendário (default: 'primary')
            description: Descrição do evento
            location: Local do evento
            all_day: Se True, cria evento de dia inteiro (start/end devem ser só data)
        
        Notas:
            - Para eventos de dia inteiro, use start e end no formato YYYY-MM-DD
            - O MCP detecta automaticamente eventos all-day quando start não contém 'T'
        """
        args = {
            "account": account_id,
            "calendarId": calendar_id,
            "summary": summary,
            "start": start,
            "end": end,
        }
        if description:
            args["description"] = description
        if location:
            args["location"] = location

        return self.call_tool("create-event", args)

    def delete_event(
        self,
        account_id: str,
        event_id: str,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """Remove um evento do calendário."""
        return self.call_tool(
            "delete-event",
            {
                "account": account_id,
                "calendarId": calendar_id,
                "eventId": event_id,
            },
        )

    def get_current_time(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtém a data/hora atual do servidor."""
        args = {}
        if account_id:
            args["account"] = account_id
        return self.call_tool("get-current-time", args)

    def get_calendars_for_account(self, account_id: str) -> List[Dict[str, Any]]:
        """Retorna a lista de calendários de uma conta."""
        account = self.get_account(account_id)
        if account:
            return account.get("calendars", [])
        return []


# Instância global do cliente
_client: Optional[CalendarMCPClient] = None


def get_calendar_client() -> CalendarMCPClient:
    """Retorna a instância global do cliente MCP Calendar."""
    global _client
    if _client is None:
        _client = CalendarMCPClient()
    return _client
