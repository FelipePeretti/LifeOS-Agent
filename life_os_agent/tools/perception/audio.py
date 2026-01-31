import os

import whisper


def extract_text_from_audio(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        return f"Erro: Arquivo de áudio não encontrado em {audio_path}"

    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        return f"Erro ao transcrever áudio: {str(e)}"
