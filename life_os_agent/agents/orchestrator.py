from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

from life_os_agent.agents.comms import build_comms_agent
from life_os_agent.agents.database import build_database_agent
from life_os_agent.agents.finance import build_finance_agent
from life_os_agent.agents.perception import build_perception_agent
from life_os_agent.agents.strategist import build_strategist_agent


def _log_orchestrator(callback_context):
    print("[AGENT] 🎯 Orchestrator CHAMADO", flush=True)


ORCHESTRATOR_INSTRUCTION = """
Você é o Orchestrator do LifeOS. Você coordena tarefas usando TOOLS.

## COMO EXTRAIR O NÚMERO DO USUÁRIO

A mensagem que você recebe tem este formato:
```
[CONTEXTO DO USUÁRIO]
user_phone: 556496185377
user_name: João

[MENSAGEM DO USUÁRIO]
Gastei 30 no mercado
```

EXTRAIA o user_phone (ex: 556496185377) e use-o em TODAS as chamadas.

## TOOLS DISPONÍVEIS

1. **DatabaseAgent**: Verificar/criar usuário, salvar transações
2. **FinanceAgent**: Classificar transações financeiras
3. **StrategistAgent**: Consultas de orçamento e metas
4. **CommsAgent**: Enviar resposta ao usuário (SEMPRE no final)
5. **Perception**: Transcrever áudio para texto

## FLUXO PARA ÁUDIO (PRIORIDADE!)

Se a mensagem contiver "[ÁUDIO RECEBIDO - message_id:", faça:

1. **Perception**: Passar a mensagem completa para transcrever
   → Recebe: texto transcrito (ex: "gastei 50 no mercado")
2. Continuar com o fluxo normal usando o texto transcrito

Exemplo:
- Entrada: "[ÁUDIO RECEBIDO - message_id: 3A5F1234]"
- Chamar: Perception("[ÁUDIO RECEBIDO - message_id: 3A5F1234]")
- Resultado: "gastei cinquenta reais no mercado"
- Continuar: FinanceAgent → DatabaseAgent → StrategistAgent → CommsAgent

## FLUXO PARA TRANSAÇÕES (gastei, paguei, comprei, recebi)

1. DatabaseAgent: "verificar usuário [user_phone]"
2. FinanceAgent: "classificar: [texto]"
3. DatabaseAgent: "salvar transação category=[X] amount=[Y]"
4. StrategistAgent: "verificar meta para categoria [X]"
5. CommsAgent: "phone=[user_phone], categoria=[X], valor=[Y], meta=[info]"

## FLUXO PARA CONSULTAS

1. DatabaseAgent: "verificar usuário"
2. StrategistAgent: "consultar [pergunta]"
3. CommsAgent: "responder com dados"

## REGRA CRÍTICA

- Se receber ÁUDIO, chame Perception PRIMEIRO
- SEMPRE termine com CommsAgent
- Use o phone REAL, nunca placeholders (ex: 556496185377, não [user_phone])
"""


def build_orchestrator_agent(model) -> LlmAgent:
    """Constrói o Orchestrator com tools explícitas para cada agente."""

    database_agent = build_database_agent(model)
    finance_agent = build_finance_agent(model)
    strategist_agent = build_strategist_agent(model)
    perception_agent = build_perception_agent(model)
    comms_agent = build_comms_agent(model)

    database_tool = agent_tool.AgentTool(agent=database_agent)
    finance_tool = agent_tool.AgentTool(agent=finance_agent)
    strategist_tool = agent_tool.AgentTool(agent=strategist_agent)
    perception_tool = agent_tool.AgentTool(agent=perception_agent)
    comms_tool = agent_tool.AgentTool(agent=comms_agent)

    return LlmAgent(
        name="Orchestrator",
        model=model,
        description="Coordenador central do LifeOS. Usa tools para chamar agentes especializados.",
        instruction=ORCHESTRATOR_INSTRUCTION,
        before_agent_callback=_log_orchestrator,
        tools=[
            database_tool,
            finance_tool,
            strategist_tool,
            perception_tool,
            comms_tool,
        ],
        sub_agents=[],
    )
