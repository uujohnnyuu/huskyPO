# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO


from __future__ import annotations


class Log:
    """
    Internal log settings.

    RECORD: True means recording internal logs for huskyPO.
    """
    RECORD = False


class Timeout:
    """
    Timeout settings.

    DEFAULT: The default wait time for each element, which can be directly called and modified.
        It will immediately affect all subsequent elements.
    RERAISE: True means that a TimeoutException will be raised immediately when a timeout occurs;
        otherwise, False will be returned.
    """
    DEFAULT = 30
    RERAISE = True

    @classmethod
    def reraise(cls, switch: bool | None = None) -> bool:
        """
        When a timeout occurs, used to determine whether to re-raise a TimeoutException or return False.
        Typically used in wait-related methods within Element or Elements.

        Args:
        - switch:
            - bool: True means a TimeoutException will be raised; False means False will be returned.
            - None: Follows the value of Timeout.RERAISE, with logic the same as bool.
        """
        return cls.RERAISE if switch is None else switch


class Appium:
    """
    General settings for Appium.

    LOCALHOST: 'http://127.0.0.1'
    PORT_4723: ':4723'
    WD_HUB (appium 1.0): '/wd/hub'
    """
    LOCALHOST = 'http://127.0.0.1'
    PORT_4723 = ':4723'
    WD_HUB = '/wd/hub'


class Offset:
    """
    Used in Page and Element to set the `offset` action for `swipe_by` and `flick_by`.
    You can set the preferred offset by assigning values to these variables,
    or create another Offset class based on your test scenario.
    """
    UP = (0.5, 0.75, 0.5, 0.25)
    DOWN = (0.5, 0.25, 0.5, 0.75)
    LEFT = (0.75, 0.5, 0.25, 0.5)
    RIGHT = (0.25, 0.5, 0.75, 0.5)
    UPPER_LEFT = (0.75, 0.75, 0.25, 0.25)
    UPPER_RIGHT = (0.25, 0.75, 0.75, 0.25)
    LOWER_LEFT = (0.75, 0.25, 0.25, 0.75)
    LOWER_RIGHT = (0.25, 0.25, 0.75, 0.75)


class Area:
    """
    Used in Page and Element to set the `area` action for `swipe_by` and `flick_by`.
    You can set the preferred area by assigning values to these variables,
    or create another Area class based on your test scenario.
    """
    FULL = (0.0, 0.0, 1.0, 1.0)
