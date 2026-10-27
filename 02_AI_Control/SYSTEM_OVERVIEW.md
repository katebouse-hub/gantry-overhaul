# Gantry AI Control — System Overview

Three projects live here. Each has its own CLAUDE.md with more detail.

## Repos

| Repo | Purpose | Port |
|------|---------|------|
| `gantry-ros2-ws/` | ROS2 nodes — state manager, MCP server, gantry control | — |
| `mastra-odin/` | Mastra AI backend — agents, MCP client, REST API | 4111 |
| `gantry-frontend/` | Next.js + assistant-ui frontend | 3000 |

## Start Order

```bash
# 1. Source ROS2 + start state manager (gantry-ros2-ws)
cd gantry-ros2-ws
source setup.sh
just launch          # production (state_manager only)
# just launch-test   # testing (no RPi needed)

# 2. Start Mastra backend (in a new shell, ROS2 must be sourced first)
cd gantry-ros2-ws && source setup.sh
cd ../mastra-odin
npm run dev          # port 4111

# 3. Start frontend
cd gantry-frontend
npm run dev          # port 3000
```

## How They Connect

```
gantry-frontend (3000)
  └── AssistantChatTransport → POST http://localhost:4111/chat/gantry_agent
        └── mastra-odin (4111) — chatRoute() → gantryAgent
              └── gantry-mcp-client → gantry_mcp_server.sh (stdio)
                    └── rclpy node → /gantry_move, /get_gantry_state (ROS2)
```

Frontend env: `NEXT_PUBLIC_MASTRA_URL=http://localhost:4111/chat/gantry_agent`

## Key Notes

- Mastra must be started from a shell where `gantry-ros2-ws/setup.sh` is sourced, so `gantry_mcp_server` is on PATH with the correct ROS2 env.
- `gantryAgent` id is `gantry_agent` (snake_case), registered as `gantryAgent` (camelCase) key in Mastra.
- Frontend uses AI SDK v6 (`"ai": "^6.x"`). `chatRoute()` in mastra-odin is configured with `version: "v6"`.
- `app/api/chat/` does not exist in gantry-frontend — transport calls Mastra directly.

## Sub-repo CLAUDE.md Locations

- `gantry-ros2-ws/CLAUDE.md` — ROS2 build/launch/test, architecture, state files
- `mastra-odin/CLAUDE.md` — Mastra agents, MCP setup, start commands

## Frontend Pages

1. **`/`** — AI chat with `gantryAgent`, persistent threads via Mastra memory
2. **`/gantry`** — Interactive container map, reads `~/.gantry/active_pos.json` via `/api/gantry/state`

## Observability & Memory

Storage: `mastra.db` (LibSQL/SQLite) in `mastra-odin/`. Created on first run.
- Observability: `DefaultExporter` persists traces to DB → visible in Mastra Studio at `localhost:4111`
- Memory: `gantryAgent` has `Memory({ lastMessages: 20, generateTitle: true })`
- Thread ID comes from `AssistantChatTransport` → sent as `memory.thread` in request body
- Resource ID: hardcoded `"gantry-user"` (no auth in frontend yet)
