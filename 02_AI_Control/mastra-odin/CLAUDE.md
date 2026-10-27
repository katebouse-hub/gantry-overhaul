# CLAUDE.md

## Start

```bash
# Mastra must be started with the ROS2 workspace sourced so that
# gantry_mcp_server is on PATH and inherits the ROS2 environment.
# In the gantry-ros2-ws directory:
source setup.sh

# Then start Mastra from this directory:
npm run dev    # development
npm run start  # production
```

## Architecture

This is the Mastra AI backend for the gantry system. It runs on the Jetson alongside
the ROS2 nodes.

```
Mastra agent (gantryAgent)
  └── gantry-mcp-client  (MCPClient — spawns gantry_mcp_server as subprocess)
        └── gantry_mcp_server  (Python, in gantry-ros2-ws repo)
              └── rclpy node → /gantry_move (RPi), /get_gantry_state (local)
```

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `gantryAgent` | gemma4:26b | Controls gantry — moves containers, reads state |
| others | various | General-purpose assistants |

## MCP

- `gantry-mcp-client.ts` — connects to the Python gantry MCP server (stdio, spawned as subprocess)
- `test-mcp-client.ts` — connects to external MCP servers (Mastra docs, grep.app)

The gantry MCP server exposes two tools:
- `gantry_move` — moves a container (12 int32 coords)
- `get_gantry_state` — returns current `active_pos.json` as JSON

## Frontend (planned)

Next.js + assistant-ui. Two pages:
- AI chat — talks to `gantryAgent`
- Interactive container map — no AI, calls Mastra REST API directly to trigger moves

See gantry-ros2-ws/TODO.md for full roadmap.
