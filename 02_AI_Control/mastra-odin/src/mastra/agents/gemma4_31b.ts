import { ollama } from "ollama-ai-provider-v2";
import { Agent } from "@mastra/core/agent";
import { testMcpClient } from "../mcp/test-mcp-client";

export const gemma4_31b = new Agent({
  id: "gemma4_31b",
  name: "gemma4:31b",
  description: "You are a helpful assistant.",
  instructions: `You are a helpful assistant that has access to the following MCP Servers.
      - Mastra Ai Documentation
      - Grep App Search Tool (Github)

      Answer questions using the information you find using the MCP Servers when appropriate.`,
  model: ollama("gemma4:31b"),
  tools: await testMcpClient.listTools(),
});
