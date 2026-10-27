# 02 · AI Control

A natural-language and web control layer for the gantry. It all runs on the **Jetson** ("Odin").
The partner's **Raspberry Pi** is the only machine that talks Modbus to the PLC.

```
Browser ─► gantry-frontend (Next.js :3000)
              └─► mastra-odin (:4111)  gantryAgent, gemma4:26b via Ollama
                    └─► gantry_mcp_server.py (MCP over stdio, embedded rclpy node)
                          ├─► /get_gantry_state  ─► state_manager_node (Jetson, ~/.gantry/active_pos.json)
                          └─► /gantry_move       ─► RPi gantry_command_node ─► Modbus ─► PLC
```

## Folders

| Folder | What it is |
|---|---|
| `gantry-ros2-ws/` | ROS2 Jazzy workspace: `gantry_interfaces` (3 `.srv` files) and `gantry_control` (state manager, MCP server, test clients, dummy move server). |
| `gantry-ros2-ws/modbus_test/plc_sim.py` | Fake Modbus PLC for testing without hardware (placeholder register map). |
| `gantry-ros2-ws/reference_rpi_modbus_client/` | The old Pi-side Modbus node. Not built (`COLCON_IGNORE`); a starting point only. |
| `mastra-odin/` | Mastra AI backend: agents, MCP client, chat API, memory and traces in `mastra.db`. |
| `gantry-frontend/` | Chat page (`/`) and read-only grid map (`/gantry`). |
| `SYSTEM_OVERVIEW.md` | Start order and how the three pieces connect. Each project also has a `CLAUDE.md`. |

## Run it (test mode, no Pi or PLC needed)

```bash
# Shell 1: ROS2
cd gantry-ros2-ws && just deps && source setup.sh && just build
just launch-test            # state_manager + dummy /gantry_move (1 s fake moves)
# Shell 2: AI backend (ROS2 must be sourced in this shell too)
cd gantry-ros2-ws && source setup.sh && cd ../mastra-odin && npm install && npm run dev
# Shell 3: web UI
cd gantry-frontend && cp .env.example .env.local && npm install && npm run dev
```

Prerequisites: Ubuntu + ROS2 Jazzy, `just`, `uv`, Node ≥ 20, and Ollama with `gemma4:26b` pulled.
Use `just launch` (state manager only) when the real Pi is serving `/gantry_move`.
`just test-unit` runs the move-validation tests; `just test` runs the state-service tests.

## Coordinates (important)

The grid is 1-indexed: **x 1–27** (x=1 nearest the gantry), **y 1–20**, **z = 1**. A container is
1×4 cells. `pos_1` and `pos_2` are its **end cells, inclusive**: `(1,1,1)→(1,4,1)` covers
y=1..4 in row x=1. The starting layout is `src/gantry_control/config/init.json` (20 containers in
rows x=1–8); zones are in `colors.json`.

## Changes made for this hand-off

- **Move safety checks:** new `move_validation.py`. The MCP server now rejects moves that are
  off-grid, not 4 cells long, have an unknown source, or overlap another container. Tests are in
  `test/test_move_validation.py`.
- **Move timeout:** the MCP move timeout is now set with `GANTRY_MOVE_TIMEOUT` (default 120 s;
  it was a fixed 35 s). A timeout message now warns that the gantry may still be moving.
- **Agent prompt:** `gantry_agent.ts` now explains the coordinate system correctly (the old
  example was 0-based, 5 cells long, and along the wrong axis).
- **Tests:** `test_state_manager.py` now backs up and restores the live `active_pos.json`
  (it used to overwrite it).
- **Defaults:** client-node defaults use real coordinates (C001 → empty row x=9).
  `launch-test` now defaults to 1 s.
- **Docs:** frontend README/.env.example rewritten.
- **Left out:** stale `init_revised.json`, old `init-*.json` copies, Mastra weather-template
  files, `node_modules`, `.next`, `mastra.db`, `.env` files, and macOS `._*` files.

## Known gaps (see the report for details)

1. The Pi-side Modbus code doesn't match the real PLC registers. See
   `01_Gantry_and_PLC/docs/MODBUS_INTERFACE.md`.
2. The Jetson and the Pi both run a `state_manager_node` with the **same service names**, which
   ROS2 can't reliably handle. Namespace or remove one.
3. The map page is read-only; click-to-move (`POST /api/gantry/move`) isn't built yet.
4. Hard-coded paths: `/home/vandal/gantry/...` in `gantry_mcp_server.sh` and `gantry-mcp-client.ts`.
5. After pulling these files, run `just build` so the new `move_validation.py` is installed.
