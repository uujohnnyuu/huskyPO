# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO


from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy


class By(AppiumBy):
    """
    Including all Selenium `By` and Appium `AppiumBy` methods.
    """
    pass


class ByAttribute:
    """
    This class is primarily used for internal validation of the correctness of `By`.
    It is not set as an inner or private method because users can also use this class
    to check which methods are available in their current version.

    Retrieve all attribute information in huskypo By:
        - NAMES (list): All attribute names (class attribute variable names) as strings.
        - VALUES (list): All actual attribute values (class attribute variable values).
        - VALUES_WITH_NONE (list): VALUES including None.
    """

    NAMES = [attr for attr in dir(By) if not attr.startswith('__')]
    VALUES = [getattr(By, attr) for attr in NAMES]
    VALUES_WITH_NONE = VALUES + [None]


class SwipeAction:
    """
    DEPRECATED.

    This method, including the corresponding
    page.swipe_ratio() and element.swipe_into_view(),
    will be `deprecated` in the future.
    Please use the new swipe parameters `Offset` and `Area` (from huskypo import Offset, Area)
    for the new swipe methods:
    1. page.swipe_by()
    2. page.flick_by()
    3. element.swipe_by()
    4. element.flick_by()
    """

    V = 'v'
    H = 'h'
    VA = 'va'
    HA = 'ha'
