from __future__ import annotations
import os
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

from .finance import build_finance_agent
from .comms import build_comms_agent
from .database import build_database_agent
from .perception import build_perception_agent
from .strategist import build_strategist_agent


from life_os_agent.tools.finance.transaction_pipeline import is_finance_related
from life_os_agent.tools.finance.finance_unified import process_finance_input

ORCHESTRATOR_INSTRUCTION = """
Você é o Orquestrador do LifeOS.
Seu objetivo é gerenciar a vida financeira e pessoal do usuário, coordenando agentes especializados.

SEU FLUXO DE TRABALHO:
1. Analise a entrada do usuário.
   - Se a entrada contiver referências a ÁUDIO ou precisar de transcrição, chame o `PerceptionAgent` PRIMEIRO.

2. Se for CHIT-CHAT (conversas, saudação):
   - Responda você mesmo.

3. Se for FINANCEIRO:
   - Chame a ferramenta `process_finance_input(text)` passando o texto original (ou transcrito).
   - Analise o JSON retornado por ela:
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

6. Se for PERGUNTA ESTRATÉGICA, DE ANÁLISE ou OPINIÃO ("Posso gastar?", "Como estou esse mês?"):
   - CHAME O `StrategistAgent`.
   - Passe a análise dele para o `CommsAgent` dar a resposta final.

7. FINALIZAÇÃO:
   - Sempre que fizer uma operação de banco, passe o resultado final para o `CommsAgent` dar o feedback ao usuário.

FERRAMENTAS:
- `FinanceAgent`: Especialista em entender textos financeiros e retornar dados estruturados.
- `StrategistAgent`: Especialista em analisar saúde financeira e dar conselhos.
- `DatabaseAgent`: O ÚNICO que pode ler/escrever no banco (inclusive updates/deletes).
- `CommsAgent`: O ÚNICO que fala bonitinho com o usuário.
- `PerceptionAgent`: Transcreve áudio e limpa inputs.
"""

DEV_MODE_INSTRUCTION = """
CONTEXTO DE USUÁRIO (DEV MODE):
- Atualmente estamos em desenvolvimento sem login real.
- Use SEMPRE o seguinte ID de usuário para TODAS as operações de banco: "5511999999999".
- Ao iniciar qualquer fluxo de escrita (como salvar transação), chame `get_or_create_user("5511999999999", "Dev User")` para garantir que ele existe.
"""


def build_orchestrator_agent(model) -> LlmAgent:
    # finance = build_finance_agent(model=model) -> Removido em favor de tool direta
    comms = build_comms_agent(model=model)
    database = build_database_agent(model=model)
    perception = build_perception_agent(model=model)
    strategist = build_strategist_agent(model=model)
    
    strategist_tool = agent_tool.AgentTool(agent=strategist)

    # Monta a instrução final dinamicamente
    final_instruction = ORCHESTRATOR_INSTRUCTION
    if os.getenv("LIFEOS_DEV_MODE", "false").lower() == "true":
        final_instruction = DEV_MODE_INSTRUCTION + "\n" + final_instruction

    comms_tool = agent_tool.AgentTool(agent=comms)
    database_tool = agent_tool.AgentTool(agent=database)
    perception_tool = agent_tool.AgentTool(agent=perception)

    return LlmAgent(
        name="Orchestrator",
        model=model,
        description="Agente orquestrador do LifeOS",
        instruction=final_instruction,
        tools=[
            is_finance_related,
            process_finance_input, # Tool direta
            database_tool,
            comms_tool,
            perception_tool,
            strategist_tool
        ],
        sub_agents=[comms, database, perception, strategist], # Finance removido
    )

