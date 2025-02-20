import pytest
import numpy as np

import boundary


def test_hole():
    grid = np.ones((4, 4))

    all_coords = np.array(np.where(grid)).T
    all_coords = {(x, y) for x, y in all_coords}
    middle = {(x, y) for x in (1, 2) for y in (1, 2)}
    bound_desired = all_coords - middle
    for m in middle:
        grid[*m] = None

    bound_actual = boundary.find_boundary(grid)
    assert bound_desired == bound_actual


channel = """
.....
bbbbb
b...b
b.bbb
b.bxb
b.bbb
"""


def test_channel():
    grid, bounds_desired, _ = ascii_to_problem(channel)

    bound_actual = boundary.find_boundary(grid)
    result_grid = np.zeros_like(grid)
    for x, y in bound_actual:
        result_grid[x, y] = 1

    assert np.all(bounds_desired == result_grid), f"""desired:
        {bounds_desired}

        actual:
        {result_grid}

        problem statement:
        {grid}
        """


simple = """
...
bbb
bxb
bbb
...
"""


def test_simple_ascii():
    grid, bounds_desired, bounds_idx_desired = ascii_to_problem(simple)

    bound_actual = boundary.find_boundary(grid)
    result_grid = np.zeros_like(grid)
    print(bound_actual)
    for x, y in bound_actual:
        result_grid[x, y] = 1

    assert np.all(bounds_desired == result_grid), f"""desired:
        {bounds_desired}

        actual:
        {result_grid}

        problem statement:
        {grid}
        """


def ascii_to_problem(string):
    string = string.replace(" ", "")
    if string[0] == "\n":
        string = string[1:]
    lines = string.split("\n")
    n_lines = len(lines)
    n_chars = len(lines[0])
    bounds = np.zeros((n_lines, n_chars))
    grid = np.zeros_like(bounds, dtype=object)
    grid[::] = None

    for x, line in enumerate(string.split("\n")):
        for y, char in enumerate(line):
            match char:
                case "x":
                    grid[x, y] = 1
                case "b":
                    grid[x, y] = 1
                    bounds[x, y] = 1
                case ".":
                    continue
                case _:
                    raise ValueError(f"unknown symbol {char}")

    bounds_idx = np.array(np.where(bounds)).T
    bounds_idx = {(x.item(), y.item()) for x, y in bounds_idx}

    for x, y in bounds_idx:
        assert grid[x, y] is not None

    return grid, bounds, bounds_idx
