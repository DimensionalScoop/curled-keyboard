"""Helper functions for working with solidpython2 and openscad"""

import solid2 as sp
from datetime import datetime

REGISTRY = dict()


def render(func=None, **kwargs):
    """Decorator that registers a function returing an openscad geometry for rendering"""

    def wrapper(func):
        REGISTRY[func.__name__] = func(**kwargs)
        return func

    # when decorator is used without calling it `@render()`
    if func is not None:
        return wrapper(func)

    return wrapper


def render_all(*objects, verbose=True, **kwargs):
    """Calls all registered functions and converts their returns to openscad.
    Passes additional `objects` to the converter.
    """
    tree = sp.union()()  # empty object
    for _, obj_generator in REGISTRY.items():
        tree += obj_generator(**kwargs)
    for obj in objects:
        tree += obj
    sp.scad_render_to_file(tree)

    if verbose:
        time = datetime.now().strftime("%H:%M:%S")
        print(f"[{time}]\t render done\n")
