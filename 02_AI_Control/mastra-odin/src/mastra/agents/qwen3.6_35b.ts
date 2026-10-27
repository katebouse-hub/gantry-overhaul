import { ollama } from "ollama-ai-provider-v2";
import { Agent } from "@mastra/core/agent";
import { testMcpClient } from "../mcp/test-mcp-client";

export const qwen36_35b = new Agent({
  id: "qwen36_35b",
  name: "qwen3.6:35b-a3b",
  description: "You are a helpful assistant.",
  instructions: `You are a helpful assistant that has access to the following MCP Servers.
      - Mastra Ai Documentation
      - Grep App Search Tool (Github)

      Answer questions using the information you find using the MCP Servers when appropriate.`,
  model: ollama("qwen3.6:35b-a3b"),
  tools: await testMcpClient.listTools(),
});
