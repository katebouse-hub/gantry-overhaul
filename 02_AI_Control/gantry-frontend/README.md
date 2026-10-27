# gantry-frontend

Next.js + assistant-ui web app for the gantry. Runs on port 3000.

| Page | What it does |
|------|--------------|
| `/` | Chat with `gantryAgent` (Mastra backend on port 4111). Threads persist in Mastra memory. |
| `/gantry` | Read-only map of the 27x20 grid and container positions, refreshed from `~/.gantry/active_pos.json` via `app/api/gantry/state/route.ts`. |

## Run

```bash
cp .env.example .env.local     # points the chat at http://localhost:4111/chat/gantry_agent
npm install
npm run dev                    # http://localhost:3000
```

Start `gantry-ros2-ws` and `mastra-odin` first (see `../SYSTEM_OVERVIEW.md`).

## Notes

- The map reads the state file straight from disk, so the frontend must run on the same machine
  as `state_manager_node` (the Jetson).
- Click-to-move on the map is not built yet. The planned route is a Mastra endpoint
  (e.g. `POST /api/gantry/move`) that calls the `gantry_move` MCP tool directly.
- Zone layout and colours live in `lib/gantry-data.ts` (mirrors `gantry-ros2-ws/colors.json`).
