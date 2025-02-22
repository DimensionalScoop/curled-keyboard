from solid2 import *  # noqa: F403
import numpy as np

from mommy import render_all
import socket


eps = 0.01
inf = 70


def fill_center(transforms, x, y, h):
    return hull()(*_get_posts(transforms, x, y, h))


def fill_edge(transforms, x, y, h, dir="x"):
    return hull()(*_get_edge_posts(transforms, x, y, h, dir))


def _get_posts(transforms, x, y, h):
    """Expects the transforms in this order:
    grid[x,y],
    grid[x, y + 1],
    grid[x + 1, y + 1],
    grid[x + 1, y],
    """
    assert len(transforms) == 4
    post = cylinder(h, r=eps)

    for trf, (dx, dy) in zip(transforms, ((1, 1), (-1, 1), (-1, -1), (1, -1))):
        at_edge = post.forward(dx * x / 2).right(dy * y / 2).down(socket.z_height / 2)
        yield trf(at_edge)


def _get_edge_posts(transforms, x, y, h, dir="x"):
    assert len(transforms) == 2
    post = cylinder(h, r=eps)

    match dir:
        case "y":
            for dx, trf in zip((-1, 1), transforms[::-1]):
                for dy in (-1, 1):
                    at_edge = (
                        post.forward(dx * x / 2)
                        .right(dy * y / 2)
                        .down(socket.z_height / 2)
                    )
                    yield trf(at_edge)
        case "x":
            for dy, trf in zip((-1, 1), transforms[::-1]):
                for dx in (-1, 1):
                    at_edge = (
                        post.forward(dx * x / 2)
                        .right(dy * y / 2)
                        .down(socket.z_height / 2)
                    )
                    yield trf(at_edge)
        case _:
            raise NotImplementedError()


demo_transforms = np.empty((6, 4), dtype=object)
for x in range(demo_transforms.shape[0]):
    for y in range(demo_transforms.shape[1]):

        def _transform(o, x=x, y=y):
            return (
                # .rotateX(y / 4 * 90)
                # o.right((socket.x_width + 2) * x)
                # .forward((socket.x_width + 2) * y)
                o.down(50)
                .rotateX(23 * y - 20)
                .up(50)
                .down(400)
                .rotateY(-x * 3 + 8)
                .up(400)
            )

        demo_transforms[x, y] = _transform


def _key_fill(grid, x, y):
    this_key = grid[x, y]
    for dir in ("right", "down", "across"):
        try:
            match dir:
                case "right":
                    next_key = grid[x + 1, y]
                    yield fill_edge(
                        (this_key, next_key),
                        socket.x_width,
                        socket.x_width,
                        socket.z_height,
                        "x",
                    )
                case "down":
                    next_key = grid[x, y + 1]
                    yield fill_edge(
                        (this_key, next_key),
                        socket.x_width,
                        socket.x_width,
                        socket.z_height,
                        "y",
                    )
                case "across":
                    keys = (
                        this_key,
                        grid[x, y + 1],
                        grid[x + 1, y + 1],
                        grid[x + 1, y],
                    )
                    yield fill_center(
                        keys, socket.x_width, socket.x_width, socket.z_height
                    )
        except IndexError:
            pass


def fill_between_switches(grid):
    gap_fill = []
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            gap_fill.extend(_key_fill(grid, x, y))
    return union()(*gap_fill)


def make_switches(grid, use_dummy=True):
    if use_dummy:
        shape = cube(socket.x_width, socket.x_width, socket.z_height, center=True)
    else:
        shape = import_stl("./switch-mount.stl").down(socket.z_height / 2)
    switches = [tr(shape) for tr in grid.flatten()]
    return np.sum(switches).color("Gray")


def example():
    switches = socket.socket_grid(demo_transforms, False)
    switch_fill = fill_between_switches(demo_transforms)
    return switches + switch_fill


if __name__ == "__main__":
    ex = example()
    render_all(ex)
