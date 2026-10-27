import { MCPClient } from "@mastra/mcp";

export const gantryMcpClient = new MCPClient({
  id: "gantry-mcp-client",
  servers: {
    gantry: {
      command: "/home/vandal/gantry/gantry-ros2-ws/gantry_mcp_server.sh",
    },
  },
});
