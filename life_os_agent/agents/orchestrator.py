from __future__ import annotations
import os
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

from .finance import build_finance_agent
from .comms import build_comms_agent
from .database import build_database_agent

from life_os_agent.tools.finance.finance_unified import process_finance_input
from life_os_agent.tools.finance.transaction_pipeline import is_finance_related

ORCHESTRATOR_INSTRUCTION = """
Você é o Orquestrador do LifeOS.
Seu objetivo é gerenciar a vida financeira e pessoal do usuário, coordenando agentes especializados.

SEU FLUXO DE TRABALHO:
1. Analise a entrada do usuário.

2. Se for CHIT-CHAT (conversas, saudação):
   - Responda você mesmo.

3. Se for FINANCEIRO:
   - Chame `process_finance_input(text)`.
   - Analise o retorno:
     - Se `action == "save_transaction"`: CHAME O `DatabaseAgent`. 
       - PRIMEIRO garanta que o usuário existe (`get_or_create_user` se necessário).
       - DEPOIS use `add_transaction` com o ID correto.
     - Se `status == "ignored"`: Trate como chit-chat normal.
     - Se `status == "need_confirmation"`: Passe o JSON para o `CommsAgent`.

4. Se for CORREÇÃO ou CANCELAMENTO ("Mude o valor para 20", "Delete a última"):
   - Primeiro: CHAME `get_transactions(limit=5)` para achar o ID da última transação.
   - Analise qual é a transação correta.
   - CHAME `update_transaction(id, ...)` ou `delete_transaction(id)`.
   - Confirme a ação com o usuário.

5. Se for PEDIDO DE DADOS (extrato, saldo, metas, ultimas compras):
   - CHAME O `DatabaseAgent` (use `get_transactions`, `get_balance`, etc).
   - Passe o JSON retornado para o `CommsAgent` formatar.

6. FINALIZAÇÃO:
   - Sempre que fizer uma operação de banco, passe o resultado final para o `CommsAgent` dar o feedback ao usuário.

FERRAMENTAS:
- `process_finance_input`: Analisa intenção e estrutura dados, mas NÃO salva.
- `DatabaseAgent`: O ÚNICO que pode ler/escrever no banco (inclusive updates/deletes).
- `CommsAgent`: O ÚNICO que fala bonitinho com o usuário.
"""

DEV_MODE_INSTRUCTION = """
CONTEXTO DE USUÁRIO (DEV MODE):
- Atualmente estamos em desenvolvimento sem login real.
- Use SEMPRE o seguinte ID de usuário para TODAS as operações de banco: "5511999999999".
- Ao iniciar qualquer fluxo de escrita (como salvar transação), chame `get_or_create_user("5511999999999", "Dev User")` para garantir que ele existe.
"""


def build_orchestrator_agent(model) -> LlmAgent:
    finance = build_finance_agent(model=model)
    comms = build_comms_agent(model=model)
    database = build_database_agent(model=model)

    # Monta a instrução final dinamicamente
    final_instruction = ORCHESTRATOR_INSTRUCTION
    if os.getenv("LIFEOS_DEV_MODE", "false").lower() == "true":
        final_instruction = DEV_MODE_INSTRUCTION + "\n" + final_instruction

    comms_tool = agent_tool.AgentTool(agent=comms)
    database_tool = agent_tool.AgentTool(agent=database)

    return LlmAgent(
        name="Orchestrator",
        model=model,
        description="Agente orquestrador do LifeOS",
        instruction=final_instruction,
        tools=[
            is_finance_related,
            process_finance_input,
            database_tool,
            comms_tool
        ],
        sub_agents=[comms, database],
    )

