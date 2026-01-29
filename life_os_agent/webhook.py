"""Webhook - Recebe mensagens do WhatsApp e repassa para o ADK."""

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

ADK_API_URL = os.getenv("ADK_API_URL", "http://localhost:8000")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "3002"))
APP_NAME = "life_os_agent"


def log(msg: str):
    print(msg, flush=True)


def ensure_session_exists(user_id: str, session_id: str) -> bool:
    """Garante que a sessão ADK existe, criando se necessário."""
    url = f"{ADK_API_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
    headers = {"Content-Type": "application/json"}

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=10):
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            try:
                data = json.dumps({}).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data, headers=headers, method="POST"
                )
                with urllib.request.urlopen(req, timeout=10):
                    return True
            except Exception:
                return False
        return False
    except Exception:
        return False


def call_adk_agent(
    user_id: str, user_name: str, message: str, session_id: Optional[str] = None
) -> dict:
    """Chama o agente ADK via API REST."""
    if session_id is None:
        session_id = f"session_{user_id}"

    if not ensure_session_exists(user_id, session_id):
        return {"status": "error", "error": "Failed to create/verify session"}

    formatted_message = f"""[CONTEXTO DO USUÁRIO]
user_phone: {user_id}
user_name: {user_name or "Desconhecido"}

[MENSAGEM DO USUÁRIO]
{message}"""

    payload = {
        "appName": APP_NAME,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {"role": "user", "parts": [{"text": formatted_message}]},
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{ADK_API_URL}/run",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            events = json.loads(response.read().decode("utf-8"))
            full_response = ""

            for event in events:
                content = event.get("content", {})
                if content.get("role") == "model" and "parts" in content:
                    for part in content["parts"]:
                        if "text" in part:
                            full_response = part["text"]

            return {"status": "success", "response": full_response}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return {"status": "error", "error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"status": "error", "error": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def extract_phone_number(data: dict, key: dict) -> str:
    """Extrai o número de telefone, resolvendo LID se necessário."""
    remote_jid = key.get("remoteJid", "")
    remote_jid_alt = data.get("remoteJidAlt", "")
    sender_pn = data.get("senderPn", "")

    if remote_jid_alt:
        return remote_jid_alt.replace("@s.whatsapp.net", "").replace("@c.us", "")
    if sender_pn:
        return sender_pn
    if remote_jid and "@lid" not in remote_jid:
        phone = remote_jid
        for suffix in ["@s.whatsapp.net", "@g.us", "@c.us"]:
            phone = phone.replace(suffix, "")
        return phone
    return remote_jid.replace("@lid", "")


def extract_message_from_webhook(webhook_data: dict) -> Optional[dict]:
    """Extrai informações relevantes do payload do webhook."""
    event = webhook_data.get("event", "").lower()

    if event not in ("messages.upsert", "messages_upsert"):
        return None

    data = webhook_data.get("data", {})
    key = data.get("key", {})
    is_from_me = key.get("fromMe", False)

    phone_number = extract_phone_number(data, key)
    if not phone_number:
        return None

    push_name = data.get("pushName", "")
    message_content = data.get("message", {})

    text = None
    message_type = "text"

    if "conversation" in message_content:
        text = message_content["conversation"]
    elif "extendedTextMessage" in message_content:
        text = message_content["extendedTextMessage"].get("text", "")
    elif "audioMessage" in message_content:
        text = "[ÁUDIO RECEBIDO]"
        message_type = "audio"

    if not text:
        return None

    return {
        "phone_number": phone_number,
        "push_name": push_name,
        "text": text,
        "message_type": message_type,
        "is_from_me": is_from_me,
    }


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            webhook_data = json.loads(body.decode("utf-8"))

            message_info = extract_message_from_webhook(webhook_data)

            if message_info:
                phone = message_info["phone_number"]
                name = message_info.get("push_name", "")
                text = message_info["text"]
                is_from_me = message_info.get("is_from_me", False)

                if is_from_me:
                    self._respond(200, {"ok": True, "direction": "outgoing"})
                    return

                log(f"[Webhook] {name} ({phone}): {text[:50]}...")
                result = call_adk_agent(user_id=phone, user_name=name, message=text)
                self._respond(200, {"ok": True, "result": result})
            else:
                self._respond(200, {"ok": True, "ignored": True})

        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
        except Exception as e:
            log(f"[Webhook] Erro: {e}")
            self._respond(500, {"error": str(e)})

    def do_GET(self):
        self._respond(200, {"status": "healthy", "service": "webhook"})

    def _respond(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def main():
    server_address = ("0.0.0.0", WEBHOOK_PORT)
    httpd = HTTPServer(server_address, WebhookHandler)
    log(f"[Webhook] Porta {WEBHOOK_PORT} | ADK: {ADK_API_URL}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()
