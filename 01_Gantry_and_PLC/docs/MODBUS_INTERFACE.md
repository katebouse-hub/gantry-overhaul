# PLC ↔ Raspberry Pi Modbus Interface

Read from `plc_program/10-12-2026 plc pull_EXPORT_DMD.txt` (the `Modb_SR`, `Coord_Map_SR`,
`Heartbeat_SR`, `RECV_STG` and `DROP_OFF_STG` blocks). This is what the PLC actually expects.
**Check it against the live PLC before you rely on it.** Do-more `MHRn` is Modbus holding register
4000n (zero-based offset n−1).

## The PLC as Modbus server (the Pi writes and reads these)

| PLC memory | Copied to | Tag name | Direction | Meaning |
|---|---|---|---|---|
| MHR50 | V50 | pickup_x_row | Pi → PLC | Pick-up row index, X |
| MHR51 | V51 | pickup_y_row | Pi → PLC | Pick-up row index, Y |
| MHR52 | V52 | pickup_z_row | Pi → PLC | Pick-up Z (not used by lookups yet) |
| MHR53 | V53 | dropoff_x_row | Pi → PLC | Drop-off row index, X |
| MHR54 | V54 | dropoff_y_row | Pi → PLC | Drop-off row index, Y |
| MHR55 | V55 | dropoff_z_row | Pi → PLC | Drop-off Z (not used by lookups yet) |
| MHR211 | D211 | CMD_ID_REG | Pi → PLC | Command ID. A new value starts a move. |
| MHR212 | D212 | START_CMD_REG | Pi → PLC | Start command |
| MHR213 | D213 | ACK_ID_REG | Pi → PLC | Acknowledge ID |
| MHR214 | D214 | SERVER_READY_REG | Pi → PLC | Server ready (≥1 = ready) |
| MHR215 | D215 | PLC_READY_REG | Pi → PLC | PLC ready (mirror) |
| MHR197 | D195 | pi_heartbeat | Pi → PLC | Must keep changing, or `pi_hb_alive` (C175) drops |
| MHR151–154 | — | encoder counts | PLC → Pi | X1, X2, Y, Z high-speed counter values |
| MC1–MC7 | — | status bits | PLC → Pi | ESTOP, estop_rev, fault, plc_busy, plc_ready, server_ready, all_sys_homed |

The row indices look up motor targets in the arrays `GntXOneCntArr`, `GntXTwoCntArr` and
`GntYAxisMmArr` (256 entries each).

## How a move starts (RECV_STG rung 17)

The PLC runs `PICK_UP_STG → MOVE_STG → DROP_OFF_STG` when **all** of these are true:
`server_snd_move` (C206), `pi_hb_alive` (C175), `CMD_ID_REG ≠ LAST_CMD_ID` (D211 ≠ D218),
not `MOTION_BUSY` (C217), and no `fault` (C6). When drop-off finishes, the PLC copies D211 → D218.
**So to command a move: write the six MHR50–55 values, then write a new CMD_ID to MHR211.**

## The PLC as Modbus client

- `STG_INIT` writes and reads `192.168.3.69:502`.
- `START_STG` and `RECV_STG` write `plc_ready` / C807 to `192.168.3.6:502`.
- It publishes MQTT to `192.168.3.50:1883`, topic prefix `top_level/field/`.

## Mismatches with the AI-control code (02_AI_Control)

1. `reference_rpi_modbus_client/gantry_command_node.py` and `modbus_test/plc_sim.py` use a
   placeholder map (HR0–5 plus coils C0 SEND / C1 ACK). **The real PLC uses MHR50–55 plus a CMD_ID
   handshake.** The Pi-side code needs to be rewritten to match the table above.
2. The PLC takes **one pick-up point and one drop-off point**. ROS2 `GantryMove` sends both ends
   of a container, so the Pi must turn a container (two ends) into one grab point and a row index.
3. Encoder counts are copied to MHR150–153 in `Coord_Map_SR` but to MHR151–154 in `Modb_SR`.
   Pick one.
4. `Coord_Map_SR` rung 2 is gated by `X980`, which isn't a wired input (see `gantry_io_list.xlsx`,
   "To Verify" tab), so it never runs.
