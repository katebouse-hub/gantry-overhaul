# 03 · Vision ("Skynet")

Camera-based mapping of the gridfinity board, written by the earlier Shipping Dock team
(Dawson Burgess, AI/vision lead). Its job is to tell the rest of the system **what is actually on
the grid**, so the state file can be checked against reality instead of trusted blindly.
**Status: prototype.** It detects grid lines and classifies cell colours from a still image; it does
not yet track containers or feed ROS2.

## What's in this folder

| Path | What it is |
|---|---|
| `skynet/capture_image_v2.py` | Grabs a JPEG from the camera server (`GET http://10.8.4.33:8123/capture`) with retries; saves `image.jpg`. |
| `skynet/grid_script.py` | OpenCV pipeline: mask header/footer → Canny edges → Hough lines → cluster into grid rows/cols → sample each cell's HSV → colour label. Writes `grid_mapping.json` and `debug_grid.jpg`. |
| `skynet/grid_mapping.json` | Example output: 2-D colour grid (bottom-left origin) plus home/calibration cells. |
| `sample_images/` | `clean_workspace.jpg` (input), `debug_grid.jpg` (detected lines), `with_containers.jpg`, plus photos of the printed grid and containers. |
| `docs/grid_system.md` | Original design notes: 1-inch gridfinity cells, colour-coded zones, priority rules. |
| `docs/camera_process_flow.png` | Camera/vision data-flow diagram. |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install opencv-python numpy scipy requests
cd skynet
python grid_script.py            # reads clean_workspace.jpg (copy one in from sample_images/)
python capture_image_v2.py       # only on the lab network, with the camera server running
```

Check `debug_grid.jpg`: green lines should sit on the printed grid lines. If not, adjust the Canny
thresholds (50/150), the Hough `threshold`/`minLineLength`, or the cluster distance `t=10`.
Colour ranges are in `classify_color()`; retune them for the lab lighting.

## Hardware notes

- The camera uses GenICam/Harvesters, which has no aarch64 build, so capture runs on the
  **gantry-server (x86)**, not the Jetson. The script just fetches over HTTP from that server.
- The camera-server code itself is not in this package. Ask Dawson, or check the server.

## Making it useful for the AI layer

1. Map image cells to the gantry grid (x 1–27, y 1–20). The script's row/column count and origin
   differ from `init.json`.
2. Detect containers (colour blobs 1×4 cells long) and output the same JSON schema as
   `active_pos.json` (`id`, `color`, `pos_1`, `pos_2`).
3. Expose that as a ROS2 service or MCP tool (`observe_grid`) so the agent can check the real
   board before and after each move.
4. Consider a YOLO or VLM detector once colour thresholds stop being reliable.
