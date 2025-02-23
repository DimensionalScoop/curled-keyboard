from solid2 import *  # noqa: F403
from solid2.extensions.bosl2 import chain_hull

from mommy import render_all

import numpy as np

import horizontal_walls
import socket
import boundary

# XXX: The git version of openscad (~ Feb 2025) has a correct preview (F5) of this file, but renders (F6) the geometry incorrectly

eps = 0.01
inf = 70


def get_outer_boundary(grid, thickness=3):
    corner_grid = boundary.center_to_corner_array(grid)
    outer_corners_unsorted = boundary.find_boundary(corner_grid)
    outer_corners = boundary.sort_idx_to_be_continous(outer_corners_unsorted)
    bound = []
    for i, j in outer_corners:
        x, y, dx, dy = boundary.corner_to_center_idx(i, j)

        def _transform(o, x=x, y=y, dx=dx, dy=dy):
            shift = socket.x_width / 2 + thickness
            o = o.forward(shift * dy).right(shift * dx)
            return grid[x, y](o)

        bound.append(_transform)
    return bound


def _socket_facing_wall(grid, thickness, offset):
    boundary = get_outer_boundary(grid, thickness / 2 + offset)

    post = cylinder(socket.z_height, r=thickness / 2, _fn=15).down(socket.z_height / 2)
    outside_posts = [trf(post) for trf in boundary]
    outside_posts.append(outside_posts[0])
    return chain_hull()(*outside_posts).color("Orange")


def create_switch_wall(
    grid,
    thickness=3,
    height=10,
    offset=0,
    create_ledge=False,
):
    socket_wall = _socket_facing_wall(grid, thickness, offset)

    boundary = get_outer_boundary(grid, thickness / 2 + offset)
    plate = cylinder(eps, r=thickness / 2, _fn=15).down(socket.z_height / 2)
    bound_2d = [trf(plate) for trf in boundary]
    bound_2d.append(bound_2d[0])
    lower_wall_pieces = []
    for a, b in zip(bound_2d[:-1], bound_2d[1:]):
        piece_2d = hull()(a, b)
        wall = piece_2d.projection().linear_extrude(height).down(height)
        connector = hull()(piece_2d, wall)
        lower_wall_pieces.append(wall + connector)

    if create_ledge:
        ledge = _create_ledge(grid, thickness, height, offset)
    else:
        ledge = union()()

    return union()(lower_wall_pieces).color("DarkOrange") + socket_wall + ledge


def _create_ledge(grid, thickness, height, offset):
    edge = cube(2, 2, 2, center=True).down(socket.z_height / 2 + 1.35)
    inner_boundary = get_outer_boundary(grid, offset)
    ledge = [trf(edge) for trf in inner_boundary]
    ledge += [ledge[0]]
    ledge = chain_hull()(ledge).color("LimeGreen")
    # the ledge is sometimes outside the wall
    ledge -= create_switch_wall(grid, 10, inf, offset, False)
    return ledge


def _generate_example_data():
    demo_transforms = np.empty((6, 4), dtype=object)
    finger_shift = np.array([0, 0, 5, 10, 5, -2, -2]) * 3
    for x in range(demo_transforms.shape[0]):
        for y in range(demo_transforms.shape[1]):

            def _transform(o, x=x, y=y, shift=finger_shift[x]):
                return (
                    o.down(50)
                    .rotateX(23 * y - 20)
                    .up(50)
                    .down(400)
                    .rotateY(-x * 3 + 8)
                    .up(400)
                    .forward(shift)
                    .rotateZ(-3 * x)  # fan
                )

            demo_transforms[x, y] = _transform
    return demo_transforms


def example():
    grid = _generate_example_data()
    switches = socket.socket_grid(grid, False)
    fill = horizontal_walls.fill_between_switches(grid)

    wall = create_switch_wall(grid, 1)

    return wall + switches + fill


if __name__ == "__main__":
    obj = example()
    render_all(obj)
