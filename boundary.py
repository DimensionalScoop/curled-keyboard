"""Find the boundary of an array that can contain None elements

Also figure out the normal of the boundary.
"""

import numpy as np
from typing import Set, Tuple

from solid2.extensions.bosl2 import path_spread


def find_boundary(arr: np.ndarray) -> Set[Tuple[int, int]]:
    assert arr.size > 0
    # try:
    #     assert np.isnan(arr).all() is False
    # except TypeError:
    #     pass

    rows, cols = arr.shape
    real_boundary = set()  # the final boundary indices
    cb = set()  # the current candidate boundary indices
    trash = set()  # all items already considered

    # Initialize candidate_boundary with the bounds of the array
    for i in range(rows):
        cb.add((i, 0))  # Left edge
        cb.add((i, cols - 1))  # Right edge
    for j in range(1, cols - 1):
        cb.add((0, j))  # Top edge
        cb.add((rows - 1, j))  # Bottom edge

    adjacent_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while len(cb):
        i, j = cb.pop()
        trash.add((i, j))
        if arr[i, j] is not None:
            # If it's an object, add it to the real boundary
            real_boundary.add((i, j))
        else:
            # If it's None, move the candidate boundary inwards
            for dx, dy in adjacent_directions:
                if 0 <= i + dx < rows and 0 <= j + dy < cols:
                    moved = (i + dx, j + dy)
                    if moved not in real_boundary and moved not in trash:
                        cb.add(moved)

    return real_boundary


def center_to_corner_array(array):
    """
    >>> center_to_corner_array([[1,2],[4,5]])
    [[1,1,2,2],[1,1,2,2,],[4,4,5,5],[4,4,5,5]]]
    """
    return np.repeat(np.repeat(array, 2, axis=-1), 2, axis=0)


def corner_to_center_idx(x, y):
    i, j = x // 2, y // 2
    dx, dy = x % 2 * 2 - 1, y % 2 * 2 - 1
    return i, j, dx, dy


def sort_idx_to_be_continous(indices: set):
    indices = indices.copy()
    sorted = [indices.pop()]
    while indices:
        head_x, head_y = sorted[-1]
        adjecent = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dx, dy in adjecent:
            candidate = (head_x + dx, head_y + dy)
            if candidate in indices:
                indices.remove(candidate)
                sorted.append(candidate)
                break
        else:
            raise ValueError(f"""can't find a neighbour for {head_x, head_y}. Is the boundary continuous?
            indices:
            {indices}
            sorted:
            {sorted}
                             """)
    return sorted
