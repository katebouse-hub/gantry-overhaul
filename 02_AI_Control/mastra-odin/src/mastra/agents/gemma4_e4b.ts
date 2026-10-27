import { ollama } from "ollama-ai-provider-v2";
import { Agent } from "@mastra/core/agent";
import { testMcpClient } from "../mcp/test-mcp-client";

export const gemma4_e4b = new Agent({
  id: "gemma4_e4b",
  name: "gemma4:e4b",
  description: "You are a helpful assistant.",
  instructions: `You are a helpful assistant that has access to the following MCP Servers.
      - Mastra Ai Documentation
      - Grep App Search Tool (Github)

      Answer questions using the information you find using the MCP Servers when appropriate.`,
  model: ollama("gemma4:e4b"),
  tools: await testMcpClient.listTools(),
});
