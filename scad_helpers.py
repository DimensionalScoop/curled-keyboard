import solid2 as sp
import solid2.extensions.bosl2 as bosl

from typing import Callable, Optional
import inspect


def _has_parameter(callable_obj, param_name):
    """
    Check if a callable accepts a parameter with the given name.

    Args:
        callable_obj: The function or method to check
        param_name: Name of the parameter to look for

    Returns:
        bool: True if the parameter exists, False otherwise
    """
    try:
        signature = inspect.signature(callable_obj)
        return param_name in signature.parameters
    except ValueError:
        return False


def attachable_cube(bb_size: Optional[list] = None):
    """Decorate a geometry function to have attachments like a cube.

    If the function to be decorated takes an argument called `bb_size`, the parameter `bb_size` is passed into the function.

    If `bb_size` is None and the function to be decorated has an argument called `size`, this parameter is used as the bounding box size.
    """

    # explicitly tell the linter that anything goes
    def decorator(func: Callable) -> Callable:
        def wrapper(
            *args,
            anchor=bosl.CENTER,
            spin=0,
            orient=bosl.UP,
            **kwargs,
        ):
            attachment_size = bb_size
            if attachment_size is None:
                try:
                    attachment_size = kwargs["size"]
                except KeyError:
                    raise Exception("did not provide a size for the attachment!")
            attachment = bosl.attachable(anchor, spin, orient, size=attachment_size)
            if _has_parameter(func, "bb_size"):
                kwargs["bb_size"] = attachment_size
            return attachment(func(*args, **kwargs), sp.children())

        return wrapper

    return decorator
