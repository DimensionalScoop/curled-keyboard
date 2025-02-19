from solid2 import *  # noqa: F403
from solid2.extensions.bosl2 import bounding_box, xcyl

from mommy import render_all


eps = 0.01
inf = 70


def make_wall(
    roof,
    base_offset,
    thickness=2,
    fill_blocker=None,
):
    walls = simple_walls_cutoff(roof, base_offset, thickness).color("Gray")
    fill = gapfill(roof, base_offset, thickness, fill_blocker).color("Lime")
    return walls + fill


def simple_walls(roof, base_offset, thickness=2):
    """Create vertical walls around the `roof`.
    Walls go up to the maximum height of the roof."""
    base = roof.projection()
    solid_walls = (
        base.offset(thickness).linear_extrude(inf, convexity=10).down(base_offset)
    )
    cutout = base.linear_extrude(inf, convexity=10).down(base_offset)
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
    wall_base_3d = wall_base.linear_extrude(eps, convexity=10)

    # covers everything, even stuff we don't want to fill
    glob = hull()(wall_base_3d, roof)
    # thicken towards the bottom to make manifold
    glob = minkowski()(glob, cylinder(eps, eps, 0))

    # don't add material outside of the walls
    glob &= (roof + walls).projection().linear_extrude(inf, convexity=5).down(eps)

    if fill_blocker is not None:
        # anywhere where walls might exist, gapfill is allowed to be
        glob -= fill_blocker - wall_base.offset(eps).linear_extrude(inf, convexity=5)
    else:
        glob -= (
            roof.projection()
            .offset(delta=eps)
            .linear_extrude(inf, convexity=5)
            .down(eps)
        )

    return glob


def _create_base(roof, h=eps):
    return roof.projection().linear_extrude(h)


def example():
    roof = cube([17, 17, 8.5]).rotateX(30)
    roof -= xcyl(17, 8).up(10)
    cleanup = cube([17, 17, inf]).down(inf / 2).rotateX(30)
    # roof += cylinder(h=5, r=9).forward(15)

    # walls = simple_walls_cutoff(roof, 5).color("Gray")
    # fill = gapfill(roof, 5, 2, cleanup).color("Lime")

    base_height = 5
    wall_thickness = 2
    walls = make_wall(roof, base_height, wall_thickness, cleanup)

    return roof + walls


if __name__ == "__main__":
    ex = example()
    render_all(ex)
