export const config = {
  evolutionApi: {
    baseUrl: process.env.EVOLUTION_API_URL || "https://seu-servidor-evolution-api.com",
    apiKey: process.env.EVOLUTION_API_KEY || "sua-chave-api",
    instanceId: process.env.EVOLUTION_API_INSTANCE || "instancia-padrao"
  },
  mcp: {
    name: "Evolution API Server",
    version: "1.0.0"
  }
};  