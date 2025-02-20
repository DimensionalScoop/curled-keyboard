from solid2 import *  # noqa: F403
# from solid2.extensions.bosl2 import *  # noqa: F403

# import solid2.extensions.bosl2 as bosl  # noqa: F403
import solid2 as sp
from solid2.extensions.bosl2 import TOP, bounding_box, chain_hull, minkowski_difference, xcyl

from mommy import render, render_all
from scad_helpers import attachable_cube

import numpy as np
from numpy import array as ar

import horizontal_walls


eps = 0.01
inf = 70

x_width = 17
z_height = 8.5



@render
def example():
    grid = horizontal_walls.demo_transforms
    switches = horizontal_walls.make_switches(grid)
    fill = horizontal_walls.fill_between_switches(grid)
    return chain_hull()(switches)

    
    # return switches + fill


if __name__ == "__main__":
    render_all()
