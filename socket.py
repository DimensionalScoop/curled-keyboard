from solid2 import *
import numpy as np
from mommy import render_all


eps = 0.01
inf = 70

x_width = 17
z_height = 2.2
x_inner = 14
y_inner = 14.15


def _printable_wedge(x_len, y_len, h, h_box=1):
    def pos(o):
        return o.rotateX(180).left(x_len / 2).forward(y_len / 2)

    wedge = pos(square([x_len, y_len]).linear_extrude(h - h_box, scale=[1, 0]))
    wedge = wedge.down(h_box)
    box = pos(square([x_len, y_len]).linear_extrude(h_box))

    return wedge + box


def socket(h_holder=2):
    s = cube([x_width, x_width, z_height], center=True)
    switch = cube([x_inner, y_inner, inf], center=True)

    s -= switch
    holder = (
        _printable_wedge(0.95, 0.45, h_holder)
        .forward((y_inner - 0.45) / 2)
        .left((x_inner - 0.95) / 2)
    )
    holder += (
        _printable_wedge(2.6, 0.5, h_holder)
        .rotateZ(90)
        .left((x_inner - 0.5) / 2)
        .forward(0.6)
    )
    holder += (
        _printable_wedge(1.75, 0.95, h_holder)
        .rotateZ(90)
        .left((x_inner - 0.95) / 2)
        .back((y_inner - 1.75) / 2)
    )
    holder += holder.mirrorX()
    holder = holder.up((z_height) / 2)

    return (s + holder).rotateZ(-90)


def dummy():
    s = cube([x_width, x_width, z_height], center=True)
    return s


def supporter():
    holder = cylinder(3.2 + 2, d=5.3 + 0.5, _fn=30).down(2)
    cutout = cylinder(3.2 + eps, d=5.3, _fn=30).down(eps / 2)

    s = holder - cutout
    s = s.down(3.2 + z_height)

    h = 10
    box = (
        cube([5, 2, h])
        .left(x_inner / 2 - 5.1 - 0.35)
        .forward(-2 + y_inner / 2 - 0.8)
        .down(h + z_height - 4)
    )
    return s + box


def socket_grid(grid, use_dummy=True):
    if use_dummy:
        shape = dummy()
    else:
        shape = socket()
    switches = [tr(shape) for tr in grid.flatten()]
    return np.sum(switches).color("Gray")


def example():
    # import_stl("./switch-mount.stl")
    # shape = import_stl("./switch-mount.stl").down(z_height / 2)
    return socket() + supporter() + dummy().debug()


if __name__ == "__main__":
    render_all(example())
