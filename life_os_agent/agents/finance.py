from __future__ import annotations

from google.adk.agents import LlmAgent

from life_os_agent.tools.finance.finance_unified import process_finance_input

FINANCE_INSTRUCTION = """
Você é o Finance Agent do LifeOS (ML-only).

Seu trabalho é transformar o texto do usuário em um JSON `agent_result`.
Regras:
- Você DEVE chamar a tool `process_finance_input(text)` e retornar para o Orchestrator EXATAMENTE o JSON retornado por ela.
- Retorne APENAS o JSON retornado pela tool. Nada além do JSON.

Não invente timestamp e não imprima/salve nada aqui.
"""


def _log_finance_agent(callback_context):
    print("[AGENT] 💰 FinanceAgent CHAMADO", flush=True)


def build_finance_agent(model) -> LlmAgent:
    return LlmAgent(
        name="FinanceAgent",
        model=model,
        description="Extrai e estrutura lançamentos financeiros a partir do texto do usuário.",
        instruction=FINANCE_INSTRUCTION,
        before_agent_callback=_log_finance_agent,
        tools=[process_finance_input],
        output_key="agent_result",
    )
