# LifeOS-Agent

Sistema de agentes de IA para gestão de vida pessoal via WhatsApp. O LifeOS-Agent integra inteligência artificial com ferramentas de produtividade para ajudar na organização diária, finanças, comunicação e agendamento, tudo acessível através do WhatsApp.

## 📋 O que é o LifeOS-Agent?

O LifeOS-Agent é uma plataforma de agentes de IA que transforma o WhatsApp em um assistente pessoal inteligente. Ele combina:

- **Agentes especializados**: Orquestrador, financeiro, comunicação, percepção, estrategista e calendário.
- **Integrações externas**: Google Calendar via MCP (Model Context Protocol), Evolution API para WhatsApp.
- **Banco de dados**: PostgreSQL para dados externos e SQLite para dados internos do agente.
- **IA generativa**: Usa modelos como Gemini para processamento de linguagem natural.

O sistema permite gerenciar finanças, agendar eventos, transcrever áudios, enviar mensagens e muito mais, tudo via conversas no WhatsApp.

## 🏗️ Arquitetura e Componentes

### Agentes do Sistema

O LifeOS-Agent é composto por vários agentes especializados que trabalham em conjunto:

- **Orchestrator**: Coordena todas as operações, decide qual agente usar baseado na solicitação do usuário.
- **Finance**: Gerencia transações, classifica despesas usando ML (modelo de classificação treinado), gera relatórios financeiros.
- **Communicator**: Lida com comunicação via WhatsApp, envia respostas e gerencia conversas.
- **Transcriber**: Processa entradas multimídia como áudio (transcrição via Whisper) e imagens.
- **Strategist**: Planeja e otimiza tarefas, sugere ações baseadas em dados históricos.
- **Calendar**: Integra com Google Calendar para agendamento, consultas e gerenciamento de eventos.

### MCP Google Calendar

O **Model Context Protocol (MCP)** é um protocolo padrão para conectar ferramentas externas a assistentes de IA. O MCP Google Calendar permite:

- **Multi-conta**: Conectar várias contas Google simultaneamente.
- **Multi-calendário**: Consultar eventos de vários calendários de uma vez.
- **Detecção de conflitos**: Identificar sobreposições de eventos entre contas.
- **Gerenciamento completo**: Criar, editar, deletar e buscar eventos.
- **Agendamento inteligente**: Entendimento de linguagem natural para datas e horários.
- **Importação inteligente**: Adicionar eventos de imagens, PDFs ou links.

O MCP roda como um servidor HTTP separado, integrado ao Docker Compose.

### Infraestrutura

- **Evolution API**: API para integração com WhatsApp Business.
- **PostgreSQL + Redis**: Banco e cache para a Evolution API.
- **SQLite**: Banco local para dados do agente (não versionado).
- **Docker Compose**: Orquestração de todos os serviços.

## 🚀 Guia Completo de Instalação

Siga estes passos para configurar o projeto em uma máquina nova.

### Pré-requisitos

- **Docker e Docker Compose**: Instale via `sudo apt install docker.io docker-compose` (Linux).
- **Git**: Para clonar o repositório.
- **Conta Google Cloud**: Para o MCP Calendar (credenciais OAuth).
- **WhatsApp Business**: Para usar a Evolution API.

### 1. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd LifeOS-Agent
```

### 2. Instalar Dependências Locais (Opcional, para Desenvolvimento)

```bash
# Instalar mise (gerenciador de versões)
curl https://mise.run | sh
mise trust
mise install

# Instalar dependências Python
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Copie os arquivos de exemplo e edite com suas chaves:

```bash
cp .env.example .env
cp .env.evolution.example .env.evolution
cp .env.calendar.example .env.calendar
```

Edite cada arquivo:
- **`.env`**: Chaves principais (Google API, Evolution, etc.).
- **`.env.evolution`**: Configurações da Evolution API.
- **`.env.calendar`**: Configurações do MCP Calendar.

#### Setup do Google Calendar MCP

1. Acesse [Google Cloud Console](https://console.cloud.google.com).
2. Crie um projeto ou selecione existente.
3. Habilite a Google Calendar API.
4. Crie credenciais OAuth 2.0 (tipo "Desktop app").
5. Baixe o `gcp-oauth.keys.json` e coloque em `mcp-google-calendar/`.
6. Adicione seu email como usuário de teste.

### 4. Iniciar Todos os Serviços

```bash
docker compose up -d
```

Isso inicia:
- Evolution API (porta 8080)
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- MCP Google Calendar (porta 3001)
- LifeOS Agent (porta 8000 e 3002)

O banco SQLite é inicializado automaticamente pelo entrypoint do container.

### 5. Verificar Instalação

- **Logs**: `docker compose logs -f`
- **Status**: `docker ps`
- **Teste APIs**:
  - Evolution: http://localhost:8080
  - MCP Calendar: http://localhost:3001/health
  - Agent: http://localhost:8000/docs

### 6. Configurar WhatsApp

1. Acesse http://localhost:8080 e crie uma instância.
2. Conecte seu WhatsApp Business escaneando o QR code.
3. Configure o webhook para apontar para o LifeOS Agent (porta 3002).

## 📁 Estrutura do Projeto

```
├── docker-compose.yml          # Orquestração completa
├── Dockerfile.agent            # Build do container do agente
├── requirements.txt            # Dependências Python
├── init_db.py                  # Script de init do banco (local)
├── docker-entrypoint.sh        # Entrypoint do container (init banco)
├── scripts/
│   ├── start_agent.sh          # Script para iniciar agente local
│   └── configure_webhook.py    # Configuração do webhook
├── life_os_agent/              # Código principal
│   ├── __init__.py
│   ├── agent.py                # Agente principal
│   ├── context.py              # Contexto de execução
│   ├── webhook.py              # Handler de webhooks
│   ├── agents/                 # Agentes especializados
│   │   ├── orchestrator.py
│   │   ├── finance.py
│   │   ├── communicator.py
│   │   ├── transcriber.py
│   │   ├── strategist.py
│   │   └── calendar.py
│   ├── database/               # SQLite local
│   ├── model/                  # Modelos ML
│   └── tools/                  # Ferramentas específicas
├── mcp-google-calendar/        # MCP Server para Calendar
├── database/                   # Scripts de banco PostgreSQL
└── docs/                       # Documentação adicional
```

## 🔧 Variáveis de Ambiente

### `.env` - LifeOS Agent

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `EVOLUTION_API_URL` | URL da Evolution API | `http://evolution-api:8080` |
| `EVOLUTION_API_KEY` | Chave de autenticação | `B6D711FC...` |
| `EVOLUTION_API_INSTANCE` | Nome da instância WhatsApp | `LifeOs` |
| `WEBHOOK_PORT` | Porta do webhook | `3002` |
| `WEBHOOK_ALLOWED_NUMBER` | Número permitido | `5564999999999` |
| `POSTGRES_*` | Credenciais PostgreSQL | - |
| `DB_PATH` | Caminho SQLite | `/data/lifeos.db` |
| `GOOGLE_API_KEY` | API Key Gemini | `AIzaSy...` |
| `LIFEOS_MODEL_NAME` | Modelo IA | `gemini-2.5-flash` |
| `GOOGLE_CALENDAR_MCP_URL` | URL MCP Calendar | `http://mcp-google-calendar:3001` |

### `.env.evolution` - Evolution API

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SERVER_PORT` | Porta servidor | `8080` |
| `AUTHENTICATION_API_KEY` | Chave API (igual ao .env) | - |
| `DATABASE_CONNECTION_URI` | URI PostgreSQL | `postgresql://...` |
| `CACHE_REDIS_URI` | URI Redis | `redis://redis:6379/0` |

### `.env.calendar` - MCP Google Calendar

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `TRANSPORT` | Modo transporte | `http` |
| `PORT` | Porta MCP | `3001` |
| `GOOGLE_OAUTH_CREDENTIALS` | Caminho credenciais | `/app/gcp-oauth.keys.json` |

## 🛠️ Desenvolvimento e Troubleshooting

### Executar Localmente (Sem Docker)

```bash
# Instalar deps
pip install -r requirements.txt

# Init banco
python init_db.py

# Iniciar agente
./scripts/start_agent.sh
```

### Comandos Úteis

- **Parar serviços**: `docker compose down`
- **Rebuild**: `docker compose up --build -d`
- **Logs específicos**: `docker compose logs lifeos-agent`
- **Acessar container**: `docker exec -it lifeos_agent bash`

### Problemas Comuns

- **Erro de credenciais**: Verifique `.env` e `gcp-oauth.keys.json`.
- **Banco não inicializa**: Execute `docker exec lifeos_agent python -m life_os_agent.database.setup`.
- **WhatsApp não conecta**: Verifique instância na Evolution API.
- **MCP Calendar falha**: Reautentique OAuth no Google.

