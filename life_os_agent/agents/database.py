from __future__ import annotations

from google.adk.agents import LlmAgent

from life_os_agent.database.crud import (
    add_calendar_log,
    add_transaction,
    check_user_exists,
    delete_transaction,
    get_balance,
    get_budget_status,
    get_calendar_events,
    get_event_by_google_id,
    get_expenses_by_category,
    get_transactions,
    set_budget_goal,
    update_transaction,
    update_user_last_interaction,
)
from life_os_agent.database.setup import init_database
from life_os_agent.tools.database.user_tools import get_or_create_user_tool

DATABASE_INSTRUCTION = """
Você é o DatabaseAgent do LifeOS.
Sua responsabilidade é executar operações no banco de dados SQLite.

## TOOLS DISPONÍVEIS

### Usuários
- `get_or_create_user_tool`: Verifica/cria usuário.

### Transações
- `add_transaction`: Adiciona receita ou despesa.
- `get_transactions`: Busca histórico de transações.
- `get_balance`: Busca o saldo atual.
- `get_expenses_by_category`: Busca gastos agrupados por categoria.

### Metas de Orçamento
- `set_budget_goal(user_id, category, monthly_limit)`: Define meta mensal para categoria.
- `get_budget_status(user_id, month?)`: **IMPORTANTE!** Retorna status de TODAS as metas com:
  - category: nome da categoria
  - monthly_limit: meta definida
  - spent: **SOMA ACUMULADA** de todas transações do mês
  - remaining: quanto ainda pode gastar
  - percentage: percentual já gasto

### Agenda
- `add_calendar_log(user_id, google_event_id, action, event_summary)`: Registra ação de calendário.
- `get_calendar_events(user_id, limit, action)`: Busca logs de eventos.
- `get_event_by_google_id(user_id, google_event_id)`: Busca evento por ID do Google.

## COMO AGIR
1. Receba a instrução do Orchestrator/StrategistAgent.
2. Escolha a tool mais adequada.
3. Execute e retorne o resultado.

## REGRAS
- Não invente dados.
- AO VERIFICAR/CRIAR USUÁRIO: Retorne `is_new_user: True/False`.
- AO CONSULTAR METAS: Use `get_budget_status` que já retorna a soma acumulada.
"""


def _log_database_agent(callback_context):
    print("[AGENT] 🗄️ DatabaseAgent CHAMADO", flush=True)


def build_database_agent(model) -> LlmAgent:
    return LlmAgent(
        name="DatabaseAgent",
        model=model,
        description="Executor de operações de banco de dados. Verifica/cria usuários e gerencia transações.",
        instruction=DATABASE_INSTRUCTION,
        before_agent_callback=_log_database_agent,
        tools=[
            # Tools de usuário (da pasta tools/)
            get_or_create_user_tool,
            # Tools de usuário (do crud)
            check_user_exists,
            update_user_last_interaction,
            # Tools de transações
            add_transaction,
            get_transactions,
            update_transaction,
            delete_transaction,
            get_balance,
            get_expenses_by_category,
            # Tools de metas
            set_budget_goal,
            get_budget_status,
            # Tools de calendário
            add_calendar_log,
            get_calendar_events,
            get_event_by_google_id,
            # Inicialização
            init_database,
        ],
    )
