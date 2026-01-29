#!/bin/bash
# Script para iniciar o ADK Web Server e o Webhook simultaneamente

echo "[LifeOS] Iniciando serviços..."

# Inicia o ADK Web Server em background (inclui API + interface web dev-ui)
# O comando 'adk web' serve tanto a API REST quanto a interface de desenvolvimento
echo "[LifeOS] Iniciando ADK Web Server na porta 8000..."
adk web --host 0.0.0.0 --port 8000 /app &
ADK_PID=$!

# Espera um pouco para o ADK iniciar
sleep 3

# Inicia o Webhook
echo "[LifeOS] Iniciando Webhook na porta 3002..."
python -m life_os_agent.webhook &
WEBHOOK_PID=$!

echo "[LifeOS] Serviços iniciados:"
echo "  - ADK API Server (PID: $ADK_PID) -> porta 8000"
echo "  - Webhook (PID: $WEBHOOK_PID) -> porta 3002"

# Função para encerrar processos graciosamente
cleanup() {
    echo "[LifeOS] Encerrando serviços..."
    kill $ADK_PID 2>/dev/null
    kill $WEBHOOK_PID 2>/dev/null
    exit 0
}

# Captura SIGTERM e SIGINT
trap cleanup SIGTERM SIGINT

# Aguarda qualquer processo terminar
wait -n

# Se qualquer processo morrer, mata os outros e sai
cleanup
