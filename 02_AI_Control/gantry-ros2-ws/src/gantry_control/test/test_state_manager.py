"""
Tests for state_manager_node services.

Requires state_manager_node running:
  ros2 run gantry_control state_manager_node

The live ~/.gantry/active_pos.json is backed up before each test and restored afterwards,
so running these tests on the Jetson no longer wipes the real container layout.

Run with: colcon test --packages-select gantry_control
"""

import json
import os
import shutil
import tempfile
import pytest
import rclpy
from rclpy.node import Node

from gantry_interfaces.srv import GetState, UpdateState

ACTIVE_JSON_PATH = os.path.expanduser('~/.gantry/active_pos.json')
SERVICE_TIMEOUT = 5.0


@pytest.fixture(scope='module')
def ros_client():
    rclpy.init()
    node = rclpy.create_node('test_state_manager_client')
    yield node
    node.destroy_node()
    rclpy.shutdown()


@pytest.fixture(autouse=True)
def reset_active_json():
    """Restore active_pos.json to a known state before each test."""
    known_state = {
        'containers': [
            {
                'id': 'C001',
                'color': 'black',
                'pos_1': {'x': 1, 'y': 1, 'z': 1},
                'pos_2': {'x': 1, 'y': 4, 'z': 1},
            }
        ]
    }
    os.makedirs(os.path.dirname(ACTIVE_JSON_PATH), exist_ok=True)
    backup = None
    if os.path.exists(ACTIVE_JSON_PATH):
        fd, backup = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        shutil.copy(ACTIVE_JSON_PATH, backup)
    with open(ACTIVE_JSON_PATH, 'w') as f:
        json.dump(known_state, f, indent=2)
    try:
        yield
    finally:
        # Put the real state back so tests never clobber the live layout.
        if backup:
            shutil.move(backup, ACTIVE_JSON_PATH)


class TestGetState:
    def test_service_available(self, ros_client):
        client = ros_client.create_client(GetState, 'get_gantry_state')
        available = client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)
        assert available, 'get_gantry_state service not available — is state_manager_node running?'

    def test_returns_valid_json(self, ros_client):
        client = ros_client.create_client(GetState, 'get_gantry_state')
        assert client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)

        future = client.call_async(GetState.Request())
        rclpy.spin_until_future_complete(ros_client, future, timeout_sec=SERVICE_TIMEOUT)

        result = future.result()
        assert result is not None
        assert result.success

        state = json.loads(result.state_json)
        assert 'containers' in state

    def test_contains_known_container(self, ros_client):
        client = ros_client.create_client(GetState, 'get_gantry_state')
        assert client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)

        future = client.call_async(GetState.Request())
        rclpy.spin_until_future_complete(ros_client, future, timeout_sec=SERVICE_TIMEOUT)

        state = json.loads(future.result().state_json)
        ids = [c['id'] for c in state['containers']]
        assert 'C001' in ids


class TestUpdateState:
    def test_service_available(self, ros_client):
        client = ros_client.create_client(UpdateState, 'update_gantry_state')
        available = client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)
        assert available, 'update_gantry_state service not available — is state_manager_node running?'

    def test_update_known_container(self, ros_client):
        client = ros_client.create_client(UpdateState, 'update_gantry_state')
        assert client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)

        req = UpdateState.Request()
        # Source matches C001 from reset_active_json fixture
        req.src_x1, req.src_y1, req.src_z1 = 1, 1, 1
        req.src_x2, req.src_y2, req.src_z2 = 1, 4, 1
        # New destination (empty row x=9)
        req.dst_x1, req.dst_y1, req.dst_z1 = 9, 1, 1
        req.dst_x2, req.dst_y2, req.dst_z2 = 9, 4, 1

        future = client.call_async(req)
        rclpy.spin_until_future_complete(ros_client, future, timeout_sec=SERVICE_TIMEOUT)

        result = future.result()
        assert result is not None
        assert result.success, f'Update failed: {result.message}'

        # Verify JSON file updated on disk
        with open(ACTIVE_JSON_PATH) as f:
            state = json.load(f)
        c = next(c for c in state['containers'] if c['id'] == 'C001')
        assert c['pos_1']['x'] == 9
        assert c['pos_2']['x'] == 9
        assert c['pos_2']['y'] == 4

    def test_update_unknown_position_fails(self, ros_client):
        client = ros_client.create_client(UpdateState, 'update_gantry_state')
        assert client.wait_for_service(timeout_sec=SERVICE_TIMEOUT)

        req = UpdateState.Request()
        req.src_x1, req.src_y1, req.src_z1 = 99, 99, 1
        req.src_x2, req.src_y2, req.src_z2 = 99, 102, 1
        req.dst_x1, req.dst_y1, req.dst_z1 = 9, 1, 1
        req.dst_x2, req.dst_y2, req.dst_z2 = 9, 4, 1

        future = client.call_async(req)
        rclpy.spin_until_future_complete(ros_client, future, timeout_sec=SERVICE_TIMEOUT)

        result = future.result()
        assert result is not None
        assert not result.success
