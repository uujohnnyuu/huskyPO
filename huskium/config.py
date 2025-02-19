# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


from __future__ import annotations

import logging

from .logging import PrefixFilter


class Log:
    """
    General log settings.

    Attributes:
        PREFIX_FILTER (PrefixFilter): Internal debug logging filter.

    Examples:
        You can control the debug logging display:
        ```python
        PREFIX_FILTER.prefix = 'run'  # Finds frames with the prefix "run".
        PREFIX_FILTER.lower = True  # Makes the prefix "run" case-insensitive.
        PREFIX_FILTER.funcframe = False  # Finds the file (module) frame using the prefix "run".
        ```
    """
    # prefix filter object
    PREFIX_FILTER = PrefixFilter('test')

    # Deprecation of logstack
    _PREFIX = 'test'
    _LOWER = True

    # basicConfig
    FILENAME = './log.log'
    FILEMODE = 'w'
    FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'
    DATEFMT = '%Y-%m-%d %H:%M:%S'
    LEVEL = logging.DEBUG
    BASIC_CONFIG = {
        "filename": FILENAME,
        "filemode": FILEMODE,
        "format": FORMAT,
        "datefmt": DATEFMT,
        "level": LEVEL
    }


class Cache:
    """
    Configure the cache in the related function.

    Attributes:
        ELEMENT (bool): True (default) to enable cache in Element.
    """
    ELEMENT: bool = True


class Timeout:
    """
    Timeout settings.

    Attributes:
        DEFAULT (int, float):
            - Default value is 30.
            - Specifies the default wait time (in seconds) for each element(s).
        RERAISE (bool):
            - `True` (default): Raise a `TimeoutException` when a timeout occurs.
            - `False`: Return `False` when a timeout occurs.
    """
    DEFAULT: int | float = 30
    RERAISE: bool = True

    @classmethod
    def reraise(cls, switch: bool | None = None) -> bool:
        """
        When a timeout occurs, used to determine whether to re-raise
        a TimeoutException or return False.
        Typically used in wait-related methods within Element or Elements.

        Args:
            switch (bool, None):
                - `None` (default): Follows the value of `Timeout.RERAISE`,
                    with logic the same as bool.
                - `True`: Raise a `TimeoutException` when a timeout occurs.
                - `False`: Return `False` when a timeout occurs.
        """
        return cls.RERAISE if switch is None else switch


class Appium:
    """
    General settings for Appium.
    """
    LOCALHOST: str = 'http://127.0.0.1'
    PORT_4723: str = ':4723'
    WD_HUB: str = '/wd/hub'


class Offset:
    """
    All Offset attributes store `(start_x, start_y, end_x, end_y)`.
    Used in `Page` and `Element` to set the `offset` action for `swipe_by` and `flick_by`.
    You can set the preferred offset by assigning values to these variables,
    or create another Offset class based on your test scenario.
    """
    UP: tuple = (0.5, 0.75, 0.5, 0.25)
    DOWN: tuple = (0.5, 0.25, 0.5, 0.75)
    LEFT: tuple = (0.75, 0.5, 0.25, 0.5)
    RIGHT: tuple = (0.25, 0.5, 0.75, 0.5)
    UPPER_LEFT: tuple = (0.75, 0.75, 0.25, 0.25)
    UPPER_RIGHT: tuple = (0.25, 0.75, 0.75, 0.25)
    LOWER_LEFT: tuple = (0.75, 0.25, 0.25, 0.75)
    LOWER_RIGHT: tuple = (0.25, 0.25, 0.75, 0.75)


class Area:
    """
    All Area attributes store `(x, y, width, height)`.
    Used in `Page` and `Element` to set the `area` action for `swipe_by` and `flick_by`.
    You can set the preferred area by assigning values to these variables,
    or create another Area class based on your test scenario.
    """
    FULL: tuple = (0.0, 0.0, 1.0, 1.0)
