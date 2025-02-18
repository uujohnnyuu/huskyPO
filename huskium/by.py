# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy


class By(AppiumBy):
    """
    Including all Selenium `By` and Appium `AppiumBy` methods.
    """
    pass


class ByAttribute:
    """
    This class is used for internal validation of the correctness of `By`.

    Although it is not set as an inner or private method, users can also utilize this class 
    to check which methods are available in their current version.

    Attributes:
        NAMES (list): A list of all `By` attribute names as strings.
        VALUES (list): A list of all `By` attribute values.
        VALUES_WITH_NONE (list): A list of `VALUES`, including `None`.
    """
    NAMES = [attr for attr in dir(By) if not attr.startswith('__')]
    VALUES = [getattr(By, attr) for attr in NAMES]
    VALUES_WITH_NONE = VALUES + [None]
