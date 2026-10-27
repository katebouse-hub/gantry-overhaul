# 01 · Gantry and PLC

The physical 4-axis gantry (X1, X2, Y, Z plus a pneumatic gripper), controlled by an
AutomationDirect **Do-more BRX PLC (BX-DM1E-x)**, link name `GANTRY_BRX`. The PLC owns all
real-time motion, homing, limit switches and E-stop. Everything else (Pi, Jetson, AI) only asks
it to move.

## What's in this folder

| Path | What it is |
|---|---|
| `plc_program/10-12-2026 plc pull.dmd` (+ `.dlo`, `.wsp`) | **Current PLC project.** Open the `.dmd` in Do-more Designer. Keep all three files together. |
| `plc_program/..._EXPORT_DMD.txt` | Same program as plain text. Search it with any editor; quickest way to find a tag or rung. |
| `plc_program/..._EXPORT_CMORE.csv` | Tag export for a C-more HMI. |
| `docs/gantry_ladder_logic_printout.pdf` | 66-page ladder printout (9/4/2026). Easiest to read on paper. |
| `docs/gantry_io_list.xlsx` | Wired I/O: inputs, encoders, outputs, PWM frequencies, plus a **To Verify** tab. |
| `docs/MODBUS_INTERFACE.md` | Registers the Pi must use to command moves. **Read this before touching 02_AI_Control.** |
| `images/` | System process-flow diagram and a photo of the gantry with containers. |

The 10-12-2026 pull has the same logic as Davis's original export (only the file header
differs), so the original copy is not repeated here.

## How the program is organised

- **`$Main`** runs lights, safety and the stage programs.
- **Stage programs, in order:** `STG_INIT` (idle, opens Modbus) → `START_STG` → `HOME_STG` /
  `Find_Home` → `True_Calib_STG` → `RECV_STG` (waits for a command) → `PICK_UP_STG` →
  `MOVE_STG` → `DROP_OFF_STG` → back to `RECV_STG`.
- **Subroutines:** per-axis homing (`X1_Hom`, `X2_Hom`, `Y_Hom`, `Z_Hom`), moves (`X_Mov`,
  `Y_Mov`, `Z_Mov`), drop-offs (`X_Drp`, `Y_Drp`), `Coord_Map_SR`, `Modb_SR`, `Heartbeat_SR`,
  `Reset_SR`. Some have doubled-letter copies (`X1_Homm`, `X_Movv`…): check which ones are
  actually CALLed before editing.
- **Position feedback:** quadrature encoders on high-speed counters `$HSIO_003_CT1–4`
  (X1, X2, Y, Z). The Z axis has a hard stop at count 9100 (`Z_Max_Thr` ISR).

## Quick start

1. Install **Do-more Designer** (2.11 or newer) on Windows.
2. Connect over Ethernet. Use *PLC → Connect*; if the IP is unknown, find the PLC by MAC address.
3. Open the `.dmd`, then use *Read from PLC* to compare against what's running **before** you
   write anything.
4. Power-up sequence: clear E-stop (X0) → press START (X1) → the gantry homes (blue light) → the
   white light means `system_ready`.
5. Save every change as a new dated pull (`MM-DD-YYYY plc pull.*`) and re-export the `.txt`.

## Safety

- E-stop (X0) drives the red light, the buzzer and the fault latch. Test it before every session.
- Only the X1 and Z drivers have enable outputs in use (Y17, Y23). Y19 and Y21 are named
  `ena_x2` / `ena_y` but are never used (see the I/O list).
- Open question for Davis: are there Y-axis limit switches on **both** sides?
  (`04_Reference/open_questions_for_davis.txt`)
