"""Tools de comunicação via WhatsApp (Evolution API)."""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_API_INSTANCE", "LifeOs")


def send_whatsapp_message(phone_number: str, message: str) -> Dict[str, Any]:
    """Envia uma mensagem de texto via WhatsApp."""
    if not phone_number or not message:
        return {"status": "error", "error": "phone_number e message são obrigatórios"}

    if not EVOLUTION_API_KEY:
        return {"status": "error", "error": "EVOLUTION_API_KEY não configurada"}

    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    payload = {"number": phone_number, "text": message}
    headers = {"Content-Type": "application/json", "apikey": EVOLUTION_API_KEY}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {
                "status": "success",
                "message_id": result.get("key", {}).get("id", ""),
                "sent_to": phone_number,
            }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        return {"status": "error", "error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"status": "error", "error": f"Connection error: {str(e.reason)}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_whatsapp_connection() -> Dict[str, Any]:
    """Verifica o status da conexão do WhatsApp."""
    if not EVOLUTION_API_KEY:
        return {"status": "error", "error": "EVOLUTION_API_KEY não configurada"}

    url = f"{EVOLUTION_API_URL}/instance/connectionState/{EVOLUTION_INSTANCE}"
    headers = {"Content-Type": "application/json", "apikey": EVOLUTION_API_KEY}

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            state = result.get(
                "state", result.get("instance", {}).get("state", "unknown")
            )
            return {
                "status": "success",
                "connection_state": state,
                "is_connected": state == "open",
            }

    except Exception as e:
        return {"status": "error", "error": str(e)}
