from __future__ import annotations
from google.adk.agents import LlmAgent
from life_os_agent.database.crud import (
    add_transaction,
    get_transactions,
    update_transaction,
    delete_transaction,
    get_balance,
    get_expenses_by_category,
    set_budget_goal,
    get_budget_status,
    add_calendar_log,
    get_calendar_logs,
    get_or_create_user
)
from life_os_agent.database.setup import init_database

DATABASE_INSTRUCTION = """
Você é o Database Agent do LifeOS.
Sua única responsabilidade é executar operações de leitura e escrita no banco de dados SQLite.

REGRA DE OURO:
- Você é um executor técnico.
- Se o Orchestrator mandar salvar uma transação (`add_transaction`), certifique-se que o usuário existe primeiro!
  - Se for um novo usuário, CHAME `get_or_create_user` antes de inserir.
- Se ele pedir relatório, use as funções de `get_...`.
- Se ele pedir alteração ou remoção, use `update_transaction` ou `delete_transaction`. Para isso, você vai precisar do ID da transação (que geralmente vem no extrato).

Formato de Saída:
- Retorne SEMPRE o JSON/Dict que a tool retornou.
"""

def build_database_agent(model) -> LlmAgent:
    return LlmAgent(
        name="DatabaseAgent",
        model=model,
        description="Executor de operações de banco de dados (Salvar transações, consultar extratos, metas, etc).",
        instruction=DATABASE_INSTRUCTION,
        tools=[
            add_transaction,
            get_transactions,
            update_transaction,
            delete_transaction,
            get_balance,
            get_expenses_by_category,
            set_budget_goal,
            get_budget_status,
            add_calendar_log,
            get_calendar_logs,
            get_or_create_user,
            init_database
        ],
    )
