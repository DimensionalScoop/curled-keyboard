from solid2 import *  # noqa: F403
import solid2 as sp

from mommy import render, render_all

from types import SimpleNamespace
import numpy as np

import chain_wall
import horizontal_walls
import socket


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


def remove_above(body, tool):
    """remove all mass of the body that is in or above the tool"""
    # XXX: only works for convex shapes
    return body - hull()(tool, tool.up(inf))


def create_key_support(place):
    to_bottom = lambda o: o.down(z_height / 2)
    column = place(to_bottom(cylinder(z_height, r=2)))

    # head = place(sphere(0.5)).color("Green")
    head = socket.socket().up(z_height / 2).down(eps).projection(cut=True)
    head = head.offset(delta=-0.5)
    head = to_bottom(head.linear_extrude(eps))
    head = place(head)

    head = hull()(head, column)

    plate = place(to_bottom(cylinder(eps, r=2)))
    stem = plate.projection().linear_extrude(inf)
    stem = stem.down(inf / 2)
    stem = remove_above(stem, place(socket.dummy()))

    return column + stem + head


def example_support():
    sample_transform = grid[3, 3]

    socket_ = socket.socket_grid(np.array([sample_transform]), False)

    support = create_key_support(sample_transform)

    return socket_.debug() + support.color("DarkBlue")


@render
def example():
    switches = socket.socket_grid(grid, False)
    fill = horizontal_walls.fill_between_switches(grid)

    wall = chain_wall.create_switch_wall(grid, 1)

    return wall + switches + fill


if __name__ == "__main__":
    render_all()
