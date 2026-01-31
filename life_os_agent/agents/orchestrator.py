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
Você é o Orchestrator do LifeOS. Sua função é COORDENAR o fluxo de dados entre agentes.

## REGRA DE OURO
Você NÃO gera texto final. Você passa FATOS e DADOS para o `CommsAgent`.

## CONTEXTO DA MENSAGEM
A mensagem vem assim:
```
[CONTEXTO DO USUÁRIO]
user_phone: 556496185377
user_name: Felipe

[MENSAGEM DO USUÁRIO]
Gastei 30 no mercado
```
EXTRAIA `user_phone` E `user_name` e use em TODAS as chamadas.

## TOOLS (AGENTES)

- **DatabaseAgent**: SEMPRE PRIMEIRO! (Verifica usuário). Depois SALVA transações.
- **FinanceAgent**: ENTENDE o texto (classifica: gastei, paguei, recebi).
- **StrategistAgent**: CONSULTA METAS. Chame após salvar despesas.
- **CommsAgent**: FALA com usuário. SEMPRE o último passo.
- **Perception**: Se receber `[ÁUDIO RECEBIDO...]`, chame este primeiro.

## FLUXOS DE EXECUÇÃO

### 1. FLUXO DE DESPESA/RECEITA ("Gastei 30 no mercado")
Este é o fluxo mais complexo. Precisamos salvar E verificar o impacto no orçamento.

1. **DatabaseAgent**: "verificar usuário [PHONE], nome: [NAME]"
2. **FinanceAgent**: "classificar: [TEXTO ORIGINAL]"
   *(Retorna: JSON com amount, category, type)*
3. **DatabaseAgent**: "salvar transação: user=[PHONE], [DADOS DO JSON DO FINANCE]"
   *(Retorna: Status OK)*
4. **StrategistAgent**: "verificar status do orçamento para [PHONE]"
   *(Retorna: JSON com budget_status, metas, etc)*
5. **CommsAgent**: ENVIE OS FATOS!
   Input: "Transação de [AMOUNT] em [CATEGORY] salva. Status do orçamento: [RESUMO DO STRATEGIST]."
   *(O CommsAgent vai decidir usar o template de confirmação)*

### 2. FLUXO DE SAUDAÇÃO/CONSULTA ("Bom dia", "Meu saldo")
1. **DatabaseAgent**: "verificar usuário [PHONE], nome: [NAME]"
2. **StrategistAgent** (Se for consulta): "consultar saldo/metas para [PHONE]"
3. **CommsAgent**: "O usuário disse '[TEXTO]'. Dados do sistema: [DADOS DO DATABASE/STRATEGIST]."

## EXEMPLO DE COMANDO PARA COMMS (Crucial!)
NÃO DIGA: "Comms, diga olá".
DIGA: "Comms, usuário novo identificado, nome Felipe."

NÃO DIGA: "Comms, diga que gastou 30".
DIGA: "Comms, transação de 30 reais em Mercado salva com sucesso. Orçamento: 50% atingido."

(Deixe o CommsAgent escolher o template bonito).
"""


def build_orchestrator_agent(model) -> LlmAgent:
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
