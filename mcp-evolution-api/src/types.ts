export interface ApiInfo {
  status: number;
  message: string;
  version: string;
  swagger?: string;
  manager?: string;
  documentation?: string;
}

export interface InstanceStatus {
  state: string;
  status: string;
  qrcode?: string;
  message?: string;
}

export interface SendTextMessageRequest {
  number: string;
  text: string;
  options?: MessageOptions;
}

export interface MessageOptions {
  delay?: number;
  presence?: "composing" | "recording" | "paused";
  quotedMessageId?: string;
  mentionedList?: string[];
}

export interface SendTextMessageResponse {
  key: {
    id: string;
    remoteJid: string;
    fromMe: boolean;
  };
  message: {
    conversation: string;
  };
  messageTimestamp: number;
  status: string;
}

export interface CheckNumberRequest {
  phone: string;
}

export interface CheckNumberResponse {
  numbers: Array<{
    jid: string;
    exists: boolean;
    phone: string;
  }>;
}

export interface Contact {
  id: string;
  name?: string;
  pushname?: string;
  shortName?: string;
  isMe?: boolean;
  isGroup?: boolean;
}

export interface Chat {
  id: string;
  name?: string;
  lastMessage?: {
    text?: string;
    timestamp?: number;
  };
  unreadCount?: number;
  isGroup?: boolean;
}

export interface SendTemplateRequest {
  number: string;
  template: {
    namespace: string;
    name: string;
    language: {
      code: string;
    };
    components: TemplateComponent[];
  };
  options?: MessageOptions;
}

export interface TemplateComponent {
  type: "header" | "body" | "button" | "footer";
  parameters?: TemplateParameter[];
}

export interface TemplateParameter {
  type: "text" | "image" | "document" | "video";
  text?: string;
  image?: { link: string };
  document?: { link: string; filename: string };
  video?: { link: string };
}

export interface SendMediaRequest {
  number: string;
  media: {
    url: string;
    caption?: string;
    fileName?: string;
    mediaType?: "image" | "document" | "video" | "audio";
  };
  options?: MessageOptions;
}

export interface SendAudioRequest {
  number: string;
  audio: {
    url: string;
    ptt?: boolean;
  };
  options?: MessageOptions;
}

export interface SendStickerRequest {
  number: string;
  sticker: {
    url: string;
  };
  options?: MessageOptions;
}

export interface SendLocationRequest {
  number: string;
  location: {
    lat: number;
    lng: number;
    title?: string;
    address?: string;
  };
  options?: MessageOptions;
}

export interface SendContactRequest {
  number: string;
  contact: {
    fullName: string;
    wuid: string;
    phoneNumber: string;
  };
  options?: MessageOptions;
}

export interface SendReactionRequest {
  reactionMessage: {
    key: {
      id: string;
      remoteJid: string;
    };
    reaction: string;
  };
}

export interface SendPollRequest {
  number: string;
  poll: {
    name: string;
    options: string[];
    multipleChoice?: boolean;
  };
  options?: MessageOptions;
}

export interface SendListRequest {
  number: string;
  list: {
    title: string;
    description: string;
    buttonText: string;
    sections: ListSection[];
  };
  options?: MessageOptions;
}

export interface ListSection {
  title: string;
  rows: ListRow[];
}

export interface ListRow {
  id: string;
  title: string;
  description?: string;
}

export interface SendStatusRequest {
  status: {
    type: "text" | "image" | "video" | "audio";
    content: string;
    caption?: string;
    options?: {
      backgroundColor?: string;
      font?: number;
    };
  };
}

export interface ProfileInfo {
  name?: string;
  status?: string;
  picUrl?: string;
  business?: {
    description?: string;
    email?: string;
    websites?: string[];
    categories?: string[];
  };
}

export interface UpdateProfileRequest {
  name?: string;
  status?: string;
}

export interface PrivacySettings {
  readreceipts: "all" | "contacts" | "none";
  profile: "all" | "contacts" | "none";
  status: "all" | "contacts" | "none";
  online: "all" | "contacts" | "none";
  last: "all" | "contacts" | "none";
  groupadd: "all" | "contacts" | "none";
}

export interface CreateGroupRequest {
  subject: string;
  participants: string[];
  description?: string;
  picture?: string;
}

export interface GroupInfo {
  id: string;
  subject: string;
  description?: string;
  owner?: string;
  participants: GroupParticipant[];
  creation?: number;
  ephemeralDuration?: number;
}

export interface GroupParticipant {
  id: string;
  admin?: "admin" | "superadmin" | null;
  isSuperAdmin?: boolean;
}

export interface GroupUpdateRequest {
  groupJid: string;
  action: "add" | "remove" | "promote" | "demote";
  participants: string[];
}

export interface GroupSettingRequest {
  groupJid: string;
  setting: "announcement" | "locked" | "unlocked";
}

export interface WebhookConfig {
  url: string;
  enabled: boolean;
  events?: WebhookEvent[];
  webhook_by_events?: boolean;
  webhook_base64?: boolean;
}

export type WebhookEvent =
  | "messages.upsert"
  | "messages.update"
  | "messages.delete"
  | "send.message"
  | "connection.update"
  | "qrcode.updated"
  | "presence.update"
  | "groups.upsert"
  | "groups.update"
  | "chats.upsert"
  | "chats.update"
  | "chats.delete"
  | "contacts.upsert"
  | "contacts.update"

  | "message"
  | "message.ack"
  | "qr"
  | "group.update";

export interface ChatwootConfig {
  enabled: boolean;
  account_id: string;
  token: string;
  endpoint: string;
  instance_name?: string;
  sign_msg?: boolean;
  name_inbox?: string;
}

export interface TypebotConfig {
  enabled: boolean;
  url: string;
  typebot: string;
  expire?: number;
  keyword_finish?: string[];
  delay_message?: number;
  unknown_message?: string;
  listening_from_me?: boolean;
}

export interface InstanceConfig {
  instanceName: string;
  webhook?: WebhookConfig;
  settings?: {
    reject_call?: boolean;
    msg_call?: string;
    groups_ignore?: boolean;
    always_online?: boolean;
    read_messages?: boolean;
    read_status?: boolean;
  };
}