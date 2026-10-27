"""
Sample client node for the /gantry_move service.

Demonstrates how to call /gantry_move (served by the RPi, or by the dummy server in test mode).
Defaults move C001 from row x=1 (y 1-4) to the empty row x=9 (y 1-4).
Sends one move request using ROS2 params, prints the result, then exits.

Usage:
  ros2 run gantry_control gantry_move_client_node

Override coordinates at launch:
  ros2 run gantry_control gantry_move_client_node --ros-args \
    -p src_x1:=1 -p src_y1:=1 -p src_z1:=1 \
    -p src_x2:=1 -p src_y2:=4 -p src_z2:=1 \
    -p dst_x1:=9 -p dst_y1:=1 -p dst_z1:=1 \
    -p dst_x2:=9 -p dst_y2:=4 -p dst_z2:=1
"""

import rclpy
from rclpy.node import Node

from gantry_interfaces.srv import GantryMove


class GantryMoveClientNode(Node):
    def __init__(self):
        super().__init__('gantry_move_client_node')

        self.declare_parameter('src_x1', 1)
        self.declare_parameter('src_y1', 1)
        self.declare_parameter('src_z1', 1)
        self.declare_parameter('src_x2', 1)
        self.declare_parameter('src_y2', 4)
        self.declare_parameter('src_z2', 1)
        self.declare_parameter('dst_x1', 9)
        self.declare_parameter('dst_y1', 1)
        self.declare_parameter('dst_z1', 1)
        self.declare_parameter('dst_x2', 9)
        self.declare_parameter('dst_y2', 4)
        self.declare_parameter('dst_z2', 1)

        self._client = self.create_client(GantryMove, 'gantry_move')
        self._done = False

        self.get_logger().info('Waiting for gantry_move service...')
        if not self._client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('gantry_move service not available.')
            self._done = True
            return

        self._send_request()

    def _send_request(self):
        def _p(name):
            return self.get_parameter(name).get_parameter_value().integer_value

        req = GantryMove.Request()
        req.src_x1, req.src_y1, req.src_z1 = _p('src_x1'), _p('src_y1'), _p('src_z1')
        req.src_x2, req.src_y2, req.src_z2 = _p('src_x2'), _p('src_y2'), _p('src_z2')
        req.dst_x1, req.dst_y1, req.dst_z1 = _p('dst_x1'), _p('dst_y1'), _p('dst_z1')
        req.dst_x2, req.dst_y2, req.dst_z2 = _p('dst_x2'), _p('dst_y2'), _p('dst_z2')

        self.get_logger().info(
            f'Requesting move: '
            f'src=({req.src_x1},{req.src_y1},{req.src_z1})->({req.src_x2},{req.src_y2},{req.src_z2})  '
            f'dst=({req.dst_x1},{req.dst_y1},{req.dst_z1})->({req.dst_x2},{req.dst_y2},{req.dst_z2})'
        )

        future = self._client.call_async(req)
        future.add_done_callback(self._on_response)

    def _on_response(self, future):
        result = future.result()
        if result.success:
            self.get_logger().info(f'Move succeeded: {result.message}')
        else:
            self.get_logger().error(f'Move failed: {result.message}')
        self._done = True


def main(args=None):
    rclpy.init(args=args)
    node = GantryMoveClientNode()
    while not node._done:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()
