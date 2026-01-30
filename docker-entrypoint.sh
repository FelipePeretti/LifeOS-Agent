#!/bin/bash
set -e

# Inicializar o banco de dados SQLite se não existir
echo "🔄 Verificando banco de dados..."
python -m life_os_agent.database.setup

# Garantir permissões de escrita no banco
chmod 666 /app/life_os_agent/database/lifeos.db 2>/dev/null || true

echo "✅ Banco de dados pronto!"
echo "🚀 Iniciando LifeOS Agent..."

exec "$@"
