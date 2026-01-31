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
```

### 2. Configurar ambiente

```bash
# Copiar templates
cp .env.example .env
cp .env.evolution.example .env.evolution
cp .env.calendar.example .env.calendar

# Editar com suas chaves
nano .env
nano .env.evolution
```

### 3. Subir Stack (Docker)

```bash
docker compose up -d
```

Serviços iniciados:
- **Evolution API**: http://localhost:8080 (WhatsApp)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MCP Google Calendar**: http://localhost:3001
- **LifeOS Agent**: http://localhost:8000

### 4. Inicializar banco de dados

O banco SQLite não é commitado no repositório. Para criá-lo:

```bash
# Via script
python init_db.py

# Ou via Docker (se usando container)
docker exec lifeos_agent python init_db.py
```

O banco será criado em `life_os_agent/database/lifeos.db`.

## 📁 Estrutura

```
├── life_os_agent/       # Agentes Python (orchestrator, finance, comms, calendar)
├── database/            # Módulo SQLite (setup, crud)
├── mcp-google-calendar/ # MCP Server para Google Calendar
├── docs/                # Documentação
└── docker-compose.yml   # Stack completa
```

## 🔧 Variáveis de Ambiente

### `.env` - LifeOS Agent

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `EVOLUTION_API_URL` | URL da Evolution API | `http://evolution-api:8080` |
| `EVOLUTION_API_KEY` | Chave de autenticação da API | `B6D711FC...` |
| `EVOLUTION_API_INSTANCE` | Nome da instância WhatsApp | `LifeOs` |
| `WEBHOOK_PORT` | Porta do webhook listener | `3002` |
| `WEBHOOK_ALLOWED_NUMBER` | Número permitido (com DDI+DDD) | `5564999999999` |
| `POSTGRES_DB` | Nome do banco PostgreSQL | `evolution` |
| `POSTGRES_USER` | Usuário PostgreSQL | `evolution` |
| `POSTGRES_PASSWORD` | Senha PostgreSQL | `sua_senha` |
| `DB_PATH` | Caminho do SQLite (LifeOS) | `/data/lifeos.db` |
| `GOOGLE_API_KEY` | API Key do Google Gemini | `AIzaSy...` |
| `LIFEOS_MODEL_NAME` | Modelo de IA a usar | `gemini-2.5-flash` |
| `LIFEOS_MODEL_PATH` | Caminho do modelo ML | `life_os_agent/model/...` |
| `LIFEOS_DEFAULT_CURRENCY` | Moeda padrão | `BRL` |
| `GOOGLE_CALENDAR_MCP_URL` | URL do MCP Calendar | `http://mcp-google-calendar:3001` |

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

### `.env.calendar` - MCP Google Calendar

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `TRANSPORT` | Modo de transporte | `http` |
| `PORT` | Porta do servidor MCP | `3001` |
| `HOST` | Host de escuta | `0.0.0.0` |
| `GOOGLE_OAUTH_CREDENTIALS` | Caminho para credenciais OAuth | `/app/gcp-oauth.keys.json` |

> 📅 **Setup do Calendar**: Veja a documentação completa em [docs/google-calendar-integration.md](docs/google-calendar-integration.md)
