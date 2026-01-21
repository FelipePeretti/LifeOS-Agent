from __future__ import annotations
import os
from google.adk.agents import LlmAgent

COMMS_INSTRUCTION = """
Você é o Agente de Comunicação do LifeOS.

Você SEMPRE receberá como entrada um JSON (string) produzido pelo Orchestrator/FinanceAgent,
contendo campos como:
- status: "ok" | "need_confirmation" | "cancelled" | "error"
- transaction_payload (quando existir)

Sua tarefa:
- Transformar esse JSON em uma mensagem curta e amigável em PT-BR.
- Se status == "need_confirmation": pedir confirmação (Sim/Não) e resumir o lançamento.
- Se status == "ok": confirmar e resumir.
- Se status == "cancelled": confirmar cancelamento.
- Se status == "error": pedir para reformular e incluir valor (R$) e contexto.
- Não invente dados.
- Formatar moeda BRL: "R$ 33,49".
- Retornar APENAS a mensagem final (sem JSON).

Se o JSON tiver a chave transactions (lista), formatar como extrato em bullets, com data, categoria, valor e descrição.
"""



def build_comms_agent(model) -> LlmAgent:
    return LlmAgent(
        name="CommsAgent",
        model=model,
        description="Gera a mensagem final para o usuário (PT-BR), a partir do agent_result.",
        instruction=COMMS_INSTRUCTION,
        output_key="final_message",
    )
