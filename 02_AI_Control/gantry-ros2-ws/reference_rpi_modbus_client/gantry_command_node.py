import threading
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from gantry_interfaces.srv import GantryMove, UpdateState

try:
    from pymodbus.client import ModbusTcpClient

    MODBUS_AVAILABLE = True
except ImportError:
    MODBUS_AVAILABLE = False

# Register / coil map
HR_SRC_X = 0
HR_SRC_Y = 1
HR_SRC_Z = 2
HR_DST_X = 3
HR_DST_Y = 4
HR_DST_Z = 5
COIL_SEND = 0
COIL_ACK = 1

ACK_TIMEOUT_S = 30.0
ACK_POLL_INTERVAL_S = 0.1


class GantryCommandNode(Node):
    def __init__(self):
        super().__init__("gantry_command_node")

        self.declare_parameter("plc_host", "127.0.0.1")
        self.declare_parameter("plc_port", 5020)

        # ReentrantCallbackGroup allows _handle_move to await _update_state_client
        # without deadlocking the executor.
        cb_group = ReentrantCallbackGroup()

        self._update_state_client = self.create_client(
            UpdateState, "update_gantry_state", callback_group=cb_group
        )
        self._move_service = self.create_service(
            GantryMove, "gantry_move", self._handle_move, callback_group=cb_group
        )

        if not MODBUS_AVAILABLE:
            self.get_logger().warn("pymodbus not installed — Modbus writes disabled.")

        self.get_logger().info("GantryCommandNode ready.")

    def _handle_move(self, request, response):
        self.get_logger().info(
            f"Move request: src=({request.src_x1},{request.src_y1},{request.src_z1})"
            f"->({request.src_x2},{request.src_y2},{request.src_z2})"
            f"  dst=({request.dst_x1},{request.dst_y1},{request.dst_z1})"
            f"->({request.dst_x2},{request.dst_y2},{request.dst_z2})"
        )

        try:
            if MODBUS_AVAILABLE:
                self._execute_modbus_move(request)
            else:
                self.get_logger().warn("pymodbus unavailable — skipping PLC write.")

            self._notify_state_update(request)
            response.success = True
            response.message = "Move confirmed."

        except ConnectionError as e:
            response.success = False
            response.message = str(e)
        except TimeoutError as e:
            response.success = False
            response.message = str(e)
        except Exception as e:
            response.success = False
            response.message = str(e)

        return response

    def _execute_modbus_move(self, request):
        host = self.get_parameter("plc_host").get_parameter_value().string_value
        port = self.get_parameter("plc_port").get_parameter_value().integer_value

        client = ModbusTcpClient(host, port=port)
        if not client.connect():
            raise ConnectionError(f"Cannot connect to PLC at {host}:{port}")

        try:
            client.write_registers(
                HR_SRC_X,
                [
                    request.src_x1,
                    request.src_y1,
                    request.src_z1,
                    request.dst_x1,
                    request.dst_y1,
                    request.dst_z1,
                ],
            )
            self.get_logger().info(
                f"HR written: src=({request.src_x1},{request.src_y1},{request.src_z1})"
                f" dst=({request.dst_x1},{request.dst_y1},{request.dst_z1})"
            )

            client.write_coil(COIL_SEND, True)
            self.get_logger().info("SEND coil set. Waiting for ACK...")

            self._wait_for_ack(client)

            # Reset both coils so PLC is ready for next command
            client.write_coil(COIL_SEND, False)
            client.write_coil(COIL_ACK, False)
            self.get_logger().info("Coils reset.")
        finally:
            client.close()

    def _wait_for_ack(self, client):
        deadline = time.time() + ACK_TIMEOUT_S
        while time.time() < deadline:
            result = client.read_coils(COIL_ACK, count=1)
            if not result.isError() and result.bits[0]:
                self.get_logger().info("ACK received.")
                return
            time.sleep(ACK_POLL_INTERVAL_S)
        raise TimeoutError(f"No PLC ACK after {ACK_TIMEOUT_S}s")

    def _notify_state_update(self, request):
        if not self._update_state_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn(
                "state_manager_node unavailable — active_pos.json not updated."
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

        # Block this callback thread while the already-running MultiThreadedExecutor
        # processes the response on another thread.
        if not event.wait(timeout=5.0):
            self.get_logger().warn("State update timed out.")
            return

        result = future.result()
        if result is None:
            self.get_logger().warn("State update returned None.")
        elif not result.success:
            self.get_logger().warn(f"State update failed: {result.message}")


def main(args=None):
    rclpy.init(args=args)
    node = GantryCommandNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
