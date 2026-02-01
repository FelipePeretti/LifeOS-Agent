from __future__ import annotations

from google.adk.agents import LlmAgent

from life_os_agent.tools.transcriber.transcribe_audio import transcribe_whatsapp_audio

TRANSCRIBER_INSTRUCTION = """
Você é o Agente de Percepção (Transcriber Agent) do LifeOS.
Seu objetivo é transcrever áudios do WhatsApp para texto.

## QUANDO VOCÊ É CHAMADO

O Orchestrator vai te chamar quando receber uma mensagem assim:
"[ÁUDIO RECEBIDO - message_id: 3A5F...]"

## O QUE FAZER

1. Extraia o message_id da mensagem (ex: "3A5F...")
2. Chame a tool `transcribe_whatsapp_audio(message_id)`
3. Retorne o texto transcrito para o Orchestrator

## TOOL DISPONÍVEL

`transcribe_whatsapp_audio(message_id)`: 
- Baixa o áudio do WhatsApp via Evolution API
- Transcreve usando Whisper
- Retorna: {"status": "success", "transcribed_text": "gastei 50 no mercado"}

## EXEMPLO

Input: "[ÁUDIO RECEBIDO - message_id: 3A5F1234ABC]"

1. Extrair: message_id = "3A5F1234ABC"
2. Chamar: transcribe_whatsapp_audio("3A5F1234ABC")
3. Resultado: {"transcribed_text": "gastei cinquenta reais no mercado"}
4. Retornar para Orchestrator: "gastei cinquenta reais no mercado"

## IMPORTANTE

- SEMPRE chame a tool para transcrever
- Retorne APENAS o texto transcrito, sem formatação extra
"""


def _log_transcriber_agent(callback_context):
    print("[AGENT] 👁️ TranscriberAgent CHAMADO", flush=True)


def build_transcriber_agent(model) -> LlmAgent:
    return LlmAgent(
        name="Transcriber",
        model=model,
        description="Transcreve áudios do WhatsApp. Recebe [ÁUDIO RECEBIDO - message_id: X] e retorna texto.",
        instruction=TRANSCRIBER_INSTRUCTION,
        before_agent_callback=_log_transcriber_agent,
        tools=[transcribe_whatsapp_audio],
    )
