from typing import Any, Dict

from life_os_agent.tools.perception.audio import extract_text_from_audio
from life_os_agent.tools.whatsapp.download_audio import (
    cleanup_audio_file,
    download_audio_from_message,
)


def transcribe_whatsapp_audio(message_id: str) -> Dict[str, Any]:
    if not message_id:
        return {"status": "error", "error": "message_id é obrigatório"}

    audio_file = download_audio_from_message(message_id)
    if not audio_file:
        return {"status": "error", "error": "Não foi possível baixar o áudio"}

    try:
        transcribed_text = extract_text_from_audio(audio_file)

        if transcribed_text and not transcribed_text.startswith("Erro"):
            print(
                f"[PerceptionAgent] 🎤 Áudio transcrito: {transcribed_text[:80]}...",
                flush=True,
            )
            return {"status": "success", "transcribed_text": transcribed_text}
        else:
            return {
                "status": "error",
                "error": transcribed_text or "Falha na transcrição",
            }
    finally:
        cleanup_audio_file(audio_file)
