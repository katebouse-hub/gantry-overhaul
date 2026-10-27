import { Mastra } from "@mastra/core/mastra";
import { PinoLogger } from "@mastra/loggers";
import { LibSQLStore } from "@mastra/libsql";
import { chatRoute } from "@mastra/ai-sdk";
import { gpt120 } from "./agents/gpt120.ts";
import { gpt20 } from "./agents/gpt20.ts";
import { gemma4_31b } from "./agents/gemma4_31b.ts";
import { gemma4_26b } from "./agents/gemma4_26b.ts";
import { gemma4_e4b } from "./agents/gemma4_e4b.ts";
import { qwen3_35b } from "./agents/qwen3_35b.ts";
import { qwen36_35b } from "./agents/qwen3.6_35b.ts";
import { testMcpServer } from "./mcp/test-mcp-server";
import { gantryAgent } from "./agents/gantry_agent";
import { Observability, DefaultExporter } from "@mastra/observability";

export const mastra = new Mastra({
  storage: new LibSQLStore({
    id: "mastra-storage",
    url: "file:./mastra.db",
  }),
  server: {
    host: "0.0.0.0",
    apiRoutes: [
      chatRoute({
        path: "/chat/:agentId",
        version: "v6",
      }),
    ],
  },
  mcpServers: { testMcpServer },
  agents: {
    gpt120,
    gpt20,
    gemma4_31b,
    gemma4_26b,
    gemma4_e4b,
    qwen3_35b,
    qwen36_35b,
    gantryAgent,
  },
  logger: new PinoLogger({
    name: "Mastra",
    level: "info",
  }),
  observability: new Observability({
    configs: {
      default: {
        serviceName: "mastra",
        exporters: [new DefaultExporter()],
      },
    },
  }),
});
