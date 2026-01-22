import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { config } from "./config.js";
import { EvolutionApiService } from "./services/evolutionApiService.js";
import { 
  messageStore, 
  startWebhookServer, 
  stopWebhookServer, 
  isWebhookServerRunning,
  getWebhookUrl 
} from "./webhook/index.js";
import "dotenv/config";

const WEBHOOK_PORT = parseInt(process.env.WEBHOOK_PORT || "3001");
const evolutionService = new EvolutionApiService();

const server = new McpServer({
  name: config.mcp.name,
  version: config.mcp.version
});

// ===== FERRAMENTAS PARA INFORMAÇÕES GERAIS =====

// Verificar o status da API
server.tool("getApiStatus",
  {},
  async () => {
    try {
      const apiInfo = await evolutionService.getApiInfo();
      return {
        content: [{ 
          type: "text", 
          text: `Evolution API v${apiInfo.version} está rodando. Status: ${apiInfo.status}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao conectar à Evolution API: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// ===== FERRAMENTAS PARA GESTÃO DE INSTÂNCIAS =====

// Verificar status da instância
server.tool("getInstanceStatus",
  {},
  async () => {
    try {
      const status = await evolutionService.getInstanceStatus();
      return {
        content: [{ 
          type: "text", 
          text: `Status da instância: ${status.state || "Desconhecido"}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao verificar status da instância: ${(error as Error).message}` 
        }]
      };
    }
  }
);

/*
// Definir presença
server.tool("setPresence",
  { 
    presence: z.enum(["available", "unavailable", "composing", "recording", "paused"])
      .describe("Status de presença para definir")
  },
  async ({ presence }) => {
    try {
      await evolutionService.setPresence(presence);
      return {
        content: [{ 
          type: "text", 
          text: `Presença definida como "${presence}" com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao definir presença: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Logout da instância
server.tool("logoutInstance",
  {},
  async () => {
    try {
      await evolutionService.logout();
      return {
        content: [{ 
          type: "text", 
          text: "Instância desconectada com sucesso." 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao desconectar instância: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Reiniciar a instância
server.tool("restartInstance",
  {},
  async () => {
    try {
      await evolutionService.restartInstance();
      return {
        content: [{ 
          type: "text", 
          text: "Instância reiniciada com sucesso." 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao reiniciar instância: ${(error as Error).message}` 
        }]
      };
    }
  }
);
*/

// ===== FERRAMENTAS PARA MENSAGENS =====

// Enviar mensagem de texto
server.tool("sendTextMessage",
  { 
    number: z.string().min(1).describe("Número do destinatário no formato internacional (ex: 5511999999999)"),
    text: z.string().min(1).describe("Texto da mensagem a ser enviada"),
    options: z.object({
      delay: z.number().optional().describe("Atraso em milissegundos"),
      presence: z.enum(["composing", "recording", "paused"]).optional().describe("Presença a mostrar"),
      quotedMessageId: z.string().optional().describe("ID da mensagem a ser citada")
    }).optional().describe("Opções adicionais para o envio")
  },
  async ({ number, text, options }) => {
    try {
      const result = await evolutionService.sendTextMessage({ number, text, options });
      return {
        content: [{ 
          type: "text", 
          text: `Mensagem enviada com sucesso: ${result?.key?.id || "ID não disponível"}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao enviar mensagem: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Enviar mídia
server.tool("sendMedia",
  { 
    number: z.string().min(1).describe("Número do destinatário no formato internacional"),
    url: z.string().url().describe("URL da mídia a ser enviada"),
    caption: z.string().optional().describe("Legenda para a mídia"),
    fileName: z.string().optional().describe("Nome do arquivo"),
    mediaType: z.enum(["image", "document", "video", "audio"]).describe("Tipo de mídia")
  },
  async ({ number, url, caption, fileName, mediaType }) => {
    try {
      const result = await evolutionService.sendMedia({
        number,
        media: { url, caption, fileName, mediaType }
      });
      return {
        content: [{ 
          type: "text", 
          text: `Mídia enviada com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao enviar mídia: ${(error as Error).message}` 
        }]
      };
    }
  }
);

/*
// Enviar áudio
server.tool("sendAudio",
  { 
    number: z.string().min(1).describe("Número do destinatário no formato internacional"),
    url: z.string().url().describe("URL do áudio a ser enviado"),
    ptt: z.boolean().optional().describe("Se é uma mensagem de voz (Push-to-talk)")
  },
  async ({ number, url, ptt }) => {
    try {
      await evolutionService.sendAudio({
        number,
        audio: { url, ptt }
      });
      return {
        content: [{ 
          type: "text", 
          text: `Áudio enviado com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao enviar áudio: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Enviar sticker
server.tool("sendSticker",
  { 
    number: z.string().min(1).describe("Número do destinatário no formato internacional"),
    url: z.string().url().describe("URL do sticker a ser enviado")
  },
  async ({ number, url }) => {
    try {
      await evolutionService.sendSticker({
        number,
        sticker: { url }
      });
      return {
        content: [{ 
          type: "text", 
          text: `Sticker enviado com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao enviar sticker: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Enviar localização
server.tool("sendLocation",
  { 
    number: z.string().min(1).describe("Número do destinatário no formato internacional"),
    lat: z.number().describe("Latitude"),
    lng: z.number().describe("Longitude"),
    title: z.string().optional().describe("Título da localização"),
    address: z.string().optional().describe("Endereço da localização")
  },
  async ({ number, lat, lng, title, address }) => {
    try {
      await evolutionService.sendLocation({
        number,
        location: { lat, lng, title, address }
      });
      return {
        content: [{ 
          type: "text", 
          text: `Localização enviada com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao enviar localização: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Enviar contato
server.tool("sendContact",
  { 
    number: z.string().min(1).describe("Número do destinatário no formato internacional"),
    fullName: z.string().min(1).describe("Nome completo do contato"),
    wuid: z.string().min(1).describe("ID do WhatsApp do contato"),
    phoneNumber: z.string().min(1).describe("Número de telefone do contato")
  },
  async ({ number, fullName, wuid, phoneNumber }) => {
    try {
      await evolutionService.sendContact({
        number,
        contact: { fullName, wuid, phoneNumber }
      });
      return {
        content: [{ 
          type: "text", 
          text: `Contato enviado com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao enviar contato: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Enviar enquete
server.tool("sendPoll",
  { 
    number: z.string().min(1).describe("Número do destinatário no formato internacional"),
    name: z.string().min(1).describe("Pergunta da enquete"),
    options: z.array(z.string()).min(2).describe("Opções de resposta"),
    multipleChoice: z.boolean().optional().describe("Permite múltiplas escolhas")
  },
  async ({ number, name, options, multipleChoice }) => {
    try {
      await evolutionService.sendPoll({
        number,
        poll: { name, options, multipleChoice }
      });
      return {
        content: [{ 
          type: "text", 
          text: `Enquete enviada com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao enviar enquete: ${(error as Error).message}` 
        }]
      };
    }
  }
);
*/

// ===== FERRAMENTAS PARA GESTÃO DE CHAT =====

// Verificar número de WhatsApp
server.tool("checkWhatsAppNumber",
  { 
    phone: z.string().min(1).describe("Número a ser verificado no formato internacional (ex: 5511999999999)")
  },
  async ({ phone }) => {
    try {
      const result = await evolutionService.checkWhatsAppNumber({ phone });
      const isWhatsApp = result?.numbers?.[0]?.exists || false;
      return {
        content: [{ 
          type: "text", 
          text: isWhatsApp 
            ? `O número ${phone} é um número de WhatsApp válido.` 
            : `O número ${phone} não é um número de WhatsApp válido.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao verificar número: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Marcar mensagem como lida
server.tool("markMessageAsRead",
  { 
    messageId: z.string().min(1).describe("ID da mensagem a ser marcada como lida")
  },
  async ({ messageId }) => {
    try {
      await evolutionService.markMessageAsRead(messageId);
      return {
        content: [{ 
          type: "text", 
          text: `Mensagem marcada como lida com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao marcar mensagem como lida: ${(error as Error).message}` 
        }]
      };
    }
  }
);

/*
// Arquivar chat
server.tool("archiveChat",
  { 
    number: z.string().min(1).describe("Número no formato internacional"),
    shouldArchive: z.boolean().default(true).describe("True para arquivar, false para desarquivar")
  },
  async ({ number, shouldArchive }) => {
    try {
      await evolutionService.archiveChat(number);
      return {
        content: [{ 
          type: "text", 
          text: shouldArchive 
            ? `Chat arquivado com sucesso.` 
            : `Chat desarquivado com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao ${shouldArchive ? 'arquivar' : 'desarquivar'} chat: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Excluir mensagem para todos
server.tool("deleteMessageForEveryone",
  { 
    messageId: z.string().min(1).describe("ID da mensagem a ser excluída")
  },
  async ({ messageId }) => {
    try {
      await evolutionService.deleteMessageForEveryone(messageId);
      return {
        content: [{ 
          type: "text", 
          text: `Mensagem excluída para todos com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao excluir mensagem: ${(error as Error).message}` 
        }]
      };
    }
  }
);
*/

// ===== FERRAMENTAS DE PERFIL =====

/*
// Atualizar nome do perfil
server.tool("updateProfileName",
  { 
    name: z.string().min(1).describe("Novo nome para o perfil")
  },
  async ({ name }) => {
    try {
      await evolutionService.updateProfileName(name);
      return {
        content: [{ 
          type: "text", 
          text: `Nome do perfil atualizado para "${name}" com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao atualizar nome do perfil: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Atualizar status do perfil
server.tool("updateProfileStatus",
  { 
    status: z.string().min(1).describe("Novo status para o perfil")
  },
  async ({ status }) => {
    try {
      await evolutionService.updateProfileStatus(status);
      return {
        content: [{ 
          type: "text", 
          text: `Status do perfil atualizado para "${status}" com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao atualizar status do perfil: ${(error as Error).message}` 
        }]
      };
    }
  }
);
*/

// ===== FERRAMENTAS DE GRUPO =====

/*
// Criar grupo
server.tool("createGroup",
  { 
    subject: z.string().min(1).describe("Nome do grupo"),
    participants: z.array(z.string()).min(1).describe("Lista de números de participantes"),
    description: z.string().optional().describe("Descrição do grupo")
  },
  async ({ subject, participants, description }) => {
    try {
      const result = await evolutionService.createGroup({
        subject,
        participants,
        description
      });
      return {
        content: [{ 
          type: "text", 
          text: `Grupo "${subject}" criado com sucesso. ID: ${result.groupId}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao criar grupo: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Adicionar participantes ao grupo
server.tool("addGroupParticipants",
  { 
    groupId: z.string().min(1).describe("ID do grupo"),
    participants: z.array(z.string()).min(1).describe("Lista de números de participantes")
  },
  async ({ groupId, participants }) => {
    try {
      await evolutionService.updateGroupMembers({
        groupJid: groupId,
        action: "add",
        participants
      });
      return {
        content: [{ 
          type: "text", 
          text: `${participants.length} participante(s) adicionado(s) ao grupo com sucesso.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao adicionar participantes: ${(error as Error).message}` 
        }]
      };
    }
  }
);
*/

// ===== FERRAMENTAS DE WEBHOOK =====

// Iniciar o servidor de webhook local
server.tool("startWebhookListener",
  { 
    port: z.number().optional().describe("Porta para o servidor de webhook (padrão: 3001)")
  },
  async ({ port }) => {
    try {
      const webhookPort = port || WEBHOOK_PORT;
      
      if (isWebhookServerRunning()) {
        return {
          content: [{ 
            type: "text", 
            text: `Servidor de webhook já está rodando na porta ${webhookPort}` 
          }]
        };
      }

      await startWebhookServer({ port: webhookPort, path: "/webhook" });
      
      return {
        content: [{ 
          type: "text", 
          text: `Servidor de webhook iniciado em http://localhost:${webhookPort}/webhook\n\nAgora configure o webhook na Evolution API usando a ferramenta configureEvolutionWebhook.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao iniciar servidor de webhook: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Parar o servidor de webhook
server.tool("stopWebhookListener",
  {},
  async () => {
    try {
      if (!isWebhookServerRunning()) {
        return {
          content: [{ 
            type: "text", 
            text: "Servidor de webhook não está rodando." 
          }]
        };
      }

      await stopWebhookServer();
      
      return {
        content: [{ 
          type: "text", 
          text: "Servidor de webhook parado com sucesso." 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao parar servidor de webhook: ${(error as Error).message}` 
        }]
      };
    }
  }
);

/*
// Configurar o webhook na Evolution API
server.tool("configureEvolutionWebhook",
  { 
    webhookUrl: z.string().url().describe("URL do webhook (ex: http://seu-servidor:3001/webhook)"),
    enabled: z.boolean().default(true).describe("Habilitar ou desabilitar o webhook"),
    events: z.array(z.enum([
      "messages.upsert",
      "messages.update", 
      "messages.delete",
      "send.message",
      "connection.update",
      "qrcode.updated",
      "presence.update",
      "groups.upsert",
      "groups.update",
      "chats.upsert",
      "chats.update",
      "chats.delete",
      "contacts.upsert",
      "contacts.update"
    ])).optional().describe("Eventos para escutar (padrão: todos)")
  },
  async ({ webhookUrl, enabled, events }) => {
    try {
      const webhookConfig = {
        url: webhookUrl,
        enabled,
        events: events || [
          "messages.upsert",
          "messages.update",
          "send.message",
          "connection.update"
        ],
        webhook_by_events: false,
        webhook_base64: false
      };

      await evolutionService.setWebhook(webhookConfig);
      
      return {
        content: [{ 
          type: "text", 
          text: `Webhook configurado com sucesso!\n\nURL: ${webhookUrl}\nAtivo: ${enabled}\nEventos: ${(webhookConfig.events as string[]).join(", ")}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao configurar webhook: ${(error as Error).message}` 
        }]
      };
    }
  }
);
*/

// Obter configuração atual do webhook
server.tool("getWebhookConfig",
  {},
  async () => {
    try {
      const config = await evolutionService.getWebhook();
      
      return {
        content: [{ 
          type: "text", 
          text: `Configuração atual do webhook:\n\nURL: ${config?.url || "Não configurado"}\nAtivo: ${config?.enabled || false}\nEventos: ${config?.events?.join(", ") || "Nenhum"}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao buscar configuração do webhook: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Buscar mensagens recebidas
server.tool("getIncomingMessages",
  { 
    limit: z.number().min(1).max(50).default(10).describe("Número máximo de mensagens a retornar"),
    fromNumber: z.string().optional().describe("Filtrar por número de telefone")
  },
  async ({ limit, fromNumber }) => {
    try {
      const messages = messageStore.getRecent(limit, fromNumber);
      
      if (messages.length === 0) {
        return {
          content: [{ 
            type: "text", 
            text: "Nenhuma mensagem recebida ainda.\n\nCertifique-se de que:\n1. O servidor de webhook está rodando (startWebhookListener)\n2. O webhook está configurado na Evolution API (configureEvolutionWebhook)" 
          }]
        };
      }

      const formattedMessages = messages.map((msg, i) => {
        const number = msg.data.remoteJid.replace("@s.whatsapp.net", "").replace("@g.us", " (grupo)");
        const text = extractMessageText(msg);
        const time = msg.timestamp.toLocaleTimeString("pt-BR");
        const direction = msg.data.fromMe ? "→ Enviada" : "← Recebida";
        
        return `${i + 1}. [${time}] ${direction} - ${number}\n   ${text}`;
      }).join("\n\n");

      return {
        content: [{ 
          type: "text", 
          text: `📬 Mensagens recentes (${messages.length}):\n\n${formattedMessages}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao buscar mensagens: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Extrair texto da mensagem
function extractMessageText(message: any): string {
  const msg = message.data?.message;
  if (!msg) return "[Mensagem sem conteúdo]";

  if (msg.conversation) return msg.conversation;
  if (msg.extendedTextMessage?.text) return msg.extendedTextMessage.text;
  if (msg.imageMessage?.caption) return `[Imagem] ${msg.imageMessage.caption}`;
  if (msg.imageMessage) return "[Imagem]";
  if (msg.videoMessage?.caption) return `[Vídeo] ${msg.videoMessage.caption}`;
  if (msg.videoMessage) return "[Vídeo]";
  if (msg.audioMessage) return "[Áudio]";
  if (msg.documentMessage) return `[Documento] ${msg.documentMessage.fileName || ""}`;
  if (msg.stickerMessage) return "[Sticker]";
  if (msg.locationMessage) return "[Localização]";
  if (msg.contactMessage) return "[Contato]";
  if (msg.pollCreationMessage) return `[Enquete] ${msg.pollCreationMessage.name || ""}`;

  return `[${message.data?.messageType || "Tipo desconhecido"}]`;
}

// Buscar apenas mensagens não lidas
server.tool("getUnreadMessages",
  { 
    limit: z.number().min(1).max(50).default(10).describe("Número máximo de mensagens")
  },
  async ({ limit }) => {
    try {
      const messages = messageStore.getUnread(limit);
      
      if (messages.length === 0) {
        return {
          content: [{ 
            type: "text", 
            text: "Nenhuma mensagem recebida de outros usuários." 
          }]
        };
      }

      const formattedMessages = messages.map((msg, i) => {
        const number = msg.data.remoteJid.replace("@s.whatsapp.net", "").replace("@g.us", " (grupo)");
        const text = extractMessageText(msg);
        const time = msg.timestamp.toLocaleTimeString("pt-BR");
        const name = msg.data.pushName || "Desconhecido";
        
        return `${i + 1}. [${time}] ${name} (${number})\n   ${text}`;
      }).join("\n\n");

      return {
        content: [{ 
          type: "text", 
          text: `📨 Mensagens recebidas (${messages.length}):\n\n${formattedMessages}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao buscar mensagens: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Limpar mensagens armazenadas
server.tool("clearStoredMessages",
  {},
  async () => {
    try {
      const count = messageStore.count();
      messageStore.clear();
      
      return {
        content: [{ 
          type: "text", 
          text: `${count} mensagens removidas do armazenamento.` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao limpar mensagens: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// Verificar status do webhook
server.tool("getWebhookStatus",
  {},
  async () => {
    try {
      const isRunning = isWebhookServerRunning();
      const messageCount = messageStore.count();
      
      let status = `📡 Status do Webhook:\n\n`;
      status += `Servidor local: ${isRunning ? "✅ Rodando" : "❌ Parado"}\n`;
      status += `Mensagens armazenadas: ${messageCount}\n`;
      
      if (isRunning) {
        status += `URL do webhook: http://localhost:${WEBHOOK_PORT}/webhook`;
      }
      
      return {
        content: [{ 
          type: "text", 
          text: status 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Erro ao verificar status: ${(error as Error).message}` 
        }]
      };
    }
  }
);

// ===== RECURSOS PARA CONSULTAR INFORMAÇÕES =====

// Visualizar contatos
server.resource(
  "contacts",
  new ResourceTemplate("contacts://list", { list: undefined }),
  async (uri) => {
    try {
      const contactsData = await evolutionService.fetchContacts();
      const contacts = contactsData?.data || [];
      
      return {
        contents: [{
          uri: uri.href,
          text: `Contatos disponíveis (${contacts.length}):\n${contacts
            .map((contact: any) => `- ${contact.name || "Sem nome"}: ${contact.id.replace("@c.us", "")}`)
            .join("\n")}`
        }]
      };
    } catch (error) {
      return {
        contents: [{
          uri: uri.href,
          text: `Erro ao buscar contatos: ${(error as Error).message}`
        }]
      };
    }
  }
);

// Visualizar conversas
server.resource(
  "chats",
  new ResourceTemplate("chats://list", { list: undefined }),
  async (uri) => {
    try {
      const chatsData = await evolutionService.fetchChats();
      const chats = chatsData?.data || [];
      
      return {
        contents: [{
          uri: uri.href,
          text: `Conversas disponíveis (${chats.length}):\n${chats
            .map((chat: any) => `- ${chat.name || chat.id || "Chat sem nome"}`)
            .join("\n")}`
        }]
      };
    } catch (error) {
      return {
        contents: [{
          uri: uri.href,
          text: `Erro ao buscar conversas: ${(error as Error).message}`
        }]
      };
    }
  }
);

// Visualizar grupos
server.resource(
  "groups",
  new ResourceTemplate("groups://list", { list: undefined }),
  async (uri) => {
    try {
      const groupsData = await evolutionService.fetchAllGroups();
      const groups = groupsData?.data || [];
      
      return {
        contents: [{
          uri: uri.href,
          text: `Grupos disponíveis (${groups.length}):\n${groups
            .map((group: any) => `- ${group.subject || group.id || "Grupo sem nome"} (${group.participants?.length || 0} membros)`)
            .join("\n")}`
        }]
      };
    } catch (error) {
      return {
        contents: [{
          uri: uri.href,
          text: `Erro ao buscar grupos: ${(error as Error).message}`
        }]
      };
    }
  }
);

// Visualizar detalhes do perfil
server.resource(
  "profile",
  new ResourceTemplate("profile://info", { list: undefined }),
  async (uri) => {
    try {
      const profile = await evolutionService.fetchProfile();
      
      return {
        contents: [{
          uri: uri.href,
          text: `Informações do perfil:\n- Nome: ${profile.name || "Não definido"}\n- Status: ${profile.status || "Não definido"}`
        }]
      };
    } catch (error) {
      return {
        contents: [{
          uri: uri.href,
          text: `Erro ao buscar informações do perfil: ${(error as Error).message}`
        }]
      };
    }
  }
);

// Visualizar configurações de privacidade
server.resource(
  "privacy",
  new ResourceTemplate("privacy://settings", { list: undefined }),
  async (uri) => {
    try {
      const privacy = await evolutionService.fetchPrivacySettings();
      
      return {
        contents: [{
          uri: uri.href,
          text: `Configurações de privacidade:\n- Confirmações de leitura: ${privacy.readreceipts}\n- Perfil: ${privacy.profile}\n- Status: ${privacy.status}\n- Online: ${privacy.online}\n- Último visto: ${privacy.last}\n- Adição a grupos: ${privacy.groupadd}`
        }]
      };
    } catch (error) {
      return {
        contents: [{
          uri: uri.href,
          text: `Erro ao buscar configurações de privacidade: ${(error as Error).message}`
        }]
      };
    }
  }
);

// ===== INICIALIZAÇÃO DO SERVIDOR =====

export async function startServer() {
  console.error("Iniciando servidor MCP para Evolution API via STDIO...");
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Servidor MCP STDIO iniciado com sucesso!");
    
    if (process.env.ENABLE_WEBHOOK === "true") {
      const webhookPort = parseInt(process.env.WEBHOOK_PORT || "3001");
      await startWebhookServer({ port: webhookPort, path: "/webhook" });
      console.error(`Servidor de webhook iniciado em http://localhost:${webhookPort}/webhook`);
    }
    
    return server;
  } catch (error) {
    console.error("Erro ao iniciar servidor MCP STDIO:", error);
    throw error;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  startServer().catch(console.error);
}
