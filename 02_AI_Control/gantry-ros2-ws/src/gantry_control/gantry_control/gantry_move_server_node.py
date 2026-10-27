import threading
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from gantry_interfaces.srv import GantryMove, UpdateState


class GantryMoveServerNode(Node):
    def __init__(self):
        super().__init__('gantry_move_server_node')

        self.declare_parameter('move_delay', 1.0)

        cb_group = ReentrantCallbackGroup()

        self._update_state_client = self.create_client(
            UpdateState, 'update_gantry_state', callback_group=cb_group
        )
        self._move_service = self.create_service(
            GantryMove, 'gantry_move', self._handle_move, callback_group=cb_group
        )

        self.get_logger().info('GantryMoveServerNode (dummy) ready.')

    def _handle_move(self, request, response):
        delay = self.get_parameter('move_delay').get_parameter_value().double_value

        self.get_logger().info(
            f'[DUMMY] Move: src=({request.src_x1},{request.src_y1},{request.src_z1})'
            f'->({request.src_x2},{request.src_y2},{request.src_z2})'
            f'  dst=({request.dst_x1},{request.dst_y1},{request.dst_z1})'
            f'->({request.dst_x2},{request.dst_y2},{request.dst_z2})'
        )

        time.sleep(delay)
        self.get_logger().info(f'[DUMMY] Simulated move complete after {delay}s.')

        self._notify_state_update(request)

        response.success = True
        response.message = 'Dummy move complete.'
        return response

    def _notify_state_update(self, request):
        if not self._update_state_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn(
                'state_manager_node unavailable — active_pos.json not updated.'
            )
            return

        req = UpdateState.Request()
        req.src_x1 = request.src_x1
        req.src_y1 = request.src_y1
        req.src_z1 = request.src_z1
        req.src_x2 = request.src_x2
        req.src_y2 = request.src_y2
        req.src_z2 = request.src_z2
        req.dst_x1 = request.dst_x1
        req.dst_y1 = request.dst_y1
        req.dst_z1 = request.dst_z1
        req.dst_x2 = request.dst_x2
        req.dst_y2 = request.dst_y2
        req.dst_z2 = request.dst_z2

        event = threading.Event()
        future = self._update_state_client.call_async(req)
        future.add_done_callback(lambda _: event.set())

        if not event.wait(timeout=5.0):
            self.get_logger().warn('State update timed out.')
            return

        result = future.result()
        if result is None:
            self.get_logger().warn('State update returned None.')
        elif not result.success:
            self.get_logger().warn(f'State update failed: {result.message}')


def main(args=None):
    rclpy.init(args=args)
    node = GantryMoveServerNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
