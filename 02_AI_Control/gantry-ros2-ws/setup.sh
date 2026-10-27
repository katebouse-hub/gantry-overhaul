#!/bin/bash
# Source ROS2, venv packages, and workspace overlay.
# Usage: source setup.bash

source /opt/ros/jazzy/setup.sh

if [ -d ".venv/lib" ]; then
    VENV_SITE_PACKAGES=$(find .venv/lib -type d -name "site-packages" 2>/dev/null | head -1)
    if [ -n "$VENV_SITE_PACKAGES" ]; then
        export PYTHONPATH="$VENV_SITE_PACKAGES:$PYTHONPATH"
    fi
fi

if [ -f install/setup.sh ]; then
    source install/setup.sh
fi

echo "ROS2: jazzy | venv: ${VENV_SITE_PACKAGES:-none} | workspace: $([ -f install/setup.sh ] && echo sourced || echo not built)"
