#!/usr/bin/env python3


import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), value)
        print(f"✅ Carregado .env de: {env_path}")
    else:
        print(f"⚠️  Arquivo .env não encontrado em: {env_path}")


load_env()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_API_INSTANCE", "LifeOs")

WEBHOOK_BRIDGE_URL = os.getenv("WEBHOOK_BRIDGE_URL", "http://localhost:3002")


def make_request(url: str, method: str = "GET", data: dict = None) -> dict:
    headers = {"Content-Type": "application/json", "apikey": EVOLUTION_API_KEY}

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        print(f"❌ HTTP Error {e.code}: {error_body}")
        return {"error": error_body, "code": e.code}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}


def check_connection():
    url = f"{EVOLUTION_API_URL}/instance/connectionState/{EVOLUTION_INSTANCE}"
    result = make_request(url)
    state = result.get("state", result.get("instance", {}).get("state", "unknown"))
    print(f"📱 Status da instância: {state}")
    return state


def get_webhook_config():
    url = f"{EVOLUTION_API_URL}/webhook/find/{EVOLUTION_INSTANCE}"
    result = make_request(url)

    if "error" not in result:
        print("📋 Configuração atual do webhook:")
        print(f"   URL: {result.get('url', 'Não configurado')}")
        print(f"   Ativo: {result.get('enabled', False)}")
        print(f"   Eventos: {result.get('events', [])}")
    return result


def configure_webhook():
    url = f"{EVOLUTION_API_URL}/webhook/set/{EVOLUTION_INSTANCE}"

    payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_BRIDGE_URL,
            "webhookByEvents": False,
            "webhookBase64": False,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE",
            ],
        }
    }

    print("🔧 Configurando webhook...")
    print(f"   Evolution API: {EVOLUTION_API_URL}")
    print(f"   Instância: {EVOLUTION_INSTANCE}")
    print(f"   Webhook URL: {WEBHOOK_BRIDGE_URL}")

    result = make_request(url, method="POST", data=payload)

    if "error" not in result:
        print("✅ Webhook configurado com sucesso!")
        return True
    return False


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 LifeOS Agent - Configuração de Webhook")
    print("=" * 50)

    if not EVOLUTION_API_KEY:
        print("⚠️  EVOLUTION_API_KEY não configurada!")
        print("   Configure a variável de ambiente antes de executar.")
        sys.exit(1)

    print("\n1️⃣ Verificando conexão...")
    state = check_connection()
    if state != "open":
        print(f"⚠️  Instância não está conectada (state={state})")
        print("   Conecte o WhatsApp via QR Code primeiro.")

    print("\n2️⃣ Configuração atual...")
    get_webhook_config()

    print("\n3️⃣ Configurando webhook...")
    if configure_webhook():
        print("\n✅ Pronto! O webhook está configurado.")
        print("\nPróximos passos:")
        print("1. Inicie o MCP Node.js: npx ts-node src/cli.ts")
        print("2. As mensagens serão recebidas pelo MCP")
        print("3. Use as tools do MCP para processar e responder")
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        sys.exit(1)
