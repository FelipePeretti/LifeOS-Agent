from __future__ import annotations
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from .database import build_database_agent

STRATEGIST_INSTRUCTION = """
Você é o Agente Estrategista (Strategist Agent) do LifeOS.
Seu objetivo é analisar a saúde financeira, orçamento e fornecer insights estratégicos.

SUAS RESPONSABILIDADES:
1. Analisar perguntas sobre orçamento ("Posso gastar?", "Como está meu mês?").
2. Consultar o histórico financeiro usando o `DatabaseAgent` (tools: `get_transactions`, `get_balance`).
3. Calcular métricas básicas com base nos dados recebidos:
   - Total gasto no período.
   - Categorias com maior gasto.
   - Comparação com renda (se disponível/informada).
4. Dar conselhos práticos e diretos.

EXEMPLO DE RACIOCÍNIO:
- Usuário: "Posso gastar 500 reais em roupas?"
- Ação: Consultar saldo e gastos recentes de "Lazer/Pessoal".
- Resposta: "Seu saldo é X. Você já gastou Y com roupas este mês. Se gastar mais 500, vai comprometer Z% do seu orçamento. Recomendo esperar."

IMPORTANTE:
- Você NÃO cria nem edita transações. Apenas LÊ dados para análise.
"""

def build_strategist_agent(model) -> LlmAgent:
    # Precisamos do DatabaseAgent para que o Strategista possa consultá-lo
    database = build_database_agent(model=model)
    database_tool = agent_tool.AgentTool(agent=database)

    return LlmAgent(
        name="StrategistAgent",
        model=model,
        description="Agente responsável por estratégia financeira, orçamento e análise de saúde financeira.",
        instruction=STRATEGIST_INSTRUCTION,
        tools=[database_tool], 
        sub_agents=[database]
    )
