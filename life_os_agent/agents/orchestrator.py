from __future__ import annotations
import os
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

from .finance import build_finance_agent
from .comms import build_comms_agent

from life_os_agent.tools.finance.transaction_pipeline import is_finance_related, apply_confirmation
from life_os_agent.tools.finance.pending_store import (
    has_pending_transaction, set_pending_transaction, get_pending_transaction, clear_pending_transaction
)
from life_os_agent.tools.finance.mock_storage import print_transaction_payload  

from life_os_agent.tools.db.sqlite_tools import init_db, upsert_user, save_transaction, get_transactions

ORCHESTRATOR_INSTRUCTION = """
Você é o Orchestrator do LifeOS.

REGRAS:
- NÃO deixe o FinanceAgent falar direto com o usuário.
- Sempre que você tiver um JSON (resultado do FinanceAgent ou apply_confirmation),
  chame a tool CommsAgent passando ESSE JSON como entrada, e retorne APENAS o texto do CommsAgent.

FLUXO:
0) Se houver pendência:
- has_pending_transaction()
- se true: pending = get_pending_transaction()
- result_json = apply_confirmation(user_text, pending)
- se result_json.status == ok: print_transaction_payload(...) e clear_pending_transaction()
- se cancelled: clear_pending_transaction()
- chame CommsAgent(result_json) e retorne a mensagem.

1) Se não houver pendência:
- is_finance_related(user_text)
- se false: responda você mesmo brevemente (sem chamar CommsAgent).

2) Se for finanças:
- result_json = FinanceAgent(user_text)   (chamado como tool)
- se status == need_confirmation: set_pending_transaction(result_json.transaction_payload)
- se status == ok: print_transaction_payload(result_json.transaction_payload)
- chame CommsAgent(result_json) e retorne a mensagem.

PERSISTÊNCIA (SQLite):
- Sempre normalize o retorno do FinanceAgent assim:
  resp = result_json.get("make_transaction_payload_response", result_json)

- Se resp.status == "ok":
  - Você DEVE gravar no banco chamando save_transaction(resp.transaction_payload, user_id=<id_do_usuario>).
  - Depois chame CommsAgent passando o JSON (pode incluir o inserted_id se quiser).

- Se resp.status == "need_confirmation":
  - NÃO grave no banco.
  - Chame set_pending_transaction(resp.transaction_payload).
  - Depois chame CommsAgent para pedir confirmação.

PENDING -> CONFIRMAÇÃO:
- Quando houver transação pendente:
  - result2 = apply_confirmation(user_text, pending_payload)
  - Se result2.status == "ok":
      - chame save_transaction(result2.transaction_payload, user_id=<id_do_usuario>)
      - clear_pending_transaction()
    Se result2.status == "cancelled":
      - clear_pending_transaction()
  - Depois chame CommsAgent(result2) e retorne a mensagem.

HISTÓRICO:
- Se o usuário pedir extrato / últimas transações / histórico:
  - chame get_transactions(user_id=<id_do_usuario>, limit=10, type/categoria se aplicável)
  - passe o JSON retornado para o CommsAgent formatar.

"""


def build_orchestrator_agent(model) -> LlmAgent:
    finance = build_finance_agent(model=model)
    comms = build_comms_agent(model=model)

    finance_tool = agent_tool.AgentTool(agent=finance)
    comms_tool = agent_tool.AgentTool(agent=comms)

    return LlmAgent(
        name="Orchestrator",
        model=model,
        description="Agente orquestrador do LifeOS",
        instruction=ORCHESTRATOR_INSTRUCTION,
        tools=[
            has_pending_transaction,
            get_pending_transaction,
            set_pending_transaction,
            clear_pending_transaction,
            is_finance_related,
            apply_confirmation,
            print_transaction_payload,
            finance_tool,
            comms_tool,
            init_db,
            upsert_user,
            save_transaction,
            get_transactions,
        ],
        sub_agents=[finance, comms],
    )
