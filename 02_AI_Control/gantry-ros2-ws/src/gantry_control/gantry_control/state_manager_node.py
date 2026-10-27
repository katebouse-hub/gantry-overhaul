import json
import os
import shutil

import rclpy
from rclpy.node import Node

from gantry_interfaces.srv import GetState, UpdateState


INIT_JSON_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..', '..', 'share',
    'gantry_control', 'config', 'init.json'
)
ACTIVE_JSON_PATH = os.path.expanduser('~/.gantry/active_pos.json')



class StateManagerNode(Node):
    def __init__(self):
        super().__init__('state_manager_node')

        self._ensure_active_json()

        self.create_service(GetState, 'get_gantry_state', self._handle_get_state)
        self.create_service(UpdateState, 'update_gantry_state', self._handle_update_state)

        self.get_logger().info(f'StateManagerNode ready. Active state: {ACTIVE_JSON_PATH}')

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------

    def _ensure_active_json(self):
        os.makedirs(os.path.dirname(ACTIVE_JSON_PATH), exist_ok=True)
        if not os.path.exists(ACTIVE_JSON_PATH):
            init_path = self._resolve_init_path()
            if init_path:
                shutil.copy(init_path, ACTIVE_JSON_PATH)
                self.get_logger().info(f'Bootstrapped active_pos.json from {init_path}')
            else:
                with open(ACTIVE_JSON_PATH, 'w') as f:
                    json.dump({'containers': []}, f, indent=2)
                self.get_logger().warn('init.json not found — wrote empty active_pos.json')

    def _resolve_init_path(self):
        candidates = [
            INIT_JSON_PATH,
            os.path.join(os.path.dirname(__file__), '..', 'config', 'init.json'),
        ]
        for p in candidates:
            resolved = os.path.normpath(p)
            if os.path.exists(resolved):
                return resolved
        return None

    # ------------------------------------------------------------------
    # Service handlers
    # ------------------------------------------------------------------

    def _handle_get_state(self, request, response):
        try:
            with open(ACTIVE_JSON_PATH, 'r') as f:
                response.state_json = f.read()
            response.success = True
            response.message = ''
        except Exception as e:
            response.success = False
            response.state_json = ''
            response.message = str(e)
        return response

    def _handle_update_state(self, request, response):
        try:
            with open(ACTIVE_JSON_PATH, 'r') as f:
                state = json.load(f)

            matched = False
            for container in state.get('containers', []):
                if self._pos_match(container, request):
                    container['pos_1'] = {
                        'x': request.dst_x1,
                        'y': request.dst_y1,
                        'z': request.dst_z1,
                    }
                    container['pos_2'] = {
                        'x': request.dst_x2,
                        'y': request.dst_y2,
                        'z': request.dst_z2,
                    }
                    matched = True
                    self.get_logger().info(
                        f"Container '{container.get('id', '?')}' moved to "
                        f"({request.dst_x1},{request.dst_y1},{request.dst_z1})"
                        f"->({request.dst_x2},{request.dst_y2},{request.dst_z2})"
                    )
                    break

            if not matched:
                response.success = False
                response.message = (
                    f'No container at src position '
                    f'({request.src_x1},{request.src_y1},{request.src_z1})'
                    f'->({request.src_x2},{request.src_y2},{request.src_z2})'
                )
                return response

            with open(ACTIVE_JSON_PATH, 'w') as f:
                json.dump(state, f, indent=2)

            response.success = True
            response.message = ''
        except Exception as e:
            response.success = False
            response.message = str(e)
        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pos_match(container, request) -> bool:
        p1 = container['pos_1']
        p2 = container['pos_2']
        return (
            int(p1['x']) == request.src_x1
            and int(p1['y']) == request.src_y1
            and int(p1['z']) == request.src_z1
            and int(p2['x']) == request.src_x2
            and int(p2['y']) == request.src_y2
            and int(p2['z']) == request.src_z2
        )


def main(args=None):
    rclpy.init(args=args)
    node = StateManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
