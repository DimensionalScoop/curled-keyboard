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
