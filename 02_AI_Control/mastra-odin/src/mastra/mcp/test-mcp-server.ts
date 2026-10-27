import { MCPServer } from "@mastra/mcp";

import { gpt120 } from "../agents/gpt120.ts";
import { gpt20 } from "../agents/gpt20.ts";
import { gemma4_31b } from "../agents/gemma4_31b.ts";
import { gemma4_26b } from "../agents/gemma4_26b.ts";
import { gemma4_e4b } from "../agents/gemma4_e4b.ts";
import { qwen3_35b } from "../agents/qwen3_35b.ts";
import { qwen36_35b } from "../agents/qwen3.6_35b.ts";

export const testMcpServer = new MCPServer({
  id: "test-mcp-server",
  name: "Test Server",
  version: "1.0.0",
  agents: {
    gpt120,
    gpt20,
    gemma4_31b,
    gemma4_26b,
    gemma4_e4b,
    qwen3_35b,
    qwen36_35b,
  },
  tools: {},
  workflows: {},
});
