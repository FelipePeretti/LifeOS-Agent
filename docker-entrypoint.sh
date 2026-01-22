#!/bin/bash
set -e

# Inicializar o banco de dados SQLite se não existir
echo "🔄 Verificando banco de dados..."
python -m database.setup

echo "✅ Banco de dados pronto!"
echo "🚀 Iniciando LifeOS Agent..."

exec "$@"
