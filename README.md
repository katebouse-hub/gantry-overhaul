# Gantry Project: Hand-off Package

Start here. This package contains the essential files for the UIdaho 4-axis gantry robot
(Do-more BRX PLC + ROS2 + local-LLM control), organised so a new student can get oriented quickly.

**Read first:** `Gantry_Handoff_Report.docx`, a 3-page summary of the project's current state,
what's included, known issues, and where the project could go next.

| Folder | Contents | Start with |
|---|---|---|
| `01_Gantry_and_PLC/` | Current PLC program, ladder printout, I/O list, Modbus register map, photos | `README.md`, then `docs/MODBUS_INTERFACE.md` |
| `02_AI_Control/` | ROS2 workspace, MCP server, Mastra AI agent, Next.js web UI | `README.md`, then `SYSTEM_OVERVIEW.md` |
| `03_Vision/` | Camera grid-mapping prototype ("Skynet"), sample images, grid design notes | `README.md` |
| `04_Reference/` | Original Shipping Dock repo docs, earlier LLM agent, older PLC version, open questions | `README.md` |

## Suggested first week

1. Read the report, then the four folder READMEs (about one page each).
2. Open the PLC program in Do-more Designer and follow one move through `RECV_STG → PICK_UP_STG →
   MOVE_STG → DROP_OFF_STG` using `docs/MODBUS_INTERFACE.md`.
3. On a Linux machine with ROS2 Jazzy, run `02_AI_Control` in **test mode** (no hardware) and
   move a container from the chat page.
4. Meet the Raspberry Pi owner and agree on the Modbus register map before any live moves.

Who to ask: Davis Onyeoguzoro (PLC and wiring) · Dawson Burgess (vision, AI server) ·
Dr. John Shovic (faculty lead) · Kate (CS 5020 directed study, Fall 2026).
