from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

from .database import build_database_agent

STRATEGIST_INSTRUCTION = """
Você é o Agente Estrategista (Strategist Agent) do LifeOS.
Seu objetivo é analisar metas de orçamento e fornecer insights estratégicos.

## SUAS RESPONSABILIDADES

1. Verificar metas de orçamento após transações
2. Responder consultas tipo "Posso gastar?", "Quanto gastei?", "Minha meta"
3. Criar e gerenciar metas de orçamento

## TOOL PRINCIPAL: get_budget_status

Esta é a tool mais importante! Ela retorna para cada categoria com meta:
- category: nome da categoria
- monthly_limit: meta mensal definida
- spent: **SOMA DE TODAS as transações do mês** (não apenas a última!)
- remaining: quanto ainda pode gastar (monthly_limit - spent)
- percentage: percentual já gasto

### Como usar:
- Ao verificar meta após transação, chame: `get_budget_status(user_id)`
- O resultado já vem com a SOMA CORRETA de todas as transações do mês

## FORMATO DE RESPOSTA PARA METAS

Quando consultado sobre uma meta, retorne:
```
{
  "category": "Mercado",
  "monthly_limit": 500,
  "spent": 472,  <- SOMA de todas transações do mês (72 + 400 = 472)
  "remaining": 28,  <- Quanto pode gastar ainda
  "percentage": 94.4
}
```

## OUTRAS TOOLS DISPONÍVEIS (via DatabaseAgent)

- `get_expenses_by_category(user_id, month)`: Gastos por categoria
- `get_transactions(user_id)`: Histórico de transações
- `get_balance(user_id)`: Saldo geral
- `set_budget_goal(user_id, category, monthly_limit)`: Criar/atualizar meta

## REGRAS

- Metas são MENSAIS (sempre considere o mês atual)
- O valor "spent" é a SOMA ACUMULADA, não a última transação
- Retorne SEMPRE o "remaining" corretamente calculado
- Se a meta foi ultrapassada, avise o usuário
"""


def _log_strategist_agent(callback_context):
    print("[AGENT] 📊 StrategistAgent CHAMADO", flush=True)


def build_strategist_agent(model) -> LlmAgent:
    # Precisamos do DatabaseAgent para que o Strategista possa consultá-lo
    database = build_database_agent(model=model)
    database_tool = agent_tool.AgentTool(agent=database)

    return LlmAgent(
        name="StrategistAgent",
        model=model,
        description="Agente responsável por verificar metas de orçamento e calcular quanto ainda pode gastar.",
        instruction=STRATEGIST_INSTRUCTION,
        before_agent_callback=_log_strategist_agent,
        tools=[database_tool],
        sub_agents=[database],
    )
