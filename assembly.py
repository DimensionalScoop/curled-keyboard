from dataclasses import dataclass
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


@dataclass
class Stagger:
    x: int
    y: int
    z: int

    def array(self):
        return [self.x, self.y, self.z]


props = SimpleNamespace(
    facing_angle=-22,
    curvature_row=104 / 3,
    curvature_col=0,
    # fan=[0, 0, 30, 7, 27, 0],
    fan=np.array([0, 0, 3, 0.7, 2.7, 0]) * 1,
    staggers=[
        Stagger(0, 0, 0),  # index
        Stagger(0, 0, 0),  # index
        Stagger(0, 7.3, 1.15),  # middle
        Stagger(0, 0.75, -0.3),  # ring
        Stagger(0, -14, 1.63),  # pinky
        Stagger(0, -14, 1.63),  # pinky
    ],
    row_spacing=socket.x_width + 4,
    col_spacing=np.array([0, 0, 2, 5, 7, 0]) + socket.x_width,
    h_offset=10,
)

target_radius = 5
U = props.row_spacing * 4 / (props.curvature_row * 3 / 360)
actual_radius = U / 2 / np.pi
print(actual_radius)


grid = np.empty((6, 5), dtype=object)
for x in range(grid.shape[0]):
    height_of_ymost_edge = 0
    width_of_ymost_edge = 0
    for y in range(grid.shape[1]):
        # row tilting
        row_tilt = y * props.curvature_row + props.facing_angle
        if y == 4:
            row_tilt = 0
        row_h = height_of_ymost_edge
        height_of_ymost_edge += np.sin(np.deg2rad(row_tilt)) * props.row_spacing
        row_f = width_of_ymost_edge
        width_of_ymost_edge += np.cos(np.deg2rad(row_tilt)) * props.row_spacing

        row_trans = np.array([0, row_f, row_h])

        def _transform(o, x=x, y=y, row_tilt=row_tilt, row_trans_p=row_trans.copy()):
            return (
                o.down(socket.z_height / 2)
                .forward(props.row_spacing / 2)
                .rotateX(row_tilt)
                # .forward(-x_width * 1.5)
                # # .forward(socket.x_width * y)
                # # .rotateZ(-np.sum(props.fan[: x + 1]))
                .translate(props.staggers[x].array())
                .translate(row_trans_p)
                .right(np.sum(props.col_spacing[: x + 1]))
                .up(props.h_offset)
                # .rotateX(10 * y)
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


def keycap():
    return (
        hull()(
            cube(16.75, 16.75, eps, center=True),
            cube(13.15, 13.15, eps, center=True).up(6.4),
        )
        .up(socket.z_height / 2 + 1)
        .color("DarkRed")
    )


@render
def example():
    show_keycaps = False

    switches = socket.socket_grid(grid, False)
    fill = horizontal_walls.fill_between_switches(grid)
    offset = 0.35
    wall = chain_wall.create_switch_wall(
        grid, 1.84, 8, offset=offset, create_ledge=True
    )
    wall -= (switches + fill).down(0.3)
    wall_cutout = chain_wall.create_switch_wall(grid, 1.84 + offset * 2, 8, offset=0)

    keycaps = [trf(keycap()) for trf in grid.flatten()]

    output = switches + fill - wall_cutout + wall
    output = wall
    if show_keycaps:
        output + keycaps
    return output


if __name__ == "__main__":
    render_all()
