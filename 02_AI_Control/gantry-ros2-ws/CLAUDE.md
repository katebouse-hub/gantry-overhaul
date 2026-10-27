# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

`setup.sh` handles ROS2 sourcing, venv PYTHONPATH overlay, and workspace overlay in one step.

```bash
# First-time setup
just deps           # create .venv (no external packages needed currently)

# Every new shell
source setup.sh     # sources ROS2 + venv + install overlay

# Build
just build          # colcon build --symlink-install (rebuild after srv/msg changes)

# Production launch (state_manager only — partner's RPi serves /gantry_move)
just launch

# Test launch (state_manager + dummy server, no RPi needed)
just launch-test             # default 1.0s simulated delay
just launch-test delay=0.5   # faster for testing

# Tests (state_manager only, self-contained)
just test

# Reset active_pos.json to known init state
just reset-state
```

## Architecture

### Split responsibilities

This workspace runs on the **Jetson (client side)**. A partner's RPi 4 runs server nodes
independently and is the only machine that talks Modbus to the PLC.

```
Jetson (this repo)                     RPi 4 (partner's repo)
─────────────────────────────          ──────────────────────────────
state_manager_node                     gantry_command_node  ──► PLC (Modbus)
gantry_move_client_node  ──/gantry_move──►  (serves /gantry_move)
state_client_node        ──/get_gantry_state──► state_manager_node
                                       state_manager_node
```

Both machines share `gantry_interfaces` (same .srv files) and maintain their own
`active_pos.json`. State sync is verified by comparing both files.

### Packages

**`gantry_interfaces`** (`ament_cmake`) — shared service definitions. Must match partner's copy.
- `srv/GantryMove.srv` — 12 `int32` fields (src/dst XYZ × 2 ends each)
- `srv/GetState.srv` — returns `active_pos.json` as JSON string
- `srv/UpdateState.srv` — finds container at src position, updates to dst in `active_pos.json`

**`gantry_control`** (`ament_python`) — client-side nodes.
- `state_manager_node` — serves `/get_gantry_state` and `/update_gantry_state`. Owns local
  `active_pos.json`; bootstraps from `init.json` on first run.
- `gantry_move_client_node` — one-shot client for `/gantry_move`. Accepts coords as ROS2
  params, calls service, exits.
- `state_client_node` — one-shot client for state services. `mode:=get` or `mode:=update`.
- `gantry_move_server_node` — **dummy server for local testing only**. Serves `/gantry_move`,
  simulates a move with a configurable delay, then calls `/update_gantry_state`. No Modbus.
  Replaces the real RPi server when testing without hardware.

## State Files

| File | Path | Purpose |
|------|------|---------|
| `init.json` | `src/gantry_control/config/init.json` | Known-good startup state. Never mutated. Shared with partner. |
| `active_pos.json` | `~/.gantry/active_pos.json` | Live state. Mutated after each confirmed move. Reset with `just reset-state`. |

Both Jetson and RPi maintain independent `active_pos.json` files. Comparison between them
is how sync is verified.

Container schema: `id`, `color`, `pos_1` `{x,y,z}`, `pos_2` `{x,y,z}`. Containers are
1x4 gridfinity units; `pos_1`/`pos_2` are the two END CELLS, inclusive, in 1-indexed grid
coordinates (x 1-27, y 1-20, z 1). Example: `(1,1,1)→(1,4,1)` covers y=1..4 in row x=1.

`gantry_control/move_validation.py` is used by the MCP server to reject moves that are
off-grid, not 4 cells long, have an unknown source, or overlap another container.

## ROS2 Networking

No special DDS configuration needed. Both machines on same network segment with same
`ROS_DOMAIN_ID` (default 0) will discover each other automatically. Services are identified
by name — `/gantry_move`, `/get_gantry_state`, `/update_gantry_state`.

## Tests

`test/test_move_validation.py` — pure-Python tests of the move safety checks (`just test-unit`).

`test/test_state_manager.py` — tests local state services. Only needs `state_manager_node`
running. Each test temporarily sets `active_pos.json` to C001 at `(1,1,1)→(1,4,1)` and restores
the real file afterwards (`just test`).

## Launch Files

| File | Purpose |
|------|---------|
| `gantry_client.launch.py` | Production — starts `state_manager_node` only |
| `gantry_test.launch.py` | Testing — starts `state_manager_node` + `gantry_move_server_node` |

## Adding a New Node

1. Create `src/gantry_control/gantry_control/<node_name>.py`
2. Add entry point to `src/gantry_control/setup.py` under `console_scripts`
3. Run `just build`
4. If new service/message types needed: add `.srv`/`.msg` to `gantry_interfaces/srv/`, register
   in `CMakeLists.txt`, rebuild, and send updated `gantry_interfaces/` to partner

See `gantry_move_client_node.py` and `state_client_node.py` for the standard one-shot client
pattern (params → wait for service → `call_async` → done callback → exit).

## AI Agent & Frontend Integration

The full system has three consumers of the gantry services:

```
Partner's RPi  ──── ROS2 services ────┐
                                       ├── state_manager_node (always on, Jetson)
Mastra agent   ── MCP → rclpy ────────┤
                                       │
Next.js frontend (interactive map) ───┘
```

### MCP Server (`gantry_mcp_server.py`, used by mastra-odin)

A Python MCP server runs on the Jetson alongside the ROS2 nodes. It has an rclpy node
embedded inside it and exposes `gantry_move`, `get_gantry_state` as MCP tools. The Mastra
agent connects to it as an MCP client. This replaces manually running `gantry_move_client_node`
from the terminal — the agent triggers the same logic programmatically.

### Frontend: Two options, Option B chosen

**Option A — HTTP bridge (Python FastAPI on Jetson):**
Next.js calls REST endpoints directly. FastAPI translates to rclpy calls. MCP server and
HTTP bridge are separate processes (or the same process serving both protocols).

**Option B (chosen) — Mastra exposes REST API, frontend calls it:**
Next.js calls Mastra API endpoints for both AI and non-AI actions. The interactive map
page calls e.g. `POST /api/gantry/move` which directly invokes the `gantry_move` MCP tool
— no agent reasoning loop, instant response. The AI chat page uses the same tool via the
agent. One backend to maintain. Planned with Next.js + assistant-ui.

## Python Dependencies

Non-ROS packages go in `requirements.txt`. Install with `just deps`. The venv site-packages
are overlaid onto PYTHONPATH by `setup.sh` and baked into `just launch` / `just test`.
System Python is externally managed on this Jetson — do not use `--system`.
