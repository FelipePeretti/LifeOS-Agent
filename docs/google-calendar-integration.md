# 📅 Integração Google Calendar - LifeOS Agent

Este documento descreve como configurar e usar a integração do Google Calendar no LifeOS Agent.

## 📋 Visão Geral

O LifeOS Agent agora suporta gerenciamento de eventos do Google Calendar via WhatsApp. Os usuários podem:

- ✅ Criar eventos no calendário
- ✅ Listar eventos próximos
- ✅ Editar eventos existentes
- ✅ Remover eventos
- ✅ Verificar disponibilidade

## 🚀 Configuração Inicial

### 1. Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google Calendar API**:
   - Menu → APIs & Services → Library
   - Busque "Google Calendar API"
   - Clique em "Enable"

### 2. Configurar OAuth Consent Screen

1. Menu → APIs & Services → OAuth consent screen
2. Selecione "External" (ou "Internal" se for Google Workspace)
3. Preencha as informações:
   - **App name**: LifeOS Agent
   - **User support email**: seu email
   - **Developer contact**: seu email
4. Em "Scopes", adicione:
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/calendar`
5. Em "Test users", adicione os emails que vão testar

### 3. Criar Credenciais OAuth

1. Menu → APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth client ID"
3. **Application type**: Desktop app
4. **Name**: LifeOS Calendar
5. Clique "Create"
6. **Baixe o arquivo JSON** clicando no ícone de download
7. Renomeie para `gcp-oauth.keys.json`
8. Coloque na pasta `mcp-google-calendar/`

### 4. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo:
```bash
cp .env.calendar.example .env.calendar
```

O arquivo `.env.calendar` já vem configurado com os valores corretos para Docker.

### 5. Iniciar os Serviços

```bash
# Build e start de todos os serviços
docker-compose up -d --build

# Verificar se o MCP Calendar está rodando
docker-compose logs mcp-google-calendar

# Testar health check
curl http://localhost:3001/health
```

### 6. Autenticação Inicial

Na primeira vez, você precisa autenticar:

```bash
# Executar autenticação OAuth
docker-compose exec mcp-google-calendar npm run auth
```

Isso abrirá uma URL para você autenticar com sua conta Google.

## 🔧 Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        WhatsApp (Evolution API)                  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LifeOS Agent (Python)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Orchestrator│──│ CalendarAgent│──│ MCP Client (HTTP)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP (porta 3001)
┌─────────────────────────────────────────────────────────────────┐
│               MCP Google Calendar (Node.js)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Tools: list-calendars, list-events, create-event, etc.  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ OAuth 2.0
┌─────────────────────────────────────────────────────────────────┐
│                     Google Calendar API                          │
└─────────────────────────────────────────────────────────────────┘
```

## 📡 Tools Disponíveis no MCP

| Tool | Descrição |
|------|-----------|
| `list-calendars` | Lista todos os calendários do usuário |
| `list-events` | Lista eventos de um calendário |
| `get-event` | Obtém detalhes de um evento específico |
| `search-events` | Busca eventos por texto |
| `create-event` | Cria um novo evento |
| `update-event` | Atualiza um evento existente |
| `delete-event` | Remove um evento |
| `respond-to-event` | Responde a convite de evento |
| `get-freebusy` | Verifica disponibilidade |
| `get-current-time` | Obtém hora atual |
| `list-colors` | Lista cores disponíveis para eventos |
| `manage-accounts` | Gerencia múltiplas contas |

## 🔒 Segurança

- Os tokens OAuth são armazenados em volume Docker persistente
- As credenciais nunca são expostas externamente
- O MCP roda em modo HTTP apenas na rede Docker interna
- Cada usuário precisa autorizar seu próprio calendário

## 🐛 Troubleshooting

### Erro "OAuth credentials not found"
```bash
# Verifique se o arquivo existe e tem permissões corretas
ls -la mcp-google-calendar/gcp-oauth.keys.json
chmod 644 mcp-google-calendar/gcp-oauth.keys.json
```

### Erro "Token expired"
```bash
# Re-autentique
docker-compose exec mcp-google-calendar npm run auth
```

### Health check falha
```bash
# Verifique os logs
docker-compose logs mcp-google-calendar

# Reinicie o serviço
docker-compose restart mcp-google-calendar
```

## 📚 Referências

- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [MCP Google Calendar GitHub](https://github.com/nspady/google-calendar-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
