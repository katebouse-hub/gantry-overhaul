#!/usr/bin/env python3
"""
Mock PLC Modbus TCP server for gantry control testing.

Simulates the PLC coil/register handshake:
  1. Client writes destination XYZ to HR0-2
  2. Client sets Coil0 (SEND) = True
  3. Server simulates move delay, then sets Coil1 (ACK) = True
  4. Client reads ACK, resets both coils

Register map:
  Holding Registers: HR0=X  HR1=Y  HR2=Z
  Coils:             C0=SEND  C1=ACK

Run this on your dev laptop, then point gantry_command_node at your laptop's IP.
  python3 plc_sim.py --host 0.0.0.0 --port 5020
"""

import argparse
import asyncio
import logging

from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import ModbusTcpServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [PLC-SIM]  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Must match gantry_command_node.py constants
HR_SRC_X = 0
HR_SRC_Y = 1
HR_SRC_Z = 2
HR_DST_X = 3
HR_DST_Y = 4
HR_DST_Z = 5
COIL_SEND = 0
COIL_ACK = 1

# pymodbus function codes for getValues / setValues
FC_COILS = 1
FC_HOLDING_REGS = 3

DEVICE_ID = 0


async def _monitor_loop(context: ModbusServerContext, move_delay: float):
    """
    Poll SEND coil. When client sets it, read HR coords, simulate move, flip ACK.
    """
    device = context[DEVICE_ID]
    log.info("Monitor task started.")

    while True:
        coils = device.getValues(FC_COILS, COIL_SEND, count=2)
        send_active = bool(coils[0])
        ack_active = bool(coils[1])

        if send_active and not ack_active:
            regs = device.getValues(FC_HOLDING_REGS, HR_SRC_X, count=6)
            sx, sy, sz = regs[0], regs[1], regs[2]
            dx, dy, dz = regs[3], regs[4], regs[5]

            log.info(f"SEND triggered — src=({sx},{sy},{sz})  dst=({dx},{dy},{dz})")
            log.info(f"Simulating move ({move_delay}s)...")
            await asyncio.sleep(move_delay)

            device.setValues(FC_COILS, COIL_ACK, [True])
            log.info("ACK set — ready for client to reset coils.")

        await asyncio.sleep(0.05)


async def run_server(host: str, port: int, move_delay: float):
    store = ModbusDeviceContext(
        co=ModbusSequentialDataBlock(0, [False] * 16),
        hr=ModbusSequentialDataBlock(0, [0] * 16),
    )
    context = ModbusServerContext(devices=store, single=True)

    asyncio.create_task(_monitor_loop(context, move_delay))

    log.info(f"Listening on {host}:{port}")
    log.info("Register map: HR0-2=src XYZ  HR3-5=dst XYZ  |  C0=SEND  C1=ACK")
    log.info("Waiting for connections...")

    server = ModbusTcpServer(context=context, address=(host, port))
    await server.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        description="Mock PLC Modbus TCP server for gantry testing"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5020,
        help="Port (default: 5020 — use 502 for standard Modbus, requires root)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Simulated move duration in seconds (default: 1.5)",
    )
    args = parser.parse_args()
    asyncio.run(run_server(args.host, args.port, args.delay))


if __name__ == "__main__":
    main()
