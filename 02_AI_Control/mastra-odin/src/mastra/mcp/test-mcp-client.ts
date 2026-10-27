import { MCPClient } from "@mastra/mcp";

export const testMcpClient = new MCPClient({
  id: "test-mcp-client",
  servers: {
    //wikipedia: {
    //  command: "npx",
    //  args: ["-y", "wikipedia-mcp"],
    //},
    mastra_docs: {
      command: "npx",
      args: ["-y", "@mastra/mcp-docs-server"],
    },
    grepmcp: {
      url: new URL("https://mcp.grep.app"),
    },
  },
});
