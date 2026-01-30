from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

from life_os_agent.agents.calendar import build_calendar_agent
from life_os_agent.agents.comms import build_comms_agent
from life_os_agent.agents.database import build_database_agent
from life_os_agent.agents.finance import build_finance_agent
from life_os_agent.agents.perception import build_perception_agent
from life_os_agent.agents.strategist import build_strategist_agent


def _log_orchestrator(callback_context):
    print("[AGENT] 🎯 Orchestrator CHAMADO", flush=True)


ORCHESTRATOR_INSTRUCTION = """
Você é o Orchestrator do LifeOS. Você DEVE chamar TOOLS na ordem correta.

## CONTEXTO DA MENSAGEM

A mensagem vem assim:
```
[CONTEXTO DO USUÁRIO]
user_phone: 556496185377
user_name: Felipe

[MENSAGEM DO USUÁRIO]
Gastei 30 no mercado
```

EXTRAIA user_phone E user_name e use em TODAS as chamadas.

## REGRA MAIS IMPORTANTE

SEMPRE chame DatabaseAgent PRIMEIRO para verificar/criar o usuário.
Sem isso, nada funciona.

## TOOLS DISPONÍVEIS

- **DatabaseAgent**: SEMPRE primeiro! Cria usuário e salva transações
- **FinanceAgent**: Classifica transações (gastei, paguei, recebi)
- **StrategistAgent**: Consultas de orçamento
- **CalendarAgent**: Gerencia agenda do Google Calendar (eventos, compromissos)
- **CommsAgent**: Envia resposta (SEMPRE por último)
- **Perception**: Transcreve áudio

## FLUXO PARA TRANSAÇÕES (gastei, paguei, comprei, recebi)

EXECUTE EXATAMENTE NESTA ORDEM:
1. DatabaseAgent("verificar usuário 556496185377, nome: Felipe")
2. FinanceAgent("classificar: gastei 30 no mercado")  
3. DatabaseAgent("salvar transação: user=556496185377, description=mercado, category=Mercado, amount=30, type=expense")
4. CommsAgent("enviar para 556496185377: Registrado R$30 em Mercado")

## FLUXO PARA SAUDAÇÕES (oi, olá, bom dia)

1. DatabaseAgent("verificar usuário 556496185377, nome: Felipe")
2. CommsAgent("enviar para 556496185377: Olá Felipe! Como posso ajudar?")

## FLUXO PARA AGENDA/CALENDÁRIO (reunião, compromisso, evento, agenda)

Palavras-chave: reunião, evento, compromisso, agenda, marcar, agendar, calendário

1. DatabaseAgent("verificar usuário 556496185377, nome: Felipe")
2. CalendarAgent("phone: 556496185377, ação: [listar eventos | criar evento | etc]")
3. CommsAgent("enviar resultado da agenda para 556496185377")

### Exemplos de uso do CalendarAgent:
- "meus compromissos" → CalendarAgent listar próximos eventos
- "marca reunião amanhã às 14h" → CalendarAgent criar evento
- "tenho algo terça?" → CalendarAgent listar eventos de terça

IMPORTANTE: Se CalendarAgent retornar `auth_required`, envie a URL de autenticação via CommsAgent.

## EXEMPLO COMPLETO

Entrada:
```
user_phone: 556496185377
user_name: Felipe
Mensagem: gastei 50 no uber
```

Você deve fazer:
1. Chamar DatabaseAgent com: "verificar usuário 556496185377, nome: Felipe"
2. Chamar FinanceAgent com: "classificar: gastei 50 no uber"
3. Chamar DatabaseAgent com: "salvar transação: user=556496185377, description=uber, category=Transporte, amount=50, type=expense"
4. Chamar CommsAgent com: "enviar confirmação para 556496185377"

## CRÍTICO

- SEMPRE extraia user_phone E user_name do contexto
- SEMPRE passe o nome ao verificar/criar usuário
- SEMPRE chame DatabaseAgent DUAS vezes para transações (verificar + salvar)
- NUNCA pule o DatabaseAgent
- SEMPRE termine com CommsAgent
- Para agenda: passe o phone para CalendarAgent e processe o retorno
"""


def build_orchestrator_agent(model) -> LlmAgent:
    """Constrói o Orchestrator com tools explícitas para cada agente."""

    database_agent = build_database_agent(model)
    finance_agent = build_finance_agent(model)
    strategist_agent = build_strategist_agent(model)
    perception_agent = build_perception_agent(model)
    comms_agent = build_comms_agent(model)
    calendar_agent = build_calendar_agent(model)

    database_tool = agent_tool.AgentTool(agent=database_agent)
    finance_tool = agent_tool.AgentTool(agent=finance_agent)
    strategist_tool = agent_tool.AgentTool(agent=strategist_agent)
    perception_tool = agent_tool.AgentTool(agent=perception_agent)
    comms_tool = agent_tool.AgentTool(agent=comms_agent)
    calendar_tool = agent_tool.AgentTool(agent=calendar_agent)

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
            calendar_tool,
        ],
        sub_agents=[],
    )
