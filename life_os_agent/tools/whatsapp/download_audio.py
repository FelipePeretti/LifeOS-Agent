import base64
import json
import os
import tempfile
import urllib.error
import urllib.request
from typing import Optional

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_API_INSTANCE", "LifeOs")


def download_audio_from_message(message_id: str) -> Optional[str]:
    """
    Baixa o áudio de uma mensagem do WhatsApp e retorna o caminho do arquivo temporário.

    Args:
        message_id: ID da mensagem que contém o áudio

    Returns:
        Caminho do arquivo de áudio baixado, ou None se falhar
    """
    if not EVOLUTION_API_KEY:
        return None

    url = f"{EVOLUTION_API_URL}/chat/getBase64FromMediaMessage/{EVOLUTION_INSTANCE}"
    payload = {"message": {"key": {"id": message_id}}}
    headers = {"Content-Type": "application/json", "apikey": EVOLUTION_API_KEY}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

            base64_data = result.get("base64")
            mimetype = result.get("mimetype", "audio/ogg")

            if not base64_data:
                return None

            ext = ".ogg"
            if "mp3" in mimetype:
                ext = ".mp3"
            elif "mp4" in mimetype or "m4a" in mimetype:
                ext = ".m4a"
            elif "wav" in mimetype:
                ext = ".wav"

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            temp_file.write(base64.b64decode(base64_data))
            temp_file.close()

            return temp_file.name

    except Exception:
        return None


def cleanup_audio_file(file_path: str) -> None:
    """Remove o arquivo de áudio temporário."""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass
