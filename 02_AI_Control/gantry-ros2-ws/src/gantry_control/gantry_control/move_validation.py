"""
Pre-flight checks for gantry moves.  Pure Python (no ROS) so it can be unit-tested anywhere.

Coordinate convention (matches config/init.json):
  - Grid is 1-indexed: x = 1..27 (x=1 nearest the gantry), y = 1..20, z = 1 (single layer today).
  - A container is 1 cell wide and 4 cells long. pos_1 and pos_2 are the two END CELLS,
    inclusive, so a container lying along y from y=1 to y=4 is pos_1=(1,1,1), pos_2=(1,4,1).
"""

GRID_X = (1, 27)
GRID_Y = (1, 20)
GRID_Z = (1, 1)
CONTAINER_LEN = 4

_KEYS = ('x1', 'y1', 'z1', 'x2', 'y2', 'z2')


def _ends(args: dict, prefix: str):
    vals = [int(args[f'{prefix}_{k}']) for k in _KEYS]
    return tuple(vals[0:3]), tuple(vals[3:6])


def cells(p1, p2):
    """All grid cells covered by a container with end cells p1 and p2 (inclusive)."""
    (x1, y1, z1), (x2, y2, z2) = p1, p2
    return {
        (x, y, z)
        for x in range(min(x1, x2), max(x1, x2) + 1)
        for y in range(min(y1, y2), max(y1, y2) + 1)
        for z in range(min(z1, z2), max(z1, z2) + 1)
    }


def _shape_error(p1, p2, label):
    (x1, y1, z1), (x2, y2, z2) = p1, p2
    for (x, y, z) in (p1, p2):
        if not (GRID_X[0] <= x <= GRID_X[1] and GRID_Y[0] <= y <= GRID_Y[1]
                and GRID_Z[0] <= z <= GRID_Z[1]):
            return (f'{label} cell ({x},{y},{z}) is outside the grid '
                    f'(x {GRID_X[0]}-{GRID_X[1]}, y {GRID_Y[0]}-{GRID_Y[1]}, '
                    f'z {GRID_Z[0]}-{GRID_Z[1]}).')
    if z1 != z2:
        return f'{label} ends must be on the same z level.'
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    if not ((dx == CONTAINER_LEN - 1 and dy == 0) or (dy == CONTAINER_LEN - 1 and dx == 0)):
        return (f'{label} ends must be {CONTAINER_LEN} cells apart in a straight line '
                f'(end cells are inclusive, e.g. (1,1,1)->(1,4,1)); got dx={dx}, dy={dy}.')
    return None


def validate_move(state: dict, args: dict):
    """Return None if the move looks safe, otherwise a human-readable reason it was rejected."""
    try:
        src = _ends(args, 'src')
        dst = _ends(args, 'dst')
    except (KeyError, TypeError, ValueError) as e:
        return f'Missing or non-integer coordinate: {e}'

    for ends, label in ((src, 'Source'), (dst, 'Destination')):
        err = _shape_error(*ends, label)
        if err:
            return err

    containers = state.get('containers', [])

    def as_ends(c):
        return ((int(c['pos_1']['x']), int(c['pos_1']['y']), int(c['pos_1']['z'])),
                (int(c['pos_2']['x']), int(c['pos_2']['y']), int(c['pos_2']['z'])))

    moving = None
    for c in containers:
        if as_ends(c) == src:
            moving = c
            break
    if moving is None:
        return (f'No container has pos_1={src[0]} and pos_2={src[1]}. '
                'Call get_gantry_state and copy the ends exactly.')

    dst_cells = cells(*dst)
    for c in containers:
        if c is moving:
            continue
        if dst_cells & cells(*as_ends(c)):
            return f"Destination overlaps container {c.get('id', '?')}."
    return None
