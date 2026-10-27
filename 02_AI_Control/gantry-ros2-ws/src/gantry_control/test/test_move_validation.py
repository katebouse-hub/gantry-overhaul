"""Unit tests for move_validation (pure Python; no ROS nodes needed)."""

from gantry_control.move_validation import validate_move

STATE = {
    'containers': [
        {'id': 'C001', 'color': 'black',
         'pos_1': {'x': 1, 'y': 1, 'z': 1}, 'pos_2': {'x': 1, 'y': 4, 'z': 1}},
        {'id': 'C002', 'color': 'yellow',
         'pos_1': {'x': 2, 'y': 5, 'z': 1}, 'pos_2': {'x': 2, 'y': 8, 'z': 1}},
    ]
}


def move(src, dst):
    keys = ('x1', 'y1', 'z1', 'x2', 'y2', 'z2')
    args = {f'src_{k}': v for k, v in zip(keys, src)}
    args.update({f'dst_{k}': v for k, v in zip(keys, dst)})
    return args


def test_valid_move():
    assert validate_move(STATE, move((1, 1, 1, 1, 4, 1), (9, 1, 1, 9, 4, 1))) is None


def test_valid_rotation_to_x_axis():
    assert validate_move(STATE, move((1, 1, 1, 1, 4, 1), (10, 10, 1, 13, 10, 1))) is None


def test_unknown_source():
    assert 'No container' in validate_move(STATE, move((5, 5, 1, 5, 8, 1), (9, 1, 1, 9, 4, 1)))


def test_off_grid():
    assert 'outside the grid' in validate_move(STATE, move((1, 1, 1, 1, 4, 1), (0, 0, 0, 4, 0, 0)))


def test_wrong_length():
    assert '4 cells apart' in validate_move(STATE, move((1, 1, 1, 1, 4, 1), (9, 1, 1, 9, 5, 1)))


def test_overlap():
    assert 'C002' in validate_move(STATE, move((1, 1, 1, 1, 4, 1), (2, 6, 1, 2, 9, 1)))


def test_moving_onto_own_cells_is_allowed():
    assert validate_move(STATE, move((1, 1, 1, 1, 4, 1), (1, 2, 1, 1, 5, 1))) is None
