const ALLOWED_NUMBER = process.env.WEBHOOK_ALLOWED_NUMBER;

export interface IncomingMessage {
  id: string;
  event: string;
  timestamp: Date;
  data: {
    remoteJid: string;
    fromMe: boolean;
    pushName?: string;
    message?: {
      conversation?: string;
      extendedTextMessage?: { text: string };
      imageMessage?: { caption?: string };
      videoMessage?: { caption?: string };
      audioMessage?: any;
      documentMessage?: { fileName?: string };
    };
    messageType?: string;
    messageTimestamp?: number;
  };
  raw: any;
}

class MessageStore {
  private messages: IncomingMessage[] = [];
  private maxMessages: number = 100;

  add(event: string, data: any): void {
    const remoteJid = data?.key?.remoteJid || data?.remoteJid || 'unknown';
    const numberFromJid = remoteJid.replace('@s.whatsapp.net', '').replace('@g.us', '');
    
    if (ALLOWED_NUMBER && !numberFromJid.includes(ALLOWED_NUMBER)) {
      console.error(`[WebhookStore] Mensagem ignorada de ${numberFromJid} (permitido apenas: ${ALLOWED_NUMBER})`);
      return;
    }

    const message: IncomingMessage = {
      id: data?.key?.id || `${Date.now()}`,
      event,
      timestamp: new Date(),
      data: {
        remoteJid,
        fromMe: data?.key?.fromMe || false,
        pushName: data?.pushName,
        message: data?.message,
        messageType: data?.messageType,
        messageTimestamp: data?.messageTimestamp
      },
      raw: data
    };

    this.messages.unshift(message);

    if (this.messages.length > this.maxMessages) {
      this.messages = this.messages.slice(0, this.maxMessages);
    }

    console.error(`[WebhookStore] ✅ Mensagem aceita: ${event}`);
  }

  getRecent(limit: number = 10, fromNumber?: string): IncomingMessage[] {
    let filtered = this.messages;

    if (fromNumber) {
      filtered = filtered.filter(m => 
        m.data.remoteJid.includes(fromNumber) || 
        m.data.remoteJid.replace('@s.whatsapp.net', '').includes(fromNumber)
      );
    }

    return filtered.slice(0, limit);
  }

  getUnread(limit: number = 10): IncomingMessage[] {
    return this.messages
      .filter(m => !m.data.fromMe && m.event === 'messages.upsert')
      .slice(0, limit);
  }

  clear(): void {
    this.messages = [];
  }

  count(): number {
    return this.messages.length;
  }

  static extractText(message: IncomingMessage): string {
    const msg = message.data.message;
    if (!msg) return '[Mensagem sem conteúdo]';

    if (msg.conversation) return msg.conversation;
    if (msg.extendedTextMessage?.text) return msg.extendedTextMessage.text;
    if (msg.imageMessage?.caption) return `[Imagem] ${msg.imageMessage.caption}`;
    if (msg.videoMessage?.caption) return `[Vídeo] ${msg.videoMessage.caption}`;
    if (msg.audioMessage) return '[Áudio]';
    if (msg.documentMessage) return `[Documento] ${msg.documentMessage.fileName || ''}`;

    return `[${message.data.messageType || 'Tipo desconhecido'}]`;
  }

  static formatNumber(remoteJid: string): string {
    return remoteJid.replace('@s.whatsapp.net', '').replace('@g.us', ' (grupo)');
  }
}

export const messageStore = new MessageStore();
