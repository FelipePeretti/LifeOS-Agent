import * as http from "http";
import { messageStore } from "./messageStore.js";

let webhookServer: http.Server | null = null;

export interface WebhookServerConfig {
  port: number;
  path?: string;
}

export function startWebhookServer(config: WebhookServerConfig): Promise<http.Server> {
  return new Promise((resolve, reject) => {
    const { port, path = "/webhook" } = config;

    if (webhookServer) {
      console.error("[WebhookServer] Servidor já está rodando");
      resolve(webhookServer);
      return;
    }

    webhookServer = http.createServer((req, res) => {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "Content-Type");

      if (req.method === "OPTIONS") {
        res.writeHead(204);
        res.end();
        return;
      }

      if (req.method !== "POST" || !req.url?.startsWith(path)) {
        res.writeHead(404, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Not found" }));
        return;
      }

      let body = "";

      req.on("data", (chunk) => {
        body += chunk.toString();
      });

      req.on("end", () => {
        try {
          const data = JSON.parse(body);
          const event = data.event || "unknown";

          console.error(`[WebhookServer] Evento recebido: ${event}`);

          if (event === "messages.upsert" || event === "message") {
            messageStore.add(event, data.data || data);
          } else if (event === "messages.update" || event === "message.ack") {
            messageStore.add(event, data.data || data);
          } else {
            messageStore.add(event, data.data || data);
          }

          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ success: true, event }));
        } catch (error) {
          console.error("[WebhookServer] Erro ao processar webhook:", error);
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Invalid JSON" }));
        }
      });
    });

    webhookServer.on("error", (error) => {
      console.error("[WebhookServer] Erro no servidor:", error);
      reject(error);
    });

    webhookServer.listen(port, () => {
      console.error(`[WebhookServer] Servidor webhook rodando em http://localhost:${port}${path}`);
      resolve(webhookServer!);
    });
  });
}

export function stopWebhookServer(): Promise<void> {
  return new Promise((resolve) => {
    if (webhookServer) {
      webhookServer.close(() => {
        console.error("[WebhookServer] Servidor parado");
        webhookServer = null;
        resolve();
      });
    } else {
      resolve();
    }
  });
}

export function isWebhookServerRunning(): boolean {
  return webhookServer !== null;
}

export function getWebhookUrl(port: number, path: string = "/webhook"): string {
  return `http://localhost:${port}${path}`;
}
