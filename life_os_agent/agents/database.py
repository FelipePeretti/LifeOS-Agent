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
    get_or_create_user,
    get_transactions,
    set_budget_goal,
    update_transaction,
    update_user_last_interaction,
)
from life_os_agent.database.setup import init_database

DATABASE_INSTRUCTION = """
Você é o Database Agent do LifeOS.
Sua única responsabilidade é executar operações de leitura e escrita no banco de dados SQLite.

## TOOLS DISPONÍVEIS

### Usuários
- `check_user_exists(whatsapp_number)`: Verifica se usuário existe. Retorna {exists, user_data, is_first_interaction_today}
- `get_or_create_user(whatsapp_number, name)`: Busca ou cria usuário. Retorna dados + is_new_user + is_first_interaction_today
- `update_user_last_interaction(whatsapp_number)`: Atualiza timestamp da última interação

### Transações (NÃO USE AGORA - apenas quando Orchestrator pedir)
- `add_transaction`: Adiciona transação
- `get_transactions`: Lista transações
- `get_balance`: Saldo do usuário
- etc.

## REGRAS
1. Quando Orchestrator perguntar sobre usuário, use `check_user_exists` ou `get_or_create_user`
2. SEMPRE retorne o resultado da tool como está, não modifique
3. Não invente dados - retorne apenas o que a tool retornar
"""


def build_database_agent(model) -> LlmAgent:
    return LlmAgent(
        name="DatabaseAgent",
        model=model,
        description="Executor de operações de banco de dados. Verifica/cria usuários e gerencia transações.",
        instruction=DATABASE_INSTRUCTION,
        tools=[
            # Tools de usuário
            check_user_exists,
            get_or_create_user,
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
