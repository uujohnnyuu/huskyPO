# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO


from __future__ import annotations

from functools import wraps

from . import Element, Elements


def dynamic(func):
    """
    Dynamic element decorator for page objects.
    Applies to any dynamic elements that return an Element or Elements.

    Usage::

        from huskypo import dynamic

        @dynamic
        def my_element(self, par):
            return Element(By.IOS_PREDICATE, 'name CONTAINS "{par}"')

        # You can NOT set the dynamic element without using the dynamic decorator,
        # as it will not trigger the descriptor method.
        # The following is incorrect:
        def my_element(self, par):
            return Element(By.IOS_PREDICATE, 'name CONTAINS "{par}"')

    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        target = func(self, *args, **kwargs)
        if isinstance(target, (Element, Elements)):
            return target.__get__(self)
        raise TypeError(f'The decorated function "{func.__name__}" must return an Element or Elements instance.')

    return wrapper
