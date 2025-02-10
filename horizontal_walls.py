from solid2 import *  # noqa: F403
# from solid2.extensions.bosl2 import *  # noqa: F403

# import solid2.extensions.bosl2 as bosl  # noqa: F403
import solid2 as sp
from solid2.extensions.bosl2 import TOP, bounding_box, minkowski_difference, xcyl

from mommy import render, render_all
from scad_helpers import attachable_cube

import numpy as np
from numpy import array as ar


eps = 0.01
inf = 70

x = 17
z = 8.5


def fill_center(transforms, x, y, h):
    return hull()(*_get_posts(transforms, x, y, h))


def _get_posts(transforms, x, y, h):
    assert len(transforms) == 4
    post = cylinder(h, r=eps)

    for trf, (dx, dy) in zip(transforms, ((1, 1), (-1, 1), (-1, -1), (1, -1))):
        at_edge = post.forward(dx * x / 2).right(dy * y / 2).down(z / 2)
        yield trf(at_edge)


transforms = [
    lambda o: o.rotateX(20).rotateY(5).color("Pink"),
    lambda o: o.rotateX(25).rotateY(5).forward(x + 2).up(8).color("Green"),
    lambda o: o.rotateX(40).right(x + 12).forward(x + 2).up(27),
    lambda o: o.rotateX(30).right(x + 7).up(10).color("Blue"),
]


@render
def dev():
    return fill_center(transforms, x, x, z)


@render
def example():
    shape = cube(x, x, z, center=True)
    switches = [tr(shape) for tr in transforms]
    return np.sum(switches).background()


if __name__ == "__main__":
    render_all()
