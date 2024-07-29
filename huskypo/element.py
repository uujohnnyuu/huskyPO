# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# TODO
# 1. Keep tracking selenium 4.0 and appium 2.0 new methods.
# 2. Keep observing whether it is necessary to add the visible state for each method.


from __future__ import annotations

import warnings
import math
import platform
from typing import Type, TypeVar, Literal, Any

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.types import WaitExcTypes

from . import logstack
from . import ec_extension as ecex
from .config import Timeout, Offset, Area
from .by import ByAttribute
from .page import Page
from .types import SeleniumWebElement, AppiumWebDriver
from .types import WebDriver, WebElement

# NOTE DEPRECATED.
from .by import SwipeAction as SA


ElementReferenceException = (AttributeError, StaleElementReferenceException)

P = TypeVar('P', bound=Page)
TupleCoordinate = tuple[int, int, int, int] | tuple[float, float, float, float]
Coordinate = TupleCoordinate | dict[str, int] | dict[str, float]


class Element:

    __TmpAttrs = ['_present_element', '_visible_element', '_clickable_element', '_select']

    def __init__(
        self,
        by: str | None = None,
        value: str | None = None,
        index: int | None = None,
        timeout: int | float | None = None,
        remark: str | None = None
    ) -> None:
        """
        Initial Element attributes.

        Args:
        - by: Element locator strategy (from huskypo import By).
        - value: Element locator value.
        - index:
            - None: Using `find_element` strategy.
            - int: Using `find_elements` with list index strategy.
        - timeout: Element timeout in seconds of explicit wait.
        - remark: Element note, can be used for easy identification or logging.

        Usage (without parameter name)::

            # (by, value)
            element = Element(By.ID, 'element_id')

            # (by, value, index):
            element = Element(By.ID, 'element_id', 3)

            # (by, value, remark):
            element = Element(By.ID, 'element_id', 'this is xxx')

            # (by, value, index, timeout):
            element = Element(By.ID, 'element_id', None, 10)

            # (by, value, index, remark):
            element = Element(By.ID, 'element_id', 3, 'this is xxx')

            # (by, value, index, timeout, remark):
            element = Element(By.ID, 'element_id', 3, 10, 'this is xxx')

        """
        # (by, value), allowing `None` to initialize an empty descriptor for dynamic elements.
        if by not in ByAttribute.VALUES_WITH_NONE:
            raise ValueError(f'The locator strategy "{by}" is undefined.')
        if not isinstance(value, (str, type(None))):
            raise TypeError(f'The locator value type should be "str", not "{type(self._value).__name__}".')
        self._by = by
        self._value = value

        # (by, value, index)
        self._index = index
        # (by, value, remark)
        if not isinstance(index, (int, type(None))):
            remark = str(index)
            self._index = None

        # (by, value, index, timeout)
        self._timeout = timeout
        # (by, value, index, remark)
        if not isinstance(timeout, (int, float, type(None))):
            remark = str(timeout)
            self._timeout = None

        # (by, value, index, timeout, remark)
        self._remark = remark

        # Record the page instance and determine
        # whether to delete the WebElement object to avoid an InvalidSessionIdException.
        self._page = None

    def __get__(self, instance: P, owner: Type[P] | None = None) -> Element:
        """
        Internal use.
        Make "Element" a data descriptor for "Page" or "other classes that inherit from Page".
        Dynamically create and record instance attributes related to Page,
        allowing Element to interact with Page-related attributes or methods.
        """
        # When a new Page instance is detected, it indicates that the driver may have changed.
        # Delete the WebElement object to avoid an InvalidSessionIdException.
        if self._page != instance:
            self._page = instance
            self.__del_tmpattrs()
        return self

    def __set__(self, instance: P, value: tuple | dict) -> None:
        """
        Internal use.
        Dynamically set element attribute values at runtime,
        typically used for configuring dynamic elements.
        """
        # Avoid referencing an old WebElement for dynamic element.
        if isinstance(value, tuple):
            self.__init__(*value)
        elif isinstance(value, dict):
            self.__init__(**value)
        else:
            raise TypeError('Please configure dynamic elements according to the logic of the Element parameters.')
        self.__del_tmpattrs()

    def __del_tmpattrs(self) -> None:
        for attr in Element.__TmpAttrs:
            if hasattr(self, attr):
                delattr(self, attr)

    @property
    def by(self) -> str | None:
        return self._by

    @property
    def value(self) -> str | None:
        return self._value

    @property
    def locator(self) -> tuple[str, str]:
        """
        Get locator (by, value).
        """
        if self._by and self._value:
            return (self._by, self._value)
        raise ValueError(
            '"by" and "value" cannot be None when performing element operations. Please ensure both are provided with valid values.')

    @property
    def index(self) -> int | None:
        return self._index

    @property
    def timeout(self) -> int | float:
        """
        The initial timeout of the element.
        If init timeout is None, return Timeout.DEFAULT.
        """
        return Timeout.DEFAULT if self._timeout is None else self._timeout

    @timeout.setter
    def timeout(self, new_timeout) -> None:
        if not isinstance(new_timeout, (int, float, type(None))):
            raise TypeError(
                f'The timeout type should be "int", "float", or "None", not "{type(new_timeout).__name__}".')
        self._timeout = new_timeout

    @property
    def remark(self) -> str:
        """
        The remark of the element.
        If init remark is None, return (by="by", value="value", index="index").
        """
        return f'(by="{self._by}", value="{self._value}", index={self._index})' if self._remark is None else self._remark

    @remark.setter
    def remark(self, new_remark) -> None:
        self._remark = new_remark

    @property
    def driver(self) -> WebDriver:
        """
        Get driver from Page-related instance.
        """
        return self._page._driver

    @property
    def _action(self) -> ActionChains:
        """
        Internal use.
        Get ActionChains object from Page-related instance.
        """
        return self._page._action

    def find_element(self) -> WebElement:
        """
        Using the traditional find_element method
        to locate element without any waiting behavior.
        It is recommended for use in situations where no waiting is required,
        such as the Android UiScrollable locator method.
        """
        return self.driver.find_element(*self.locator)

    def wait(
        self,
        timeout: int | float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebDriverWait:
        """
        Get an object of WebDriverWait.

        Args:
        - timeout: The maximum time in seconds to wait for the expected condition.
            By default, it initializes with the element timeout.
        - ignored_exceptions: iterable structure of exception classes ignored during calls.
            By default, it contains NoSuchElementException only.
        """
        self._wait_timeout = self.timeout if timeout is None else timeout
        return WebDriverWait(self.driver, self._wait_timeout, ignored_exceptions=ignored_exceptions)

    @property
    def wait_timeout(self) -> int | float | None:
        """
        Get the final waiting timeout of the element.
        If no element action has been executed yet, it will return None.
        """
        try:
            return self._wait_timeout
        except AttributeError:
            return None

    def __timeout_message(self, status: str, present: bool = True) -> str:
        """
        Waiting for element "{self.final_remark}" to become "{status}" timed out after {self._wait_timeout} seconds.
        if not present: status + ' or absent'
        """
        if not present:
            status += ' or absent'
        return f'Waiting for element "{self.remark}" to become "{status}" timed out after {self._wait_timeout} seconds.'

    def find(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None,
    ) -> WebElement | Literal[False]:
        """
        Wait for the element to be `present`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.
        - reraise: If a timeout occurs, True means reraising TimeoutException,
            and False means returning False directly.

        Returns:
        - WebElement: If the element becomes present before the timeout.
        - False: "reraise" is False and the element is not present after the timeout.
        """
        return self.wait_present(timeout, reraise)

    @property
    def present_element(self) -> WebElement:
        """
        Obtaining the present WebElement simply.
        The same as element.wait_present(reraise=True).
        Note that a TimeoutException will be raised
        if the element is abesent within the timeout period.
        """
        return self.wait_present(reraise=True)

    @property
    def visible_element(self) -> WebElement:
        """
        Obtaining the visible WebElement simply.
        The same as element.wait_visible(reraise=True).
        Note that a TimeoutException will be raised
        if the element is invisible or abesent within the timeout period.
        """
        return self.wait_visible(reraise=True)

    @property
    def clickable_element(self) -> WebElement:
        """
        Obtaining the clickable WebElement simply.
        The same as element.wait_clickable(reraise=True).
        Note that a TimeoutException will be raised
        if the element is unclickable or abesent within the timeout period.
        """
        return self.wait_clickable(reraise=True)

    def wait_present(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Wait for the element to become `present`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - WebElement (Expected): The element reached the expected status before the timeout.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            self._present_element = self.wait(timeout).until(
                ecex.presence_of_element_located(self.locator, self._index),
                self.__timeout_message('present'))
            return self._present_element
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_absent(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Wait for the element to become `absent`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - True (Expected): The element reached the expected status before the timeout.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.absence_of_element_located(self.locator, self._index),
                self.__timeout_message('absent'))
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_visible(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Wait for the element to become `visible`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - WebElement (Expected): The element reached the expected status before the timeout.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            self._visible_element = self.wait(timeout).until(
                ecex.visibility_of_element(self._present_element),
                self.__timeout_message('visible'))
            return self._visible_element
        except ElementReferenceException:
            self._present_element = self._visible_element = self.wait(timeout, StaleElementReferenceException).until(
                ecex.visibility_of_element_located(self.locator, self._index),
                self.__timeout_message('visible'))
            return self._visible_element
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_invisible(
        self,
        timeout: int | float | None = None,
        present: bool = True,
        reraise: bool | None = None
    ) -> WebElement | bool:
        """
        Wait for the element to become `invisible`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - present: Indicates whether the element should be present.
            - True: The element should be present in the expected state.
            - False: The element can be either present in the expected state or absent.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - WebElement (Expected): The element reached the expected status before the timeout.
        - True (Expected): The element is absent before the timeout, and "present" is False,
            indicating that the absence of the element is allowed.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.invisibility_of_element(self._present_element),
                self.__timeout_message('invisible'))
        except ElementReferenceException:
            self._present_element = self.wait(timeout, StaleElementReferenceException).until(
                ecex.invisibility_of_element_located(self.locator, self._index, present),
                self.__timeout_message('invisible', present))
            return self._present_element
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_clickable(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Wait for the element to become `clickable`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - WebElement (Expected): The element reached the expected status before the timeout.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            self._visible_element = self._clickable_element = self.wait(timeout).until(
                ecex.element_to_be_clickable(self._present_element),
                self.__timeout_message('clickable'))
            return self._clickable_element
        except ElementReferenceException:
            self._present_element = self._visible_element = self._clickable_element = self.wait(
                timeout, StaleElementReferenceException).until(
                    ecex.element_located_to_be_clickable(self.locator, self._index),
                    self.__timeout_message('clickable'))
            return self._clickable_element
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_unclickable(
        self,
        timeout: int | float | None = None,
        present: bool = True,
        reraise: bool | None = None
    ) -> WebElement | bool:
        """
        Wait for the element to become `unclickable`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - present: Indicates whether the element should be present.
            - True: The element should be present in the expected state.
            - False: The element can be either present in the expected state or absent.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - WebElement (Expected): The element reached the expected status before the timeout.
        - True (Expected): The element is absent before the timeout, and "present" is False,
            indicating that the absence of the element is allowed.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.element_to_be_unclickable(self._present_element),
                self.__timeout_message('unclickable'))
        except ElementReferenceException:
            self._present_element = self.wait(timeout, StaleElementReferenceException).until(
                ecex.element_located_to_be_unclickable(self.locator, self._index, present),
                self.__timeout_message('unclickable', present))
            return self._present_element
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_selected(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Wait for the element to become `selected`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - WebElement (Expected): The element reached the expected status before the timeout.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.element_to_be_selected(self._present_element),
                self.__timeout_message('selected'))
        except ElementReferenceException:
            self._present_element = self.wait(timeout, StaleElementReferenceException).until(
                ecex.element_located_to_be_selected(self.locator, self._index),
                self.__timeout_message('selected'))
            return self._present_element
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_unselected(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Waiting for the element to become `unselected`.

        Note that the behavior of unselected is different from invisible and unclickable.
        The selection state highly depends on the user's action, so the element must be present.
        Therefore, absent is not considered one of the expected results.

        Args:
        - timeout: The maximum time (in seconds) to wait for the element to reach the expected state.
            Defaults (None) to the element's timeout value.
        - reraise: When the element state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - WebElement (Expected): The element reached the expected status before the timeout.
        - False (Unexpected): The element did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the element did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.element_to_be_unselected(self._present_element),
                self.__timeout_message('unselected'))
        except ElementReferenceException:
            self._present_element = self.wait(timeout, StaleElementReferenceException).until(
                ecex.element_located_to_be_unselected(self.locator, self._index),
                self.__timeout_message('unselected'))
            return self._present_element
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def is_present(self, timeout: int | float | None = None) -> bool:
        """
        Whether the element is present.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.

        Returns:
        - True: The element is present before timeout.
        - False: The element is still not present after timeout.
        """
        return True if self.wait_present(timeout, False) else False

    def is_visible(self) -> bool:
        """
        Whether the element is visible.
        It is the same as the official "is_displayed()" method.
        """
        try:
            result = self._present_element.is_displayed()
        except ElementReferenceException:
            result = self.present_element.is_displayed()

        if result:
            self._visible_element = self._present_element

        return result

    def is_enabled(self) -> bool:
        """
        Whether the element is enabled.
        """
        try:
            return self._present_element.is_enabled()
        except ElementReferenceException:
            return self.present_element.is_enabled()

    def is_clickable(self) -> bool:
        """
        Whether the element is clickable.
        """
        try:
            result = self._present_element.is_displayed() and self._present_element.is_enabled()
        except ElementReferenceException:
            element = self.present_element
            result = element.is_displayed() and element.is_enabled()

        if result:
            self._clickable_element = self._visible_element = self._present_element

        return result

    def is_selected(self) -> bool:
        """
        Whether the element is selected.
        """
        try:
            return self._present_element.is_selected()
        except ElementReferenceException:
            return self.present_element.is_selected()

    @property
    def text(self) -> str:
        """
        The text of the element when it is present.
        """
        try:
            return self._present_element.text
        except ElementReferenceException:
            return self.present_element.text

    @property
    def visible_text(self) -> str:
        """
        The text of the element when it is visible.
        """
        try:
            return self._visible_element.text
        except ElementReferenceException:
            return self.visible_element.text

    @property
    def rect(self) -> dict:
        """
        A dictionary with the size and location of the element when it is present.

        Return is rearranged, for example:
        {'x': 10, 'y': 15, 'width': 100, 'height': 200}

        Note that the official rect may have decimals;
        We remain consistent with the official standards.
        """
        try:
            rect = self._present_element.rect
        except ElementReferenceException:
            rect = self.present_element.rect
        return {
            'x': rect['x'], 'y': rect['y'],
            'width': rect['width'], 'height': rect['height']
        }

    @property
    def location(self) -> dict[str, int]:
        """
        The location of the element when it is present in the renderable canvas.

        Return is the same as official:
        {'x': int, 'y': int}

        Note that the official location has been rounded,
        so the x, y may be different with rect.
        """
        try:
            return self._present_element.location
        except ElementReferenceException:
            return self.present_element.location

    @property
    def size(self) -> dict[str, int]:
        """
        The size of the element when it is present.

        Return is rearranged, for example:
        - {'width': 200, 'height': 100}

        Note that the official size may have decimals;
        We remain consistent with the official standards.
        """
        try:
            size = self._present_element.size
        except ElementReferenceException:
            size = self.present_element.size
        return {'width': size['width'], 'height': size['height']}

    @property
    def border(self) -> dict[str, int]:
        """
        The border of the element when it is present.

        Return is rounded down:
        - {'left': int, 'right': int, 'top': int, 'bottom': int}
        """
        try:
            rect = self._present_element.rect
        except ElementReferenceException:
            rect = self.present_element.rect
        return {
            'left': int(rect['x']),
            'right': int(rect['x'] + rect['width']),
            'top': int(rect['y']),
            'bottom': int(rect['y'] + rect['height'])
        }

    @property
    def center(self) -> dict[str, int]:
        """
        The center location of the element when it is present.

        Return is rounded down:
        - {'x': int, 'y': int}
        """
        try:
            rect = self._present_element.rect
        except ElementReferenceException:
            rect = self.present_element.rect
        return {
            'x': int(rect['x'] + rect['width'] / 2),
            'y': int(rect['y'] + rect['height'] / 2)
        }

    def click(self) -> Element:
        """
        Click the element when it is clickable.
        """
        try:
            self._clickable_element.click()
        except ElementReferenceException:
            self.clickable_element.click()
        return self

    def tap(self, duration: int | None = None) -> Element:
        """
        Appium API.
        Tap the center location of the element when it is present.
        When the element is expected to be clickable,
        but it does not behave as anticipated,
        you can use this method to trigger a click.

        Args:
        - duration: length of time to tap, in ms
        """
        center = tuple(self.center.values())
        self.driver.tap([center], duration)
        return self

    def app_drag_and_drop(self, target: Element) -> AppiumWebDriver:
        """
        Appium API.
        Drag the origin element to the destination element.

        Args:
        - target: the element to drag to
        """
        try:
            return self.driver.drag_and_drop(self._present_element, target._present_element)
        except ElementReferenceException:
            return self.driver.drag_and_drop(self.present_element, target.present_element)

    def app_scroll(self, target: Element, duration: int | None = None) -> AppiumWebDriver:
        """
        Appium API.
        Scrolls from one element to another

        Args:
        - target: the element to scroll to (center of element)
        - duration: defines speed of scroll action when moving to target.
            Default is 600 ms for W3C spec.
        """
        try:
            return self.driver.scroll(self._present_element, target._present_element, duration)
        except ElementReferenceException:
            return self.driver.scroll(self.present_element, target.present_element, duration)

    def is_viewable(self, timeout: int | float | None = None) -> bool:
        """
        Appium API.
        For native iOS and Android,
        access the element status whether it is in view border.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.
        """
        element = self.wait_present(timeout, False)
        if element and element.is_displayed():
            self._visible_element = element
            return True
        return False

    def swipe_by(
        self,
        offset: Coordinate = Offset.UP,
        area: Coordinate = Area.FULL,
        timeout: int | float = 3,
        max_swipe: int = 10,
        max_adjust: int = 2,
        min_distance: int = 100,
        duration: int = 1000
    ) -> Element:
        """
        Appium API.
        For native iOS and Android apps,
        this function swipes the screen until the element becomes visible
        within the specified area.

        Args:
        - offset: Please refer to the Usage.
        - area: Please refer to the Usage.
        - timeout: The maximum time in seconds to wait for the element to become visible.
        - max_swipe: The maximum number of swipes allowed.
        - max_adjust: The maximum number of adjustments to align all borders of the element within the view border.
        - min_distance: The minimum swipe distance to avoid being mistaken for a click.
        - duration: The duration of the swipe in milliseconds, from start to end.

        Note on Args "min_distance" and "duration":
        Both parameters are used to adjust the element position with a swipe
        when the element is visible but not within the desired area.
        The default settings are based on sliding at a rate of 100 pixels per second,
        which has been found to be stable.
        It is recommended not to change these parameter values unless you have specific testing scenarios.

        Usage::

            # The "offset" parameter can be directly obtained from the "Offset" class for common swipe ranges.
            # The four values of "offset" represent (start_x, start_y, end_x, end_y),
            # it can also be written as a dictionary.
            from huskypo import Offset

            # The "area" parameter can also be obtained from the "Area" class,
            # but here it is mainly used to set the default scrollable area to the entire screen,
            # so there is no need to call it actively.
            # The four values of "area" represent rect (x, y, width, height),
            # it can also be written as a dictionary.
            from huskypo import Area

            # Swipe down.
            my_page.target_element.swipe_by(Offset.DOWN)

            # Swipe to the right.
            my_page.target_element.swipe_by(Offset.RIGHT)

            # Swipe to the upper left.
            my_page.target_element.swipe_by(Offset.UPPER_LEFT)

            # Default is swiping up.
            # offset = Offset.UP = (0.5, 0.5, 0.5, 0.25)
            # area = Area.FULL = (0.0, 0.0, 1.0, 1.0)
            # offset x: Fixed 50% (0.5) of 100% (1.0) current window width.
            # offset y: From 50% (0.5) to 25% (0.25) of 100% (1.0) current window height.
            my_page.target_element.swipe_by()

            # This is the most recommended method to swipe within a swipeable range.
            # Get the absolute area coordinates using the scrollable element's rect.
            area = my_page.scrollable_element.rect
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35), area)

            # Swipe with customize absolute offset.
            # Note that the area parameter will affect the adjusting process.
            # We recommend not setting the area in this case,
            # unless you have a specific testing scenario.
            # (ex. Swiping range is not within the area,
            # and the target element should be inside the area after swiping.)
            my_page.target_element.swipe_by((250, 300, 400, 700))

            # Swipe with customize relative offset of current window size.
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35))

            # Swipe with customize relative offset of customize relative area.
            # The area is relative to current window rect, for example:
            # current window rect = (10, 20, 500, 1000)
            # area = (0.1, 0.2, 0.6, 0.7)
            # area x = 10 + 500 x 0.1 = 60
            # area y = 20 + 1000 x 0.2 = 220
            # area width = 500 x 0.6 = 300
            # area height = 1000 x 0.7 = 700
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35), (0.1, 0.2, 0.6, 0.7))

            # Swipe with customize relative offset of customize absolute area.
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35), (100, 150, 300, 700))

        """
        area = self.__get_area(area)
        offset = self.__get_offset(offset, area)
        self.__start_swiping_by(offset, duration, timeout, max_swipe)
        self.__start_adjusting_by(offset, area, max_adjust, min_distance, duration)
        return self

    def flick_by(
        self,
        offset: Coordinate = Offset.UP,
        area: Coordinate = Area.FULL,
        timeout: int | float = 3,
        max_flick: int = 10,
        max_adjust: int = 2,
        min_distance: int = 100,
        duration: int = 1000
    ) -> Element:
        """
        Appium API.
        For native iOS and Android apps,
        this function flicks the screen until the element becomes visible
        within the specified area.

        Args:
        - offset: Please refer to the Usage.
        - area: Please refer to the Usage.
        - timeout: The maximum time in seconds to wait for the element to become visible.
        - max_flick: The maximum number of swipes allowed.
        - max_adjust: The maximum number of adjustments to align all borders of the element within the view border.
        - min_distance: Adjusting. The minimum swipe distance to avoid being mistaken for a click.
        - duration: Adjustung. The duration of the swipe in milliseconds, from start to end.

        Note on Args "min_distance" and "duration":
        Both parameters are used to adjust the element position with a swipe (not a flick)
        when the element is visible but not within the desired area.
        The default settings are based on sliding at a rate of 100 pixels per second,
        which has been found to be stable.
        It is recommended not to change these parameter values unless you have specific testing scenarios.

        Usage::

            # The "offset" parameter can be directly obtained from the "Offset" class for common flick ranges.
            # The four values of "offset" represent (start_x, start_y, end_x, end_y),
            # it can also be written as a dictionary.
            from huskypo import Offset

            # The "area" parameter can also be obtained from the "Area" class,
            # but here it is mainly used to set the default scrollable area to the entire screen,
            # so there is no need to call it actively.
            # The four values of "area" represent rect (x, y, width, height),
            # it can also be written as a dictionary.
            from huskypo import Area

            # Flick down.
            my_page.target_element.flick_by(Offset.DOWN)

            # Flick to the right.
            my_page.target_element.flick_by(Offset.RIGHT)

            # Flick to the upper left.
            my_page.target_element.flick_by(Offset.UPPER_LEFT)

            # Default is flicking up.
            # offset = Offset.UP = (0.5, 0.5, 0.5, 0.25)
            # area = Area.FULL = (0.0, 0.0, 1.0, 1.0)
            # offset x: Fixed 50% (0.5) of 100% (1.0) current window width.
            # offset y: From 50% (0.5) to 25% (0.25) of 100% (1.0) current window height.
            my_page.target_element.flick_by()

            # This is the most recommended method to flick within a swipeable range.
            # Get the absolute area coordinates using the scrollable element's rect.
            area = my_page.scrollable_element.rect
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35), area)

            # Flick with customize absolute offset.
            # Note that the area parameter will affect the adjusting process.
            # We recommend not setting the area in this case,
            # unless you have a specific testing scenario.
            # (ex. Swiping range is not within the area,
            # and the target element should be inside the area after flicking.)
            my_page.target_element.flick_by((250, 300, 400, 700))

            # Flick with customize relative offset of current window size.
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35))

            # Flick with customize relative offset of customize relative area.
            # The area is relative to current window rect, for example:
            # current window rect = (10, 20, 500, 1000)
            # area = (0.1, 0.2, 0.6, 0.7)
            # area x = 10 + 500 x 0.1 = 60
            # area y = 20 + 1000 x 0.2 = 220
            # area width = 500 x 0.6 = 300
            # area height = 1000 x 0.7 = 700
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35), (0.1, 0.2, 0.6, 0.7))

            # Flick with customize relative offset of customize absolute area.
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35), (100, 150, 300, 700))

        """
        area = self.__get_area(area)
        offset = self.__get_offset(offset, area)
        self.__start_flicking_by(offset, timeout, max_flick)
        self.__start_adjusting_by(offset, area, max_adjust, min_distance, duration)
        return self

    def __get_coordinate(
        self,
        coordinate: Coordinate,
        name: str
    ) -> TupleCoordinate:

        # Check coordinate type.
        if not isinstance(coordinate, (dict, tuple)):
            raise TypeError(f'"{name}" should be dict or tuple.')
        if isinstance(coordinate, dict):
            coordinate = tuple(coordinate.values())

        # Check all values in coordinate should be int or float.
        if not (all(isinstance(c, int) for c in coordinate) or all(isinstance(c, float) for c in coordinate)):
            raise TypeError(f'All "{name}" values should be "int" or "float".')

        # If float, all should be (0 <= x <= 1).
        if isinstance(coordinate[0], float) and not all(0 <= abs(c) <= 1 for c in coordinate):
            raise ValueError(f'All "{name}" values are floats and should be between "0.0" and "1.0".')

        return coordinate

    def __get_area(self, area: Coordinate) -> tuple[int, int, int, int]:

        area_x, area_y, area_width, area_height = self.__get_coordinate(area, 'area')

        if isinstance(area_x, float):
            window_x, window_y, window_width, window_height = self._page.get_window_rect().values()
            area_x = int(window_x + window_width * area_x)
            area_y = int(window_y + window_height * area_y)
            area_width = int(window_width * area_width)
            area_height = int(window_height * area_height)

        area = (area_x, area_y, area_width, area_height)
        logstack._info(f'area: {area}')
        return area

    def __get_offset(
        self,
        offset: Coordinate,
        area: tuple[int, int, int, int]
    ) -> tuple[int, int, int, int]:

        start_x, start_y, end_x, end_y = self.__get_coordinate(offset, 'offset')

        if isinstance(start_x, float):
            area_x, area_y, area_width, area_height = area
            start_x = int(area_x + area_width * start_x)
            start_y = int(area_y + area_height * start_y)
            end_x = int(area_x + area_width * end_x)
            end_y = int(area_y + area_height * end_y)

        offset = (start_x, start_y, end_x, end_y)
        logstack._info(f'offset: {offset}')
        return offset

    def __start_swiping_by(
        self,
        offset: tuple[int, int, int, int],
        duration: int,
        timeout: int | float,
        max_swipe: int
    ) -> int | Literal[False]:
        logstack._info(f'Start swiping to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                logstack._warning(
                    f'Stop swiping to element {self.remark} as the maximum swipe count of {max_swipe} has been reached.')
                return False
            self.driver.swipe(*offset, duration)
            count += 1
        logstack._info(f'End swiping as the element {self.remark} is now viewable.')
        return count

    def __start_flicking_by(
        self,
        offset: tuple[int, int, int, int],
        timeout: int | float,
        max_swipe: int
    ) -> int | Literal[False]:
        logstack._info(f'Start flicking to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                logstack._warning(
                    f'Stop flicking to element {self.remark} as the maximum flick count of {max_swipe} has been reached.')
                return False
            self.driver.flick(*offset)
            count += 1
        logstack._info(f'End flicking as the element {self.remark} is now viewable.')
        return count

    def __start_adjusting_by(
        self,
        offset: tuple[int, int, int, int],
        area: tuple[int, int, int, int],
        max_adjust: int,
        min_distance: int,
        duration: int
    ) -> int | Literal[False]:

        def delta(area, element):
            d = area - element
            return int(math.copysign(min_distance, d)) if abs(d) < min_distance else d

        logstack._info(f'Start adjusting to element {self.remark}')

        for i in range(1, max_adjust + 2):

            # offset
            start_x, start_y, end_x, end_y = offset

            # area border
            area_left, area_top, area_width, area_height = area
            area_right = area_left + area_width
            area_bottom = area_top + area_height

            # element border
            element_left, element_right, element_top, element_bottom = self.border.values()

            # delta = (area - element) and compare with min distance
            delta_left = delta(area_left, element_left)
            delta_right = delta(area_right, element_right)
            delta_top = delta(area_top, element_top)
            delta_bottom = delta(area_bottom, element_bottom)

            # adjust condition
            adjust_left = delta_left > 0
            adjust_right = delta_right < 0
            adjust_top = delta_top > 0
            adjust_bottom = delta_bottom < 0
            adjust = (adjust_left, adjust_right, adjust_top, adjust_bottom)
            adjust_actions = {
                (True, False, True, False): (delta_left, delta_top),
                (False, False, True, False): (0, delta_top),
                (False, True, True, False): (delta_right, delta_top),
                (True, False, False, False): (delta_left, 0),
                (False, True, False, False): (delta_right, 0),
                (True, False, False, True): (delta_left, delta_bottom),
                (False, False, False, True): (0, delta_bottom),
                (False, True, False, True): (delta_right, delta_bottom),
            }

            # Set the end point by adjust actions.
            if adjust in adjust_actions:
                logstack._info(f'Adjust (left, right, top, bottom): {adjust}')
                delta_x, delta_y = adjust_actions[adjust]
                end_x = start_x + delta_x
                end_y = start_y + delta_y
            else:
                logstack._info(f'End adjusting as the element {self.remark} is in area.')
                return i

            # max
            if i == max_adjust + 1:
                logstack._warning(
                    f'End adjusting to the element {self.remark} as the maximum adjust count of {max_adjust} has been reached.')
                return False

            self.driver.swipe(start_x, start_y, end_x, end_y, duration)

    def clear(self) -> Element:
        """
        Clear the text of the field type element.

        Usage::

            my_page.my_element.clear()
            my_page.my_element.clear().send_keys('my_text')
            my_page.my_element.click().clear().send_keys('my_text')

        """
        try:
            self._clickable_element.clear()
        except ElementReferenceException:
            self.clickable_element.clear()
        return self

    def send_keys(self, *value) -> Element:
        """
        Simulates typing into the element.

        Args:
        - value: The texts or keys to typing.

        Usage::

            my_page.my_element.send_keys('my_text')
            my_page.my_element.clear().send_keys('my_text')
            my_page.my_element.click().clear().send_keys('my_text')

        """
        try:
            self._clickable_element.send_keys(*value)
        except ElementReferenceException:
            self.clickable_element.send_keys(*value)
        return self

    def get_attribute(self, name: Any | str) -> Any | str | dict | None:
        """
        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, `None` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-`None` values are returned
        as strings.  For attributes or properties which do not exist, `None`
        is returned.

        To obtain the exact value of the attribute or property,
        use :func:`~selenium.webdriver.remote.BaseWebElement.get_dom_attribute` or
        :func:`~selenium.webdriver.remote.BaseWebElement.get_property` methods respectively.

        Args:
        - name: Name of the attribute/property to retrieve.

        Usage::

            # Check if the "active" CSS class is applied to an element.
            is_active = "active" in target_element.get_attribute("class")

        """
        try:
            return self._present_element.get_attribute(name)
        except ElementReferenceException:
            return self.present_element.get_attribute(name)

    def get_property(self, name: Any) -> str | bool | WebElement | dict:
        """
        Gets the given property of the element.

        Args:
        - name: Name of the property to retrieve.

        Usage::

            text_length = target_element.get_property("text_length")

        """
        try:
            return self._present_element.get_property(name)
        except ElementReferenceException:
            return self.present_element.get_property(name)

    def submit(self) -> None:
        """
        Selenium API.
        Submits a form.
        """
        try:
            self._clickable_element.submit()
        except ElementReferenceException:
            self.clickable_element.submit()

    @property
    def tag_name(self) -> str:
        """
        Selenium API.
        This element's `tagName` property.
        """
        try:
            return self._present_element.tag_name
        except ElementReferenceException:
            return self.present_element.tag_name

    def value_of_css_property(self, property_name: Any) -> str:
        """
        Selenium API.
        The value of a CSS property.
        """
        try:
            return self._present_element.value_of_css_property(property_name)
        except ElementReferenceException:
            return self.present_element.value_of_css_property(property_name)

    def visible_value_of_css_property(self, property_name: Any) -> str:
        """
        Selenium API.
        The visible value of a CSS property.
        """
        try:
            return self._visible_element.value_of_css_property(property_name)
        except ElementReferenceException:
            return self.visible_element.value_of_css_property(property_name)

    def switch_to_frame(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        If the frame is available it switches the given driver to the specified frame.
        """
        try:
            return self.wait(timeout).until(
                ec.frame_to_be_available_and_switch_to_it(self.locator),
                self.__timeout_message('available frame'))
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def perform(self) -> None:
        """
        Selenium ActionChains API.
        Performs all stored actions.
        once called, it will execute all stored actions in page.

        Usage::

            # Basic usage. Execute element actions.
            my_page.my_element.scroll_to_element().action_click().perform()

            # Multiple actions to call, set perform to the last action.
            # This will execute all actions in my_page not just my_page.my_element2.
            my_page.my_element1.scroll_to_element().action_click()
            my_page.my_element2.drag_and_drop(my_page.element3).perform()

            # As above, it is the same to call perform by page, which is more clear:
            my_page.my_element1.scroll_to_element().action_click()
            my_page.my_element2.drag_and_drop(my_page.element3)
            my_page.perform()

        """
        self._action.perform()

    def reset_actions(self) -> None:
        """
        Selenium ActionChains API.
        Clears actions that are already stored in object of Page.
        once called, it will reset all stored actions in page.

        Usage::

            # Reset the stored actions by the last reset_actions.
            my_page.my_element1.scroll_to_element().action_click()
            my_page.my_element2.click_and_hold().reset_actions()

            # There is a better one structure,
            # reset all action calls made by my_page.
            my_page.my_element1.scroll_to_element().action_click()
            my_page.my_element2.click_and_hold()
            my_page.reset_actions()

        """
        self._action.reset_actions()

    def action_click(self) -> Element:
        """
        Selenium ActionChains API.
        Clicks an element.

        Usage::

            # Basic usage
            my_page.my_element.action_click().perform()

            # Chain with another method
            my_page.my_element.scroll_to_element().action_click().perform()

            # or
            my_page.my_element1.scroll_to_element().action_click()
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.click(self._present_element)
        except ElementReferenceException:
            self._action.click(self.present_element)
        return self

    def click_and_hold(self) -> Element:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on an element.

        Usage::

            # Basic usage
            my_page.my_element.click_and_hold().perform()

            # Chain with another method
            my_page.my_element.scroll_to_element().click_and_hold().perform()

            # or
            my_page.my_element1.scroll_to_element().click_and_hold()
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.click_and_hold(self._present_element)
        except ElementReferenceException:
            self._action.click_and_hold(self.present_element)
        return self

    def context_click(self) -> Element:
        """
        Selenium ActionChains API.
        Performs a context-click (right click) on an element.

        Usage::

            # Basic usage
            my_page.my_element.context_click().perform()

            # Chain with another method
            my_page.my_element.scroll_to_element().context_click().perform()

            # or
            my_page.my_element1.scroll_to_element().context_click()
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.context_click(self._present_element)
        except ElementReferenceException:
            self._action.context_click(self.present_element)
        return self

    def double_click(self) -> Element:
        """
        Selenium ActionChains API.
        Double-clicks an element.

        Usage::

            # Basic usage
            my_page.my_element.double_click()

            # Chain with another method
            my_page.my_element.scroll_to_element().double_click()

            # or
            my_page.my_element1.scroll_to_element().double_click()
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.double_click(self._present_element)
        except ElementReferenceException:
            self._action.double_click(self.present_element)
            return self

    def drag_and_drop(self, target: Element) -> Element:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on the source element,
        then moves to the target element and releases the mouse button.

        Args:
        - target: The element to mouse up. Allowing Element or WebElement type.

        Usage::

            # Basic usage
            my_page.my_element1.drag_and_drop(my_page.my_element2).perform()

            # Chain with another method
            my_page.my_element1.scroll_to_element().drag_and_drop(my_page.my_element2).perform()

            # or
            my_page.my_element1.scroll_to_element().drag_and_drop(my_page.my_element2)
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.drag_and_drop(self._present_element, target._present_element)
        except ElementReferenceException:
            self._action.drag_and_drop(self.present_element, target.present_element)
            return self

    def drag_and_drop_by_offset(self, xoffset: int, yoffset: int) -> Element:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on the source element,
        then moves to the target offset and releases the mouse button.

        Args:
        - xoffset: X offset to move to, as a positive or negative integer.
        - yoffset: Y offset to move to, as a positive or negative integer.

        Usage::

            # Basic usage
            my_page.my_element.drag_and_drop_by_offset(100, 200).perform()

            # Chain with another method
            my_page.my_element.scroll_to_element().drag_and_drop_by_offset(100, 200).perform()

            # or
            my_page.my_element.scroll_to_element().drag_and_drop_by_offset(100, 200)
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.drag_and_drop_by_offset(self._present_element, xoffset, yoffset)
        except ElementReferenceException:
            self._action.drag_and_drop_by_offset(self.present_element, xoffset, yoffset)
        return self

    def hotkey(self, *value: str) -> Element:
        """
        Selenium ActionChains API.
        Sends hotkey to target element.

        Args:
        - value: The combination of hotkey.

        Usage::

            # copy(control+c)
            my_page.my_element.hotkey(Keys.CONTROL, 'c').perform()

            # switch to previous application(command+shift+tab)
            my_page.my_element.hotkey(Keys.COMMAND, Keys.SHIFT, Keys.TAB).perform()

        """
        # key_down, first to focus target element.
        try:
            self._action.key_down(value[0], self._present_element)
        except ElementReferenceException:
            self._action.key_down(value[0], self.present_element)
        for key in value[1:-1]:
            self._action.key_down(key)
        # send_keys
        self._action.send_keys(value[-1])
        # key_up
        for key in value[-2::-1]:
            self._action.key_up(key)
        return self

    def key_down(self, value: str, focus: bool = True) -> Element:
        """
        Selenium ActionChains API.
        Sends a key press only, without releasing it.
        Should only be used with modifier keys (Control, Alt and Shift).
        If you want to perform a hotkey process,
        it is recommended to use hotkey() instead.

        Args:
        - value: The modifier key to send. Values are defined in Keys class.
        - focus: Whether to focus element or not. Default to focus current element.

        Usage::

            # copy(control+c)
            my_page.my_element.key_down(Key.CONTROL).action_send_keys('c').key_up(Key.CONTROL)

        """
        if focus:
            try:
                self._action.key_down(value, self._present_element)
            except ElementReferenceException:
                self._action.key_down(value, self.present_element)
        else:
            self._action.key_down(value)
        return self

    def key_up(self, value: str, focus: bool = False) -> Element:
        """
        Selenium ActionChains API.
        Releases a modifier key.
        Should only be used with modifier keys (Control, Alt and Shift).
        If you want to perform a hotkey process,
        it is recommended to use hotkey() instead.

        Args:
        - value: The modifier key to send. Values are defined in Keys class.
        - focus: Whether to focus on the element or not.
            The default is NOT to focus on the current element
            as this is generally not the first action.

        Usage::

            # copy(control+c)
            my_page.my_element.key_down(Key.CONTROL).action_send_keys('c').key_up(Key.CONTROL)

        """
        if focus:
            try:
                self._action.key_up(value, self._present_element)
            except ElementReferenceException:
                self._action.key_up(value, self.present_element)
        else:
            self._action.key_up(value)
        return self

    def action_send_keys(self, *keys_to_send: str) -> Element:
        """
        Selenium ActionChains API.
        Sends keys to current focused element.
        Note that it should have focused element first.

        Args:
        - keys_to_send: The keys to send. Modifier keys constants can be found in the 'Keys' class.

        Usage::

            # Combine with key_down and key_up method
            my_page.my_element.key_down(Keys.COMMAND).action_send_keys('a').key_up(Keys.COMMAND).perform()

            # Send keys to focused element
            # This is recommend to use send_keys_to_element() instead.
            my_page.my_element.action_click()  # Need to have focused element first.
            my_page.my_element.action_send_keys('my_keys').perform()

        """
        self._action.send_keys(*keys_to_send)
        return self

    def send_keys_to_element(self, *keys_to_send: str) -> Element:
        """
        Selenium ActionChains API.
        Sends keys to an element.

        Args:
        - keys_to_send: The keys to send. Modifier keys constants can be found in the 'Keys' class.

        Usage::

            # Basic usage
            my_page.my_element.send_keys_to_element(Keys.ENTER)

            # Chain with another method
            my_page.my_element.scroll_to_element(False).send_keys_to_element(Keys.ENTER)

            # or
            my_page.my_element.scroll_to_element(False).send_keys_to_element(Keys.ENTER)
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.send_keys_to_element(self._present_element, *keys_to_send)
        except ElementReferenceException:
            self._action.send_keys_to_element(self.present_element, *keys_to_send)
        return self

    def move_to_element(self) -> Element:
        """
        Selenium ActionChains API.
        Moving the mouse to the middle of an element.

        Usage::

            # Basic usage
            my_page.my_element.move_to_element().perform()

            # Chain with another method
            my_page.my_element.scroll_to_element().move_to_element().perform()

            # or
            my_page.my_element.scroll_to_element().move_to_element()
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.move_to_element(self._present_element)
        except ElementReferenceException:
            self._action.move_to_element(self.present_element)
        return self

    def move_to_element_with_offset(
        self,
        xoffset: int,
        yoffset: int,
    ) -> Element:
        """
        Selenium ActionChains API.
        Move the mouse by an offset of the specified element.
        Offsets are relative to the in-view center point of the element.

        Args:
        - xoffset: X offset to move to, as a positive or negative integer.
        - yoffset: Y offset to move to, as a positive or negative integer.

        Usage::

            # Basic usage
            my_page.my_element.move_to_element_with_offset(100, 200).perform()

            # Chain with another method
            my_page.my_element.scroll_to_element().move_to_element_with_offset(100, 200).perform()

            # or
            my_page.my_element.scroll_to_element().move_to_element_with_offset(100, 200)
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.move_to_element_with_offset(self._present_element, xoffset, yoffset)
        except ElementReferenceException:
            self._action.move_to_element_with_offset(self.present_element, xoffset, yoffset)
        return self

    def release(self) -> Element:
        """
        Selenium ActionChains API.
        Releasing a held mouse button on an element.

        Usage::

            # Basic usage
            my_page.my_element.release().perform()

            # Chain with another method
            my_page.my_element.click_and_hold().release().perform()

            # or
            my_page.my_element.click_and_hold().release()
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.release(self._present_element)
        except ElementReferenceException:
            self._action.release(self.present_element)
        return self

    def pause(self, seconds: int | float) -> Element:
        """
        Selenium ActionChains API.
        Pause all inputs for the specified duration in seconds.
        """
        self._action.pause(seconds)
        return self

    def scroll_to_element(self) -> Element:
        """
        Selenium ActionChains API.
        If the element is outside the viewport,
        scrolls the bottom of the element to the bottom of the viewport.

        Usage::

            # Basic usage
            my_page.my_element.scroll_to_element().perform()

            # Chain with another method
            my_page.my_element.scroll_to_element().action_click().perform()

            # or
            my_page.my_element1.scroll_to_element().action_click()
            ...  # other process
            my_page.perform()

        """
        try:
            self._action.scroll_to_element(self._present_element)
        except ElementReferenceException:
            self._action.scroll_to_element(self.present_element)
        return self

    def scroll_from_element(
        self,
        x_offset: int = 0,
        y_offset: int = 0,
        delta_x: int = 0,
        delta_y: int = 0
    ) -> Element:
        """
        Selenium ActionChains API.
        Set the origin to the center of the element with an offset,
        and perform the swipe with the specified delta.
        If the element is not in the viewport,
        the bottom of the element will first be scrolled to the bottom of the viewport.

        Args:
        - x_offset: from origin element center, a negative value offset left.
        - y_offset: from origin element center, a negative value offset up.
        - delta_x: Distance along X axis to scroll using the wheel. A negative value scrolls left.
        - delta_y: Distance along Y axis to scroll using the wheel. A negative value scrolls up.
        - perform: Default is True to perform the stored action immediately;
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.scroll_from_element(100, 200, -50, -100).perform()

            # Chain with another method
            my_page.my_element.scroll_from_element(-30, -50, 150, 100).action_click().perform()

            # or
            my_page.my_element.scroll_from_element(-30, -50, 150, 100).action_click()
            ...  # other process
            my_page.perform()

        """
        try:
            scroll_origin = ScrollOrigin.from_element(self._present_element, x_offset, y_offset)
            self._action.scroll_from_origin(scroll_origin, delta_x, delta_y)
        except ElementReferenceException:
            scroll_origin = ScrollOrigin.from_element(self.present_element, x_offset, y_offset)
            self._action.scroll_from_origin(scroll_origin, delta_x, delta_y)
        return self

    @property
    def options(self) -> list[SeleniumWebElement]:
        """
        Selenium Select API.
        Returns a list of all options belonging to this select tag.
        """
        # All Select-related methods must be encapsulated using this structure
        # to ensure no unnecessary steps are taken.
        # The reason is that if "self._select.method" raises a
        # StaleElementReferenceException or InvalidSessionIdException,
        # we can directly rebuild with "self._select = Select(self.present_element)",
        # without needing to check "self._select = Select(self._present_element)" again.
        # Once part of the try-except block is encapsulated into a function,
        # there will inevitably be redundant checks for "self._select = Select(self._present_element)".

        try:
            try:
                # The main process.
                return self._select.options
            except AttributeError:
                # Handle the first AttributeError:
                # If there is no available select attribute, create it using the "_present_element" first.
                self._select = Select(self._present_element)
        except ElementReferenceException:
            # Handle ElementReferenceException by creating a new select object.
            # This exception can be triggered in two scenarios:
            # 1. The main process triggers a stale or invalid session exception.
            # 2. During the first AttributeError handling, if there is no "_present_element" attribute,
            #       or it triggers a stale or invalid session exception when initializing.
            self._select = Select(self.present_element)
        return self._select.options

    @property
    def all_selected_options(self) -> list[SeleniumWebElement]:
        """
        Selenium Select API.
        Returns a list of all selected options belonging to this select tag.
        """
        try:
            try:
                return self._select.all_selected_options
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.all_selected_options

    @property
    def first_selected_option(self) -> SeleniumWebElement:
        """
        Selenium Select API.
        The first selected option in this select tag,
        or the currently selected option in a normal select.
        """
        try:
            try:
                return self._select.first_selected_option
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.first_selected_option

    def select_by_value(self, value: str) -> None:
        """
        Selenium Select API.
        Select all options that have a value matching the argument.

        That is, when given "foo" this would select an option like:
        <option value="foo">Bar</option>

        Args:
        - value: The value to match against
        """
        try:
            try:
                return self._select.select_by_value(value)
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.select_by_value(value)

    def select_by_index(self, index: int) -> None:
        """
        Selenium Select API.
        Select the option at the given index.

        This is done by examining the "index" attribute of an element, and not merely by counting.

        Args:
        - index: The option at this index will be selected
            throws NoSuchElementException If there is no option with specified index in SELECT
        """
        try:
            try:
                return self._select.select_by_index(index)
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.select_by_index(index)

    def select_by_visible_text(self, text: str) -> None:
        """
        Selenium Select API.
        Select all options that display text matching the argument.

        That is, when given "Bar" this would select an option like:
        <option value="foo">Bar</option>

        Args:
        - text: The visible text to match against
            throws NoSuchElementException If there is no option with specified text in SELECT
        """
        try:
            try:
                return self._select.select_by_visible_text(text)
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.select_by_visible_text(text)

    def deselect_all(self) -> None:
        """
        Selenium Select API.
        Clear all selected entries.
        This is only valid when the SELECT supports multiple selections.
        """
        try:
            try:
                return self._select.deselect_all()
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.deselect_all()

    def deselect_by_value(self, value: str) -> None:
        """
        Selenium Select API.
        Deselect all options that have a value matching the argument.
        That is, when given "foo" this would deselect an option like:
        <option value="foo">Bar</option>

        Args:
        - value: The value to match against
        """
        try:
            try:
                return self._select.deselect_by_value(value)
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.deselect_by_value(value)

    def deselect_by_index(self, index: int) -> None:
        """
        Selenium Select API.
        Deselect the option at the given index.
        This is done by examining the "index" attribute of an element,
        and not merely by counting.

        Args:
        - index: The option at this index will be deselected
        """
        try:
            try:
                return self._select.deselect_by_index(index)
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.deselect_by_index(index)

    def deselect_by_visible_text(self, text: str) -> None:
        """
        Selenium Select API.
        Deselect all options that display text matching the argument.
        That is, when given "Bar" this would deselect an option like:
        <option value="foo">Bar</option>

        Args:
        - text: The visible text to match against
        """
        try:
            try:
                return self._select.deselect_by_visible_text(text)
            except AttributeError:
                self._select = Select(self._present_element)
        except ElementReferenceException:
            self._select = Select(self.present_element)
        return self._select.deselect_by_visible_text(text)

    @property
    def location_in_view(self) -> dict[str, int]:
        """
        Appium API.
        Retrieve the location (coordination) of the element relative to the view when it is present.

        Return is the same as official:
        {'x': int, 'y': int}
        """
        try:
            return self._present_element.location_in_view
        except ElementReferenceException:
            return self.present_element.location_in_view

    def input(self, text: str = '') -> Element:
        """
        Selenium API
        Input text to the element.

        Args:
        - text: The text to input.

        Usage::

            my_page.my_element.input('123 456')
            my_page.my_element.input('123').space().input('456')

        """
        try:
            self._present_element.send_keys(text)
        except ElementReferenceException:
            self.present_element.send_keys(text)
        return self

    def enter(self) -> Element:
        """
        Selenium API
        Send keys ENTER to the element.

        Usage::

            my_page.my_element.input('123 456').enter()

        """
        try:
            self._present_element.send_keys(Keys.ENTER)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.ENTER)
        return self

    def select_all(self) -> Element:
        """
        Selenium API, this is NOT Select relative function.
        Send keys "COMMAND/CONTROL + A" to the element.

        Usage::

            my_page.my_element.select_all().copy()

        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'a')
        except ElementReferenceException:
            self.present_element.send_keys(first, 'a')
        return self

    def cut(self) -> Element:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + X" to the element.

        Usage::

            my_page.my_element1.cut()
            my_page.my_element2.paste()

        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'x')
        except ElementReferenceException:
            self.present_element.send_keys(first, 'x')
        return self

    def copy(self) -> Element:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + C" to the element.

        Usage::

            my_page.my_element1.copy()
            my_page.my_element2.paste()

        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'c')
        except ElementReferenceException:
            self.present_element.send_keys(first, 'c')
        return self

    def paste(self) -> Element:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + V" to the element.

        Usage::

            my_page.my_element1.copy()
            my_page.my_element2.paste()

        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'v')
        except ElementReferenceException:
            self.present_element.send_keys(first, 'v')
        return self

    def arrow_left(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys "ARROW_LEFT" to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.arrow_left(3)

        """
        try:
            self._present_element.send_keys(Keys.ARROW_LEFT * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.ARROW_LEFT * times)
        return self

    def arrow_right(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys "ARROW_RIGHT" to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.arrow_right(3)

        """
        try:
            self._present_element.send_keys(Keys.ARROW_RIGHT * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.ARROW_RIGHT * times)
        return self

    def arrow_up(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys "ARROW_UP" to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.arrow_up(3)

        """
        try:
            self._present_element.send_keys(Keys.ARROW_UP * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.ARROW_UP * times)
        return self

    def arrow_down(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys "ARROW_DOWN" to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.arrow_down(3)

        """
        try:
            self._present_element.send_keys(Keys.ARROW_DOWN * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.ARROW_DOWN * times)
        return self

    def backspace(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys BACKSPACE to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.backspace(3).input('123456').enter()

        """
        try:
            self._present_element.send_keys(Keys.BACKSPACE * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.BACKSPACE * times)
        return self

    def delete(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys DELETE to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.delete(3)

        """
        try:
            self._present_element.send_keys(Keys.DELETE * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.DELETE * times)
        return self

    def tab(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys TAB to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.tab(2)

        """
        try:
            self._present_element.send_keys(Keys.TAB * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.TAB * times)
        return self

    def space(self, times: int = 1) -> Element:
        """
        Selenium API
        Send keys SPACE to the element.

        Args:
        - times: The input times of key.

        Usage::

            my_page.my_element.space(4)

        """
        try:
            self._present_element.send_keys(Keys.SPACE * times)
        except ElementReferenceException:
            self.present_element.send_keys(Keys.SPACE * times)
        return self

    def swipe_into_view(
        self,
        direction: str = SA.V,
        border: dict | tuple = {'left': 0, 'right': 100, 'top': 0, 'bottom': 100},
        start: int = 75,
        end: int = 25,
        fix: bool | int = False,
        timeout: int | float = 3,
        max_swipe: int = 10,
        max_adjust: int = 2,
        min_distance: int = 100,
        duration: int = 1000
    ) -> Element:
        """
        DEPRECATED.
        Please use "swipe_by" or "flick_by" instead.
        """
        warnings.warn('Please use "swipe_by" or "flick_by" instead.', DeprecationWarning, stacklevel=2)

        # Get border.
        border = self.__get_border(direction, border)

        # Determine v or h, and actual swiping range.
        coordinate = self.__get_range(direction, *border, start, end, fix)

        # Start swiping and check whether it is viewable in max count of swiping.
        self.__start_swiping(*coordinate, duration, timeout, max_swipe)

        # Start adjusting when element is viewable.
        self.__start_adjusting(*border, *coordinate, max_adjust, min_distance, duration)

        # Return self to re-trigger the element finding process, thereby avoiding staleness issues.
        return self

    def __get_border(
        self,
        direction: str,
        border: dict[str, int] | tuple[int, int, int, int]
    ) -> tuple[int, int, int, int]:
        """
        DEPRECATED.
        return left, right, top, bottom
        """
        # Get border.
        if isinstance(border, dict):
            left, right, top, bottom = border.values()
        elif isinstance(border, tuple):
            left, right, top, bottom = border
        else:
            raise TypeError('Parameter "border" should be dict or tuple.')

        if 'a' not in direction.lower():
            window_left, window_top, window_width, window_height = self._page.get_window_rect().values()
            left, right = [int(window_left + window_width * x / 100) for x in (left, right)]
            top, bottom = [int(window_top + window_height * y / 100) for y in (top, bottom)]

        border = (left, right, top, bottom)
        logstack._info(f'border: {border}')
        return border

    def __get_range(
        self,
        direction: str,
        left: int,
        right: int,
        top: int,
        bottom: int,
        start: int,
        end: int,
        fix: bool | int = False
    ) -> tuple[int, int, int, int]:
        """
        DEPRECATED.
        return sx, sy, ex, ey
        """
        width = right - left
        height = bottom - top

        # Determine v or h, and actual swiping range.
        if 'v' in direction.lower():
            sy = top + int(height * start / 100)
            ey = top + int(height * end / 100)
            if fix is False:
                # border center x
                sx = ex = left + int(width / 2)
            elif fix is True:
                # element center x
                sx = ex = self.center['x']
            elif isinstance(fix, int):
                # absolute x
                sx = ex = fix
            else:
                raise TypeError('Parameter "fix" should be bool or int.')
        elif 'h' in direction.lower():
            sx = left + int(width * start / 100)
            ex = left + int(width * end / 100)
            if fix is False:
                # border center y
                sy = ey = top + int(height / 2)
            elif fix is True:
                # element center y
                sy = ey = self.center['y']
            elif isinstance(fix, int):
                # absolute y
                sy = ey = fix
            else:
                raise TypeError('Parameter "fix" should be bool or int.')
        else:
            raise ValueError(f'Parameter "dirtype" should be {SA.V}, {SA.VA}, {SA.H} or {SA.HA}.')

        coordinate = (sx, sy, ex, ey)
        logstack._info(f'coordinate: {coordinate}')
        return coordinate

    def __start_swiping(
        self,
        sx: int,
        sy: int,
        ex: int,
        ey: int,
        duration: int,
        timeout: int | float,
        max_swipe: int
    ) -> int | Literal[False]:
        """
        DEPRECATED.
        Return viewable or not.
        """
        logstack._info(f'Start swiping to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                logstack._warning(
                    f'Stop swiping to element {self.remark} as the maximum swipe count of {max_swipe} has been reached.')
                return False
            self.driver.swipe(sx, sy, ex, ey, duration)
            count += 1
        logstack._info(f'End swiping as the element {self.remark} is now viewable.')
        return count

    def __start_adjusting(
        self,
        left: int,
        right: int,
        top: int,
        bottom: int,
        sx: int,
        sy: int,
        ex: int,
        ey: int,
        max_adjust: int,
        min_distance: int,
        duration: int
    ) -> int | Literal[False]:
        """
        DEPRECATED.
        Start adjusting.
        """
        logstack._info(f'Start adjusting to element {self.remark}')
        for i in range(1, max_adjust + 2):
            element_left, element_right, element_top, element_bottom = self.border.values()
            delta_left = left - element_left
            delta_right = element_right - right
            delta_top = top - element_top
            delta_bottom = element_bottom - bottom
            if delta_left > 0:
                logstack._info(f'Adjust {i}: swipe right.')
                adjust_distance = delta_left if delta_left > min_distance else min_distance
                ex = sx + int(adjust_distance)
            elif delta_right > 0:
                logstack._info(f'Adjust {i}: swipe left.')
                adjust_distance = delta_right if delta_right > min_distance else min_distance
                ex = sx - int(adjust_distance)
            elif delta_top > 0:
                logstack._info(f'Adjust {i}: swipe down.')
                adjust_distance = delta_top if delta_top > min_distance else min_distance
                ey = sy + int(adjust_distance)
            elif delta_bottom > 0:
                logstack._info(f'Adjust {i}: swipe up.')
                adjust_distance = delta_bottom if delta_bottom > min_distance else min_distance
                ey = sy - int(adjust_distance)
            else:
                logstack._info(f'End adjusting as the element {self.remark} border is in view border.')
                return i
            if i == max_adjust + 1:
                logstack._warning(
                    f'End adjusting to the element {self.remark} as the maximum adjust count of {max_adjust} has been reached.')
                return False
            self.driver.swipe(sx, sy, ex, ey, duration)

    def wait_not_present(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        DEPRECATED.
        Please use `wait_absent` instead.
        """
        warnings.warn('Please use "wait_absent" instead.', DeprecationWarning, stacklevel=2)
        return self.wait_absent(timeout, reraise)

    def wait_not_visible(
        self,
        timeout: int | float | None = None,
        present: bool = True,
        reraise: bool | None = None
    ) -> WebElement | bool:
        """
        DEPRECATED.
        Please use `wait_invisible` instead.
        """
        warnings.warn('Please use "wait_invisible" instead.', DeprecationWarning, stacklevel=2)
        return self.wait_invisible(timeout, present, reraise)

    def wait_not_clickable(
        self,
        timeout: int | float | None = None,
        present: bool = True,
        reraise: bool | None = None
    ) -> WebElement | bool:
        """
        DEPRECATED.
        Please use `wait_unclickable` instead.
        """
        warnings.warn('Please use "wait_unclickable" instead.', DeprecationWarning, stacklevel=2)
        return self.wait_unclickable(timeout, present, reraise)

    def wait_not_selected(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        DEPRECATED.
        Please use `wait_unselected` instead.
        """
        warnings.warn('Please use "wait_unselected" instead.', DeprecationWarning, stacklevel=2)
        return self.wait_unselected(timeout, reraise)
