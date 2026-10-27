#!/bin/bash
# Self-contained launcher for the gantry MCP server.
# Called by Mastra as a subprocess — sets up the full ROS2 + venv env internally.
set -e

WS=/home/vandal/gantry/gantry-ros2-ws

source /opt/ros/jazzy/setup.bash
source "$WS/install/setup.bash"

VENV_SITE=$(find "$WS/.venv/lib" -type d -name "site-packages" 2>/dev/null | head -1)
if [ -n "$VENV_SITE" ]; then
    export PYTHONPATH="$VENV_SITE:$PYTHONPATH"
fi

exec python3 "$WS/src/gantry_control/gantry_control/gantry_mcp_server.py"
