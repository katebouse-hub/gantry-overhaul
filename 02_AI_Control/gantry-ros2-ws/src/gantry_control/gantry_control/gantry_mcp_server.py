import asyncio
import json
import os
import threading

# Force ROS2 logs to stderr — stdout is reserved for MCP stdio protocol.
os.environ.setdefault('RCUTILS_LOGGING_USE_STDOUT', '0')

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from gantry_interfaces.srv import GantryMove, GetState

from gantry_control.move_validation import validate_move

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types


class GantryMCPNode(Node):
    def __init__(self):
        super().__init__('gantry_mcp_node')
        self._move_client = self.create_client(GantryMove, 'gantry_move')
        self._state_client = self.create_client(GetState, 'get_gantry_state')
        self.get_logger().info('GantryMCPNode ready.')


# How long to wait for /gantry_move to answer. A real pick-and-place can take longer than the
# old 35 s default; override with the GANTRY_MOVE_TIMEOUT environment variable (seconds).
MOVE_TIMEOUT_S = float(os.environ.get('GANTRY_MOVE_TIMEOUT', '120'))


async def _wait_ros(future, timeout: float = 35.0):
    """Bridge a ROS2 async future to asyncio without blocking the event loop."""
    loop = asyncio.get_running_loop()
    done = asyncio.Event()
    future.add_done_callback(lambda _: loop.call_soon_threadsafe(done.set))
    try:
        await asyncio.wait_for(done.wait(), timeout=timeout)
        return future.result()
    except asyncio.TimeoutError:
        return None


async def _wait_for_service(client, timeout: float = 5.0) -> bool:
    """Run wait_for_service in a thread so it doesn't block the asyncio event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, client.wait_for_service, timeout)


async def serve(node: GantryMCPNode) -> None:
    server = Server('gantry')

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name='gantry_move',
                description=(
                    'Move a 1x4 gridfinity container on the gantry. '
                    'pos_1 and pos_2 are the two END CELLS of the container (inclusive), e.g. '
                    'a container covering y=1..4 in row x=1 is (1,1,1)->(1,4,1). '
                    'Grid is 1-indexed: x 1-27, y 1-20, z 1. Source ends must exactly match '
                    'get_gantry_state. The move is rejected if the destination is off-grid, '
                    'not 4 cells long, or overlaps another container.'
                ),
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'src_x1': {'type': 'integer', 'description': 'Source end-1 X'},
                        'src_y1': {'type': 'integer', 'description': 'Source end-1 Y'},
                        'src_z1': {'type': 'integer', 'description': 'Source end-1 Z'},
                        'src_x2': {'type': 'integer', 'description': 'Source end-2 X'},
                        'src_y2': {'type': 'integer', 'description': 'Source end-2 Y'},
                        'src_z2': {'type': 'integer', 'description': 'Source end-2 Z'},
                        'dst_x1': {'type': 'integer', 'description': 'Destination end-1 X'},
                        'dst_y1': {'type': 'integer', 'description': 'Destination end-1 Y'},
                        'dst_z1': {'type': 'integer', 'description': 'Destination end-1 Z'},
                        'dst_x2': {'type': 'integer', 'description': 'Destination end-2 X'},
                        'dst_y2': {'type': 'integer', 'description': 'Destination end-2 Y'},
                        'dst_z2': {'type': 'integer', 'description': 'Destination end-2 Z'},
                    },
                    'required': [
                        'src_x1', 'src_y1', 'src_z1',
                        'src_x2', 'src_y2', 'src_z2',
                        'dst_x1', 'dst_y1', 'dst_z1',
                        'dst_x2', 'dst_y2', 'dst_z2',
                    ],
                },
            ),
            types.Tool(
                name='get_gantry_state',
                description='Get the current position of all containers on the gantry.',
                inputSchema={'type': 'object', 'properties': {}},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        if name == 'gantry_move':
            if not await _wait_for_service(node._move_client):
                return [types.TextContent(type='text', text='ERROR: /gantry_move service unavailable')]

            # Safety pre-check against the current state before anything moves.
            if not await _wait_for_service(node._state_client):
                return [types.TextContent(type='text', text='ERROR: /get_gantry_state unavailable; refusing to move without checking state')]
            st = await _wait_ros(node._state_client.call_async(GetState.Request()), timeout=5.0)
            if st is None or not st.success:
                return [types.TextContent(type='text', text='ERROR: could not read gantry state; move not sent')]
            reason = validate_move(json.loads(st.state_json), arguments)
            if reason:
                return [types.TextContent(type='text', text=f'Move rejected (nothing moved): {reason}')]

            req = GantryMove.Request()
            req.src_x1 = int(arguments['src_x1'])
            req.src_y1 = int(arguments['src_y1'])
            req.src_z1 = int(arguments['src_z1'])
            req.src_x2 = int(arguments['src_x2'])
            req.src_y2 = int(arguments['src_y2'])
            req.src_z2 = int(arguments['src_z2'])
            req.dst_x1 = int(arguments['dst_x1'])
            req.dst_y1 = int(arguments['dst_y1'])
            req.dst_z1 = int(arguments['dst_z1'])
            req.dst_x2 = int(arguments['dst_x2'])
            req.dst_y2 = int(arguments['dst_y2'])
            req.dst_z2 = int(arguments['dst_z2'])

            result = await _wait_ros(node._move_client.call_async(req), timeout=MOVE_TIMEOUT_S)
            if result is None:
                return [types.TextContent(type='text', text=f'ERROR: /gantry_move gave no answer within {MOVE_TIMEOUT_S:.0f}s. The gantry may still be moving; check get_gantry_state before retrying.')]
            if result.success:
                return [types.TextContent(type='text', text=f'Move succeeded: {result.message}')]
            return [types.TextContent(type='text', text=f'Move failed: {result.message}')]

        if name == 'get_gantry_state':
            if not await _wait_for_service(node._state_client):
                return [types.TextContent(type='text', text='ERROR: /get_gantry_state service unavailable')]

            result = await _wait_ros(node._state_client.call_async(GetState.Request()), timeout=5.0)
            if result is None:
                return [types.TextContent(type='text', text='ERROR: /get_gantry_state timed out')]
            if result.success:
                return [types.TextContent(type='text', text=result.state_json)]
            return [types.TextContent(type='text', text=f'ERROR: {result.message}')]

        return [types.TextContent(type='text', text=f"ERROR: Unknown tool '{name}'")]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    rclpy.init()
    node = GantryMCPNode()

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    ros_thread = threading.Thread(target=executor.spin, daemon=True)
    ros_thread.start()

    try:
        asyncio.run(serve(node))
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
