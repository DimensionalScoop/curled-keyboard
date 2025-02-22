from solid2 import *  # noqa: F403
from solid2.extensions.bosl2 import chain_hull

from mommy import render_all

import numpy as np

import horizontal_walls
import socket
import boundary


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


def create_switch_wall(
    grid,
    thickness=3,
    height=10,
):
    boundary = get_outer_boundary(grid, thickness)

    post = cylinder(socket.z_height, r=thickness).down(socket.z_height / 2)
    outside_posts = [trf(post) for trf in boundary]
    outside_posts.append(outside_posts[0])
    switch_wall = chain_hull()(*outside_posts).color("Orange")

    plate = cylinder(eps, r=thickness).down(socket.z_height / 2)
    bound_2d = [trf(plate) for trf in boundary]
    bound_2d.append(bound_2d[0])
    lower_wall_pieces = []
    for a, b in zip(bound_2d[:-1], bound_2d[1:]):
        piece_2d = hull()(a, b)
        wall = piece_2d.projection().linear_extrude(height).down(height)
        connector = hull()(piece_2d, wall)
        lower_wall_pieces.append(wall + connector)

    return union()(lower_wall_pieces).color("DarkOrange") + switch_wall


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
