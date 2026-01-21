from __future__ import annotations
import os
from google.adk.agents import LlmAgent
from life_os_agent.tools.finance.transaction_pipeline import make_transaction_payload

FINANCE_INSTRUCTION = """
Você é o Finance Agent do LifeOS (ML-only).

Seu trabalho é transformar o texto do usuário em um JSON `agent_result`.
Regra: você DEVE chamar a tool `make_transaction_payload(raw_text)` e retornar EXATAMENTE o JSON retornado por ela.
Não invente timestamp e não imprima/salve nada aqui.
"""


def build_finance_agent(model) -> LlmAgent:
    return LlmAgent(
        name="FinanceAgent",
        model=model,
        instruction=FINANCE_INSTRUCTION,
        tools=[make_transaction_payload],
        output_key="agent_result",
    )
