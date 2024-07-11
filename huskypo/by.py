# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO


from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy


class By(AppiumBy):
    pass


class ByAttribute:

    NAMES = [attr for attr in dir(By) if not attr.startswith('__')]
    VALUES = [getattr(By, attr) for attr in NAMES]
    VALUES_WITH_NONE = VALUES + [None]


class SwipeAction:

    # TODO deprecate
    V = 'v'
    H = 'h'
    VA = 'va'
    HA = 'ha'
