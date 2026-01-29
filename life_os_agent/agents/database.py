from __future__ import annotations

from google.adk.agents import LlmAgent

from life_os_agent.database.crud import (
    add_calendar_log,
    add_transaction,
    check_user_exists,
    delete_transaction,
    get_balance,
    get_budget_status,
    get_calendar_logs,
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

### Finanças
- `add_transaction`: Adiciona receita ou despesa.
- `get_transactions`: Busca histórico de transações.
- `get_balance`: Busca o saldo atual.
- `get_expenses_by_category`: Busca gastos agrupados por categoria.

### Agenda
- `add_calendar_log`: Adiciona evento.
- `get_calendar_logs`: Busca eventos.

## COMO AGIR
1. Receba a instrução do Orchestrator.
2. Escolha a tool mais adequada para a solicitação.
   - Ex: "Quanto gastei?" -> Use `get_expenses_by_category` ou `get_transactions`.
   - Ex: "Registre 10 reais" -> Use `add_transaction`.
3. Execute a tool.
4. Retorne o resultado (JSON/Dict) para o Orchestrator.

## REGRAS
- Não invente dados. Se a tool retornar vazio, informe isso.
- Retorne sempre o resultado da execução da tool.
"""


def build_database_agent(model) -> LlmAgent:
    return LlmAgent(
        name="DatabaseAgent",
        model=model,
        description="Executor de operações de banco de dados. Verifica/cria usuários e gerencia transações.",
        instruction=DATABASE_INSTRUCTION,
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
            get_calendar_logs,
            # Inicialização
            init_database,
        ],
    )
