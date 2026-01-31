#!/bin/bash

echo "[LifeOS] Iniciando serviços..."
echo "[LifeOS] Iniciando ADK Web Server na porta 8000..."
adk web --host 0.0.0.0 --port 8000 /app &
ADK_PID=$!
sleep 3
echo "[LifeOS] Iniciando Webhook na porta 3002..."
python -m life_os_agent.webhook &
WEBHOOK_PID=$!

echo "[LifeOS] Serviços iniciados:"
echo "  - ADK API Server (PID: $ADK_PID) -> porta 8000"
echo "  - Webhook (PID: $WEBHOOK_PID) -> porta 3002"

cleanup() {
    echo "[LifeOS] Encerrando serviços..."
    kill $ADK_PID 2>/dev/null
    kill $WEBHOOK_PID 2>/dev/null
    exit 0
}

trap cleanup SIGTERM SIGINT
wait -n
cleanup
