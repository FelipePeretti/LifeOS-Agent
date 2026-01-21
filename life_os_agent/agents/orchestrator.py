from __future__ import annotations
import os
from google.adk.agents import LlmAgent

from .finance import build_finance_agent
from .comms import build_comms_agent

from life_os_agent.tools.finance.transaction_pipeline import is_finance_related, apply_confirmation
from life_os_agent.tools.finance.pending_store import (
    has_pending_transaction, set_pending_transaction, get_pending_transaction, clear_pending_transaction
)
from google.adk.tools import transfer_to_agent
from life_os_agent.tools.finance.mock_storage import print_transaction_payload  

ORCHESTRATOR_INSTRUCTION = """
Você é o Agente Orquestrador do LifeOS.

Fluxo:

0) Primeiro, chame has_pending_transaction().
   - Se has_pending=true: chame get_pending_transaction(), depois chame apply_confirmation(user_text, pending_payload).
     - Se status=ok: chame print_transaction_payload(transaction_payload) e clear_pending_transaction().
     - Se status=cancelled: chame clear_pending_transaction().
     - Depois delegue ao CommsAgent para gerar a resposta final ao usuário.
     - Pare.

1) Se NÃO há pendência: chame is_finance_related(user_text).
   - Se is_finance=false: responda educadamente (cumprimento/ajuda) SEM chamar FinanceAgent.

2) Se is_finance=true:
   - Delegue ao FinanceAgent.
   - Se o FinanceAgent retornar status=need_confirmation:
        chame set_pending_transaction(transaction_payload) e depois delegue ao CommsAgent (para perguntar 1 coisa objetiva).
   - Se status=ok:
        chame print_transaction_payload(transaction_payload) e delegue ao CommsAgent para confirmar ao usuário.

IMPORTANTE (TOOLS):
- Você PODE e DEVE usar as tools listadas abaixo quando necessário:
  has_pending_transaction, get_pending_transaction, set_pending_transaction, clear_pending_transaction,
  is_finance_related, apply_confirmation, print_transaction_payload, transfer_to_agent.
- Use transfer_to_agent APENAS para delegar ao FinanceAgent ou CommsAgent.
- Não escreva "transfer_to_agent(...)" como texto; execute como tool-call.

Exemplo de resposta caso o usuario pergunte o que você pode fazer:
Posso te ajudar com:
- Registrar gastos e rendas a partir de texto (ex.: "gastei 35,90 no Uber").
- Ajustar categoria quando estiver incerta.
- Extrair valor e moeda do texto.
- Gerar um resumo do que seria salvo (sem banco por enquanto).

"""

def build_orchestrator_agent(model) -> LlmAgent:
    finance = build_finance_agent(model=model)
    comms = build_comms_agent(model=model)

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
        ],
        sub_agents=[finance, comms],
    )
