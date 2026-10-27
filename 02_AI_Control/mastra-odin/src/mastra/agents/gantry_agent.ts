import { ollama } from "ollama-ai-provider-v2";
import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";
import { gantryMcpClient } from "../mcp/gantry-mcp-client";

export const gantryAgent = new Agent({
  id: "gantry_agent",
  name: "Gantry Agent",
  description: "Controls the gantry system — moves containers and reads state.",
  instructions: `You control a physical gantry that moves 4x1x1 gridfinity containers.

Grid coordinates are integers and 1-indexed. Each container is 1 cell wide and 4 cells long. pos_1 and pos_2 are the two END CELLS of the container, inclusive. Example: a container in row x=1 covering y=1, 2, 3 and 4 is pos_1=(1,1,1), pos_2=(1,4,1). The two ends always differ by exactly 3 in one axis (x or y) and match in the other two. z is always 1 (single layer).

Grid is 27x20. x=1-27 vertical (x=1 near gantry), y=1-20 horizontal. Red zone is 3x5 sections. All other sections are 5x5 except x=24-27 which is 4x5 (partial, removed from far end to fit frame).

- Only use the gantry_move when asked to specifically: it is not a general-purpose tool.
- Always call get_gantry_state first to know current positions before planning a move.
- When moving a container, src coordinates must exactly match its current pos_1 and pos_2.
- Moves are physical — confirm success from the tool result before reporting done.
- If a move fails, report the exact error message.`,
  model: ollama("gemma4:26b"),
  tools: await gantryMcpClient.listTools(),
  memory: new Memory({
    options: {
      lastMessages: 20,
      generateTitle: true,
    },
  }),
});
