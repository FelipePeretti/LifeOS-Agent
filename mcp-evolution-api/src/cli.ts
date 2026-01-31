#!/usr/bin/env node

import { startServer } from "./index.js";
import { config } from "./config.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.error(`
╔════════════════════════════════════════════════════╗
║            MCP SERVER PARA EVOLUTION API           ║
╠════════════════════════════════════════════════════╣
║ Versão: ${config.mcp.version}                             ║
║ Instância: ${config.evolutionApi.instanceId}        ║
╚════════════════════════════════════════════════════╝
`);

const enableWebSocket = process.env.ENABLE_WEBSOCKET === "true";

async function init() {
  try {
    await startServer();

    if (enableWebSocket) {
      const port = process.env.PORT || 3000;
    }
  } catch (error) {
    console.error("Erro ao iniciar servidores MCP:", error);
    process.exit(1);
  }
}

init();
