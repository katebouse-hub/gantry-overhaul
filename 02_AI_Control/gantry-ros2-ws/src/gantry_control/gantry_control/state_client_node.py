"""
Sample client node for /get_gantry_state and /update_gantry_state services.

Demonstrates how to interact with state_manager_node from another ROS2 node.
Runs one operation based on the `mode` param, prints result, then exits.

Usage:
  # Get current state
  ros2 run gantry_control state_client_node

  # Update a container position
  ros2 run gantry_control state_client_node --ros-args -p mode:=update \
    -p src_x1:=1 -p src_y1:=1 -p src_z1:=1 \
    -p src_x2:=1 -p src_y2:=4 -p src_z2:=1 \
    -p dst_x1:=9 -p dst_y1:=1 -p dst_z1:=1 \
    -p dst_x2:=9 -p dst_y2:=4 -p dst_z2:=1
"""

import json

import rclpy
from rclpy.node import Node

from gantry_interfaces.srv import GetState, UpdateState


class StateClientNode(Node):
    def __init__(self):
        super().__init__('state_client_node')

        self.declare_parameter('mode', 'get')  # 'get' | 'update'

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

        self._done = False
        mode = self.get_parameter('mode').get_parameter_value().string_value

        if mode == 'update':
            self._run_update()
        else:
            self._run_get()

    def _run_get(self):
        client = self.create_client(GetState, 'get_gantry_state')
        self.get_logger().info('Waiting for get_gantry_state service...')
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('get_gantry_state not available.')
            self._done = True
            return

        future = client.call_async(GetState.Request())

        def _on_response(f):
            result = f.result()
            if result.success:
                self.get_logger().info(
                    f'State:\n{json.dumps(json.loads(result.state_json), indent=2)}'
                )
            else:
                self.get_logger().error(f'GetState failed: {result.message}')
            self._done = True

        future.add_done_callback(_on_response)

    def _run_update(self):
        client = self.create_client(UpdateState, 'update_gantry_state')
        self.get_logger().info('Waiting for update_gantry_state service...')
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('update_gantry_state not available.')
            self._done = True
            return

        def _p(name):
            return self.get_parameter(name).get_parameter_value().integer_value

        req = UpdateState.Request()
        req.src_x1, req.src_y1, req.src_z1 = _p('src_x1'), _p('src_y1'), _p('src_z1')
        req.src_x2, req.src_y2, req.src_z2 = _p('src_x2'), _p('src_y2'), _p('src_z2')
        req.dst_x1, req.dst_y1, req.dst_z1 = _p('dst_x1'), _p('dst_y1'), _p('dst_z1')
        req.dst_x2, req.dst_y2, req.dst_z2 = _p('dst_x2'), _p('dst_y2'), _p('dst_z2')

        self.get_logger().info(
            f'Requesting update: '
            f'src=({req.src_x1},{req.src_y1},{req.src_z1})->({req.src_x2},{req.src_y2},{req.src_z2})  '
            f'dst=({req.dst_x1},{req.dst_y1},{req.dst_z1})->({req.dst_x2},{req.dst_y2},{req.dst_z2})'
        )

        future = client.call_async(req)

        def _on_response(f):
            result = f.result()
            if result.success:
                self.get_logger().info('State updated successfully.')
            else:
                self.get_logger().error(f'UpdateState failed: {result.message}')
            self._done = True

        future.add_done_callback(_on_response)


def main(args=None):
    rclpy.init(args=args)
    node = StateClientNode()
    while not node._done:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()
