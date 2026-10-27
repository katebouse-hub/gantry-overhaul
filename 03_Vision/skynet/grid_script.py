import cv2
import numpy as np
import json
from scipy.cluster.hierarchy import fclusterdata


def classify_color(mean_hsv):
    """
    Classify the average HSV color into one of the zones.
    Ranges are approximate; tune based on your image's lighting/colors.
    """
    h, s, v = mean_hsv
    if v < 60:  # Dark
        return "black"
    if s < 40:  # Low saturation
        return "white"
    if 90 < h < 140:  # Blue hues
        return "blue"
    if (0 <= h < 10) or (170 < h <= 180):  # Red hues
        return "red"
    if 10 < h < 25:  # Orange hues
        return "orange"
    if 25 < h < 40:  # Yellow hues
        return "yellow"
    return "unknown"


# Load the image
img = cv2.imread("clean_workspace.jpg")
if img is None:
    raise ValueError("Image not found. Check the file path.")

cv2.rectangle(img, (0, 0), (1280, 30), 0, -1)
cv2.rectangle(img, (0, 970), (1280, 1024), 0, -1)
cv2.imwrite("debug_cover.jpg", img)

# Convert to HSV for color classification
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Convert to grayscale for edge detection
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(gray, (9, 9), 0)

# Edge detection with Canny
edges = cv2.Canny(blurred, 50, 150)

# Dilate edges slightly to connect broken lines
kernel = np.ones((3, 3), np.uint8)
dilated = cv2.dilate(edges, kernel, iterations=1)

# Detect lines with Probabilistic Hough Transform
lines = cv2.HoughLinesP(
    dilated, rho=1, theta=np.pi / 180, threshold=50, minLineLength=20, maxLineGap=10
)

if lines is None:
    raise ValueError("No lines detected. Adjust thresholds or check image.")

# Extract line coordinates
h_lines = []  # Horizontal
v_lines = []  # Vertical
for line in lines:
    x1, y1, x2, y2 = line[0]
    if abs(y1 - y2) < abs(x1 - x2):
        h_lines.append((x1, y1, x2, y2))
    else:
        v_lines.append((x1, y1, x2, y2))

# Cluster horizontal lines by y-position (average y for each line)
if h_lines:
    h_ys = [(y1 + y2) / 2 for x1, y1, x2, y2 in h_lines]
    clusters_h = fclusterdata(
        np.array(h_ys)[:, np.newaxis], t=10, criterion="distance", metric="euclidean"
    )
    unique_ys = sorted(
        [
            np.mean([h_ys[k] for k in range(len(h_ys)) if clusters_h[k] == i])
            for i in set(clusters_h)
        ]
    )
else:
    raise ValueError("No horizontal lines detected.")

# Cluster vertical lines by x-position (average x for each line)
if v_lines:
    v_xs = [(x1 + x2) / 2 for x1, y1, x2, y2 in v_lines]
    clusters_v = fclusterdata(
        np.array(v_xs)[:, np.newaxis], t=10, criterion="distance", metric="euclidean"
    )
    unique_xs = sorted(
        [
            np.mean([v_xs[k] for k in range(len(v_xs)) if clusters_v[k] == i])
            for i in set(clusters_v)
        ]
    )
else:
    raise ValueError("No vertical lines detected.")

# Now unique_ys and unique_xs define the grid boundaries
num_rows = len(unique_ys) - 1
num_cols = len(unique_xs) - 1
print(f"Detected grid: {num_rows} rows x {num_cols} columns")

# Create the grid map (top-left is image (0,0); we'll remap to bottom-left as (0,0) later if needed)
grid = [[None for _ in range(num_cols)] for _ in range(num_rows)]

for i in range(num_rows):
    for j in range(num_cols):
        # Calculate center of the cell
        cx = int((unique_xs[j] + unique_xs[j + 1]) / 2)
        cy = int((unique_ys[i] + unique_ys[i + 1]) / 2)

        # Sample a small central patch to avoid lines/objects (adjust size if cells are small)
        patch_size = 5
        patch = hsv_img[
            max(0, cy - patch_size) : cy + patch_size,
            max(0, cx - patch_size) : cx + patch_size,
        ]

        if patch.size == 0:
            grid[i][j] = "unknown"
            continue

        # Compute mean HSV
        mean_hsv = np.mean(patch, axis=(0, 1))

        # Classify
        grid[i][j] = classify_color(mean_hsv)

# Optional: Remap coordinates so bottom-left is (0,0) – reverse rows
grid = grid[::-1]  # Flip vertically

# Pick 3 squares for calibration (assuming bottom-left origin now)
# Home: (0,0) – bottom-left cell
# X-calibration: (1,0) – right of home
# Y-calibration: (0,1) – above home
# If out of bounds or wrong color, adjust indices manually
home_row, home_col = 0, 0
x_cal_row, x_cal_col = 0, 1
y_cal_row, y_cal_col = 1, 0

print(f"Home square (0,0): color {grid[home_row][home_col]}")
print(f"X-cal square (1,0): color {grid[x_cal_row][x_cal_col]}")
print(f"Y-cal square (0,1): color {grid[y_cal_row][y_cal_col]}")

# Save to JSON
output = {
    "grid": grid,  # 2D list of colors, rows from bottom to top now
    "num_rows": len(grid),
    "num_cols": len(grid[0]) if grid else 0,
    "home_position": {
        "row": home_row,
        "col": home_col,
        "color": grid[home_row][home_col],
    },
    "calibration_positions": [
        {"row": x_cal_row, "col": x_cal_col, "color": grid[x_cal_row][x_cal_col]},
        {"row": y_cal_row, "col": y_cal_col, "color": grid[y_cal_row][y_cal_col]},
    ],
}
with open("grid_mapping.json", "w") as f:
    json.dump(output, f, indent=4)

print("Grid mapped and saved to grid_mapping.json")

# Optional: Draw detected grid for debugging (save visualized image)
vis_img = img.copy()
for y in unique_ys:
    cv2.line(vis_img, (0, int(y)), (img.shape[1], int(y)), (0, 255, 0), 2)
for x in unique_xs:
    cv2.line(vis_img, (int(x), 0), (int(x), img.shape[0]), (0, 255, 0), 2)
cv2.imwrite("debug_grid.jpg", vis_img)
