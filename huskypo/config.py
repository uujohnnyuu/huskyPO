# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

from __future__ import annotations


class Log:
    RECORD = False


class Timeout:
    DEFAULT = 30
    RERAISE = True

    @classmethod
    def reraise(cls, switch: bool | None = None) -> bool:
        return cls.RERAISE if switch is None else switch


class Appium:
    LOCALHOST = 'http://127.0.0.1'
    PORT_4723 = ':4723'
    WD_HUB = '/wd/hub'  # appium 1.0


class Swipe:
    UP = (0.5, 0.5, 0.5, 0.25)
    DOWN = (0.5, 0.5, 0.5, 0.75)
    LEFT = (0.5, 0.5, 0.25, 0.5)
    RIGHT = (0.5, 0.5, 0.75, 0.5)
    UPPER_LEFT = (0.5, 0.5, 0.25, 0.25)
    UPPER_RIGHT = (0.5, 0.5, 0.75, 0.25)
    LOWER_LEFT = (0.5, 0.5, 0.25, 0.75)
    LOWER_RIGHT = (0.5, 0.5, 0.75, 0.75)
