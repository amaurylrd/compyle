import itertools
from collections.abc import Callable, Generator
from typing import Any, TypeVar


class __Default:  # pylint: disable=invalid-name
    pass


DEFAULT: Any = __Default()
"""
This object represents a default value for factories.
This allows the default to be hidden from the signature and for ``None`` to be specified as a value.
"""

T = TypeVar("T")  # pylint: disable=invalid-name


def sequence(func: Callable[[int], T]) -> Generator[T, None, None]:
    """Generates a sequence of values from a sequence of integers starting at zero,
    passed through the callable, which must take an integer argument.

    Args:
        func: The function to generate the sequence with.

    Returns:
        A generator that yields the result of calling the function with the integer.
    """
    return (func(n) for n in itertools.count())
