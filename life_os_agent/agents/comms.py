from __future__ import annotations

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Caminho para o MCP Server do Evolution API
MCP_SERVER_PATH = os.getenv(
    "MCP_EVOLUTION_PATH",
    "/app/mcp-evolution-api/dist/cli.js",
)

COMMS_INSTRUCTION = """
Você é o Agente de Comunicação do LifeOS.
Sua ÚNICA tarefa é enviar mensagens via WhatsApp.

## COMO USAR A TOOL sendTextMessage

Quando receber uma solicitação para enviar mensagem, use a tool sendTextMessage com:
- number: o número de telefone (apenas números, ex: "5564999999999")
- text: o texto da mensagem

## EXEMPLO

Se recebi: "Envie para 5564999999999: Olá, tudo bem?"

Você deve chamar:
sendTextMessage(number="5564999999999", text="Olá, tudo bem?")

## IMPORTANTE
- SEMPRE use a tool sendTextMessage para enviar
- O número deve conter apenas dígitos
- Não adicione @s.whatsapp.net, a tool faz isso automaticamente
"""


def build_comms_agent(model) -> LlmAgent:
    """
    Constrói o CommsAgent que usa o MCP do Evolution API para enviar mensagens.
    """
    evolution_mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="node",
                args=[MCP_SERVER_PATH],
                env={
                    "EVOLUTION_API_URL": os.getenv(
                        "EVOLUTION_API_URL", "http://evolution-api:8080"
                    ),
                    "EVOLUTION_API_KEY": os.getenv("EVOLUTION_API_KEY", ""),
                    "EVOLUTION_API_INSTANCE": os.getenv(
                        "EVOLUTION_API_INSTANCE", "LifeOs"
                    ),
                },
            ),
        ),
        tool_filter=["sendTextMessage"],
    )

    return LlmAgent(
        name="CommsAgent",
        model=model,
        description="Envia mensagens via WhatsApp usando MCP Evolution API",
        instruction=COMMS_INSTRUCTION,
        tools=[evolution_mcp_toolset],
    )
