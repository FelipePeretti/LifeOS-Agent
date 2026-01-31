#!/bin/bash
set -e

echo "🔄 Verificando banco de dados..."
python -m life_os_agent.database.setup

chmod 666 /app/life_os_agent/database/lifeos.db 2>/dev/null || true

echo "✅ Banco de dados pronto!"
echo "🚀 Iniciando LifeOS Agent..."

exec "$@"
