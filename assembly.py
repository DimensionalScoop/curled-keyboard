from solid2 import *  # noqa: F403
# from solid2.extensions.bosl2 import *  # noqa: F403

# import solid2.extensions.bosl2 as bosl  # noqa: F403
import solid2 as sp
from solid2.extensions.bosl2 import (
    TOP,
    bounding_box,
    chain_hull,
    minkowski_difference,
    xcyl,
)

from mommy import render, render_all
from scad_helpers import attachable_cube

from types import SimpleNamespace
import numpy as np
from numpy import array as ar

import horizontal_walls


eps = 0.01
inf = 70

x_width = 17
z_height = 8.5


props = SimpleNamespace(
    curvature_row=0,
    curvature_col=0,
)


grid = np.empty((6, 4), dtype=object)
for x in range(grid.shape[0]):
    for y in range(grid.shape[1]):

        def _transform(o, x=x, y=y):
            return (
                o.down(50)
                .rotateX(23 * y - 20)
                .up(50)
                .down(400)
                .rotateY(-x * 3 + 8)
                .up(400)
            )

        grid[x, y] = _transform


@render
def example():
    switches = horizontal_walls.make_switches(grid)
    fill = horizontal_walls.fill_between_switches(grid)

    return switches + fill


if __name__ == "__main__":
    render_all()
