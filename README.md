# LifeOS-Agent

Sistema de agentes de IA para gestão de vida pessoal via WhatsApp.

## 🚀 Quick Start

### 1. Instalar dependências (mise)

```bash
# Instalar mise (se não tiver)
curl https://mise.run | sh

# Ativar e instalar tools
mise trust
mise install

# Instalar dependências Python
pip install -r requirements.txt

# Instalar dependências do MCP Server
cd mcp-evolution-api && pnpm install && cd ..
```

### 2. Configurar ambiente

```bash
# Copiar templates
cp .env.example .env
cp .env.evolution.example .env.evolution
cp mcp-evolution-api/.env.example mcp-evolution-api/.env

# Editar com suas chaves
nano .env
nano .env.evolution
```

### 3. Subir Evolution API (Docker)

```bash
docker-compose up -d
```

Serviços iniciados:
- **Evolution API**: http://localhost:8080
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Testar MCP Server (Inspector)

```bash
cd mcp-evolution-api
npx @modelcontextprotocol/inspector node dist/cli.js
```

Abre o Inspector em http://localhost:5173 para testar as tools.

### 5. Inicializar banco SQLite

```bash
python -c "from database.setup import init_database; init_database()"
```

## 📁 Estrutura

```
├── life_os_agent/     # Agentes Python (orchestrator, finance, comms)
├── database/          # Módulo SQLite (setup, crud)
├── mcp-evolution-api/ # MCP Server para Evolution API
├── docs/              # Documentação
└── docker-compose.yml # Stack completa
```

## 🔧 Variáveis de Ambiente

### `.env` - LifeOS Agent

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `EVOLUTION_API_URL` | URL da Evolution API | `http://evolution-api:8080` |
| `EVOLUTION_API_KEY` | Chave de autenticação da API | `B6D711FC...` |
| `EVOLUTION_API_INSTANCE` | Nome da instância WhatsApp | `LifeOs` |
| `WEBHOOK_PORT` | Porta do webhook listener | `3001` |
| `WEBHOOK_ALLOWED_NUMBER` | Número permitido (com DDI+DDD) | `5564999999999` |
| `POSTGRES_DB` | Nome do banco PostgreSQL | `evolution` |
| `POSTGRES_USER` | Usuário PostgreSQL | `evolution` |
| `POSTGRES_PASSWORD` | Senha PostgreSQL | `sua_senha` |
| `DB_PATH` | Caminho do SQLite (LifeOS) | `/data/lifeos.db` |
| `GOOGLE_API_KEY` | API Key do Google Gemini | `AIzaSy...` |
| `LIFEOS_MODEL_NAME` | Modelo de IA a usar | `gemini-2.5-flash` |
| `LIFEOS_MODEL_PATH` | Caminho do modelo ML | `life_os_agent/model/...` |
| `LIFEOS_DEFAULT_CURRENCY` | Moeda padrão | `BRL` |

### `.env.evolution` - Evolution API

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SERVER_PORT` | Porta do servidor | `8080` |
| `AUTHENTICATION_API_KEY` | Mesma chave do `.env` | - |
| `DATABASE_CONNECTION_URI` | URI do PostgreSQL | `postgresql://...` |
| `CACHE_REDIS_URI` | URI do Redis | `redis://redis:6379/0` |
| `LOG_LEVEL` | Níveis de log | `ERROR,WARN,INFO` |
| `LANGUAGE` | Idioma | `pt-BR` |

> ⚠️ **Importante**: A `AUTHENTICATION_API_KEY` no `.env.evolution` deve ser igual à `EVOLUTION_API_KEY` no `.env`

### `mcp-evolution-api/.env` - MCP Server

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `EVOLUTION_API_URL` | URL da API (**localhost**, roda fora do Docker) | `http://localhost:8080` |
| `EVOLUTION_API_KEY` | Mesma chave dos outros `.env` | `B6D711FC...` |
| `EVOLUTION_API_INSTANCE` | Nome da instância | `LifeOs` |
| `WEBHOOK_PORT` | Porta para receber webhooks | `3001` |
| `WEBHOOK_ALLOWED_NUMBER` | Número permitido (DDI+DDD) | `5564999999999` |

> 💡 **Nota**: O MCP Server usa `localhost:8080` porque roda **fora** do Docker (no host), diferente do LifeOS Agent que usa `evolution-api:8080` (rede Docker).
