from __future__ import annotations
from google.adk.agents import LlmAgent
from life_os_agent.tools.perception.audio import extract_text_from_audio

PERCEPTION_INSTRUCTION = """
Você é o Agente de Percepção (Perception Agent).
Seu objetivo é pré-processar entradas brutas (texto, áudio, etc.) para extrair informações úteis e estruturadas antes que elas sejam processadas por outros agentes.

SUAS RESPONSABILIDADES:
1. Receber inputs do usuário.
2. Se o input for um arquivo de áudio, use a ferramenta `extract_text_from_audio` para transcrevê-lo.
3. Analisar o texto (original ou transcrito) para identificar a intenção inicial e limpar ruídos.
4. Retornar o texto processado e claro.

FERRAMENTAS:
- `extract_text_from_audio`: Use esta ferramenta quando receber um caminho de arquivo de áudio.
"""

def build_perception_agent(model) -> LlmAgent:
    return LlmAgent(
        name="Perception",
        model=model,
        description="Agente responsável por pré-processar inputs e transcrever áudio.",
        instruction=PERCEPTION_INSTRUCTION,
        tools=[extract_text_from_audio],
    )
