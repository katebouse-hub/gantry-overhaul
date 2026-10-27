# 04 · Reference

Background material. **Nothing here runs today.** It explains where the project came from and
holds earlier versions you may want to compare against.

## Project history

The gantry started as the **Shipping Dock Gantry** (University of Idaho robotics program; faculty lead Dr. John Shovic):
a miniature automated shipping dock combining a PLC, ROS2, machine vision, Ignition SCADA and an
LLM. Original team: **Davis Onyeoguzoro** (team lead, PLC, wiring), **Tim Libeck** (ROS2, PLC
co-lead), **James Lasso** (ROS2 co-lead, Ignition, Git), **Dawson Burgess** (server admin, AI,
vision). The CS 5020 directed study (Fall 2026) continued the PLC logic analysis and developed the
current ROS2 + Mastra AI control layer (02_AI_Control).

## What's in this folder

| Path | What it is | Why keep it |
|---|---|---|
| `original_shipping_dock_repo/README.md` | Original project README: goals, features, team roles. | Explains the bigger vision (PackML, Ignition SCADA, factory-cell integration). |
| `original_shipping_dock_repo/ai_and_vision_README.md` | Describes "Auto" (LLM agent) and "Skynet" (vision). | Context for 02 and 03. |
| `original_shipping_dock_repo/LICENSE` | MIT licence of the original repo. | Licensing. |
| `earlier_llm_agent_auto/backend.py` | First LLM agent: pydantic-ai + Ollama (gpt-oss), FastAPI, tool `send_gantry_instructions`. | Earlier design, replaced by Mastra + MCP. |
| `earlier_llm_agent_auto/page.tsx` | Its Next.js/CopilotKit chat page. | Same. |
| `earlier_llm_agent_auto/important_changes.md` | Patch note for a pydantic-ai streaming bug (empty text deltas). | Saves time if anyone revives it. |
| `older_plc_version/Brx_Gantry_Da.*` | Earlier, smaller Do-more project (~13 KB vs ~29 KB now). | Shows how the PLC program grew. |
| `older_plc_version/logic.txt`, `tags.csv` | Text and tag exports of an earlier program. | Searchable diff baseline. |
| `open_questions_for_davis.txt` | Questions still open for the original PLC author. | Ask before rewiring. |

## Not included (still in the course folder if needed)

- `PLC-ROS2-Shipping-Dock-Gantry-master.zip`: the full original repo, including the CopilotKit
  app scaffolding, the `uv.lock`, and duplicate camera captures.
- `davis_original_gantry_code/`: same ladder logic as `01_Gantry_and_PLC/plc_program`.
- `Gantry AI control/`: the full working copies, with `node_modules`, build output and local
  databases.

## Using this material

- Compare PLC versions by diffing the exported `.txt` files (code starts after the `#END` of
  `SYS_CONFIG`; the header hashes always differ).
- To understand the original zone and priority rules, read `03_Vision/docs/grid_system.md`
  together with the original README. The zones in `02_AI_Control/gantry-ros2-ws/colors.json` are
  the current implementation.
