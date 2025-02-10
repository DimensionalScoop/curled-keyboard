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


def make_wall(
    roof,
    base_offset,
    thickness=2,
    fill_blocker=None,
):
    walls = simple_walls_cutoff(roof, base_offset, thickness).color("Gray")
    gapfill = gapfill(roof, base_offset, thickness, fill_blocker).color("Lime")
    return walls + gapfill


def _vertical_walls(roof, base_offset, thickness=2):
    raise NotImplementedError()
    base = _create_base(roof).down(base_offset)

    bb = bounding_box(excess=thickness)(roof, base)

    wallmaker = cylinder(eps, d=thickness, _fn=6)
    wallmaker = sphere(thickness)
    closed_shell = minkowski()(roof, wallmaker) - roof
    base_cutout = _create_base(roof, inf).down(base_offset) & bb

    return closed_shell - base_cutout


def simple_walls(roof, base_offset, thickness=2):
    """Create vertical walls around the `roof`.
    Walls go up to the maximum height of the roof."""
    base = roof.projection()
    solid_walls = base.offset(thickness).linear_extrude(inf).down(base_offset)
    cutout = base.linear_extrude(inf).down(base_offset)
    thin_walls = solid_walls - cutout
    bb = bounding_box(excess=thickness)(roof + base).down(thickness)

    return thin_walls & bb


def simple_walls_cutoff(roof, base_offset, thickness=2):
    """simple_walls, but cut off at the base of the object."""
    walls = simple_walls(roof, base_offset, thickness)
    bb = bounding_box(excess=thickness + eps)(roof).up(thickness + eps)

    return walls - bb


def gapfill(
    roof,
    base_offset,
    thickness=2,
    fill_blocker=None,
):
    """Optional `cleanup` object that indicates where gaps should not be filled."""

    walls = simple_walls_cutoff(roof, base_offset, thickness)
    wall_base = walls.projection()
    wall_base_3d = wall_base.linear_extrude(eps)

    # covers everything, even stuff we don't want to fill
    glob = hull()(wall_base_3d, roof)
    # thicken towards the bottom to make manifold
    glob = minkowski()(glob, cylinder(eps, eps, 0))

    # don't add material outside of the walls
    glob &= (roof + walls).projection().linear_extrude(inf).down(eps)

    if fill_blocker is not None:
        # anywhere where walls might exist, gapfill is allowed to be
        glob -= fill_blocker - wall_base.offset(eps).linear_extrude(inf)
    else:
        glob -= roof.projection().offset(delta=eps).linear_extrude(inf).down(eps)

    return glob


def _make_printable():
    raise NotImplementedError()
    fill_without_walls = glob  # - wall_base.linear_extrude(inf).down(-eps)
    bottom_surface = fill_without_walls.down(eps).projection(cut=True)

    # make a stair case
    supports = union()()
    for z in np.arange(0, 5):
        step = bottom_surface.offset(delta=-z).linear_extrude(z).down(z)
        supports += step

    # h = 4
    # printable_round = cylinder(h, 0, 3)
    # supports = (
    #     minkowski_difference()(bottom_surface, printable_round)
    #     # .linear_extrude(eps)
    #     # .up(eps / 2)
    # ).down(h)


def _create_base(roof, h=eps):
    return roof.projection().linear_extrude(h)


@render
def example():
    roof = cube([17, 17, 8.5]).rotateX(30)
    roof -= xcyl(17, 8).up(10)
    cleanup = cube([17, 17, inf]).down(inf / 2).rotateX(30)
    # roof += cylinder(h=5, r=9).forward(15)

    walls = simple_walls_cutoff(roof, 5).color("Gray")
    fill = gapfill(roof, 5, 2, cleanup).color("Lime")

    return fill + roof + walls


if __name__ == "__main__":
    render_all()
