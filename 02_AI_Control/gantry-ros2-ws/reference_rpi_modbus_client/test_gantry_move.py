"""
Integration tests for gantry_command_node.

Requires ALL of the following running before executing:
  1. Dev laptop: python3 modbus_test/plc_sim.py --host 0.0.0.0 --port 5020
  2. Jetson:     ros2 run gantry_control state_manager_node
  3. Jetson:     ros2 run gantry_control gantry_command_node \
                   --ros-args -p plc_host:=<laptop_ip> -p plc_port:=5020

Run with: colcon test --packages-select gantry_control
Or:       pytest src/gantry_control/test/test_gantry_move.py -v
"""

import json
import os
import socket
import pytest
import rclpy

from gantry_interfaces.srv import GantryMove, GetState

ACTIVE_JSON_PATH = os.path.expanduser('~/.gantry/active_pos.json')
SERVICE_TIMEOUT = 5.0
MOVE_TIMEOUT = 40.0  # includes PLC sim delay + ack polling


def _plc_sim_reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


KNOWN_STATE = {
    'containers': [
        {
            'id': 'C001',
            'color': 'red',
            'pos_1': {'x': 0, 'y': 0, 'z': 0},
            'pos_2': {'x': 4, 'y': 0, 'z': 0},
        }
    ]
}


@pytest.fixture(autouse=True)
def reset_active_json():
    """Write known state before each test so container positions are predictable."""
    os.makedirs(os.path.dirname(ACTIVE_JSON_PATH), exist_ok=True)
    with open(ACTIVE_JSON_PATH, 'w') as f:
        json.dump(KNOWN_STATE, f, indent=2)


@pytest.fixture(scope='module')
def ros_client():
    rclpy.init()
    node = rclpy.create_node('test_gantry_move_client')
    yield node
    node.destroy_node()
    rclpy.shutdown()


@pytest.fixture(scope='module')
def move_client(ros_client):
    client = ros_client.create_client(GantryMove, 'gantry_move')
    available = client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)
    if not available:
        pytest.skip('gantry_move service not available — is gantry_command_node running?')
    return client


class TestGantryMove:
    def test_service_available(self, ros_client):
        client = ros_client.create_client(GantryMove, 'gantry_move')
        available = client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)
        assert available, 'gantry_move service not available'

    def test_move_returns_success(self, ros_client, move_client):
        """Full move: send coords → PLC sim acks → state updated."""
        req = GantryMove.Request()
        # Source container C001 at known init position
        req.src_x1, req.src_y1, req.src_z1 = 0, 0, 0
        req.src_x2, req.src_y2, req.src_z2 = 4, 0, 0
        # Destination
        req.dst_x1, req.dst_y1, req.dst_z1 = 8, 0, 0
        req.dst_x2, req.dst_y2, req.dst_z2 = 12, 0, 0

        future = move_client.call_async(req)
        rclpy.spin_until_future_complete(ros_client, future, timeout_sec=MOVE_TIMEOUT)

        result = future.result()
        assert result is not None, 'No response from gantry_move service'
        assert result.success, f'Move failed: {result.message}'

    def test_state_updated_after_move(self, ros_client, move_client):
        """After confirmed move, active_pos.json must reflect new container position."""
        # Move C001 to a distinct position
        req = GantryMove.Request()
        req.src_x1, req.src_y1, req.src_z1 = 0, 0, 0
        req.src_x2, req.src_y2, req.src_z2 = 4, 0, 0
        req.dst_x1, req.dst_y1, req.dst_z1 = 20, 0, 0
        req.dst_x2, req.dst_y2, req.dst_z2 = 24, 0, 0

        future = move_client.call_async(req)
        rclpy.spin_until_future_complete(ros_client, future, timeout_sec=MOVE_TIMEOUT)
        assert future.result().success

        # Verify via get_gantry_state service
        state_client = ros_client.create_client(GetState, 'get_gantry_state')
        assert state_client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)
        state_future = state_client.call_async(GetState.Request())
        rclpy.spin_until_future_complete(ros_client, state_future, timeout_sec=SERVICE_TIMEOUT)

        state = json.loads(state_future.result().state_json)
        c001 = next((c for c in state['containers'] if c['id'] == 'C001'), None)
        assert c001 is not None
        assert c001['pos_1']['x'] == 20
        assert c001['pos_2']['x'] == 24

    def test_move_skipped_when_plc_unreachable(self, ros_client):
        """
        When plc_sim is not reachable, gantry_command_node returns failure
        (not a crash/hang). Useful for smoke-testing node startup without hardware.

        Skip this test if plc_sim IS reachable — it would succeed rather than fail.
        """
        plc_host = '127.0.0.1'
        plc_port = 19999  # nothing listening here

        if _plc_sim_reachable(plc_host, plc_port):
            pytest.skip('Something is listening on the unreachable port — test invalid')

        # We can't easily reconfigure the running node's params here, so this test
        # documents expected behavior. To run it in isolation, start gantry_command_node
        # with --ros-args -p plc_host:=127.0.0.1 -p plc_port:=19999 and no plc_sim.
        pytest.skip('Reconfigure node with bad plc_host/port to exercise this path')
