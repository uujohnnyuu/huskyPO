# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# We do not store found elements within the Elements class because
# the results of find_elements can easily change due to platform or operational differences.
# Therefore, searching again each time is more robust and can help avoid unexpected errors.
# If there is a need for repeated use,
# you can construct a custom function or
# inherit from this class to define your own handling.

# TODO Keep tracking selenium 4.0 and appium 2.0 new methods.


from __future__ import annotations

import warnings
from typing import Type, TypeVar, Literal

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.types import WaitExcTypes

from . import ec_extension as ecex
from .config import Timeout
from .by import ByAttribute
from .page import Page
from .types import WebDriver, WebElement


P = TypeVar('P', bound=Page)


class Elements:

    def __init__(
        self,
        by: str | None = None,
        value: str | None = None,
        timeout: int | float | None = None,
        remark: str | None = None
    ) -> None:
        """
        Initial Elements attributes.

        Args:
        - by: The locator strategy. You can use all `By` methods as `from huskypo import By`.
        - value: The locator value.
        - timeout: Element timeout in seconds of explicit wait.
        - remark: Comments convenient for element identification, or logging.

        Usage (without parameter name)::

            # (by, value):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid')

            # (by, value, timeout):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid', 10)

            #(by, value, remark):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid', 'these are xxx')

            # (by, value, timeout, remark):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid', 10, 'these are xxx')

        """
        # (by, value)
        # Allowing `None` to initialize an empty descriptor for dynamic elements.
        if by not in ByAttribute.VALUES_WITH_NONE:
            raise ValueError(f'The locator strategy "{by}" is undefined.')
        if not isinstance(value, (str, type(None))):
            raise TypeError(f'The locator value type should be "str", not "{type(self._value).__name__}".')
        self._by = by
        self._value = value

        # (by, value, timeout)
        self._timeout = timeout
        # (by, value, remark)
        if not isinstance(timeout, (int, float, type(None))):
            remark = str(timeout)
            self._timeout = None

        # (by, value, timeout, remark)
        self._remark = remark

    def __get__(self, instance: P, owner: Type[P] | None = None) -> Elements:
        """
        Internal use.
        Dynamically obtain the instance of Page and
        execute the corresponding function only when needed.
        """
        self._page = instance
        return self

    def __set__(self, instance: P, value: tuple | dict) -> None:
        """
        Internal use.
        Dynamically set element attribute values at runtime,
        typically used for configuring dynamic elements.
        """
        if isinstance(value, tuple):
            self.__init__(*value)
        elif isinstance(value, dict):
            self.__init__(**value)
        else:
            raise TypeError('Please configure dynamic elements according to the logic of the Elements parameters.')

    @property
    def by(self) -> str | None:
        return self._by

    @property
    def value(self) -> str | None:
        return self._value

    @property
    def locator(self) -> tuple[str, str]:
        """
        Return locator (by, value)
        """
        if self._by and self._value:
            return (self._by, self._value)
        raise ValueError(
            '"by" and "value" cannot be None when performing elements operations. Please ensure both are provided with valid values.')

    @property
    def timeout(self):
        """
        The initial timeout of the elements.
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
    def remark(self):
        """
        The remark of the elements.
        If init remark is None, return (by="by", value="value").
        """
        return f'(by="{self._by}", value="{self._value}")' if self._remark is None else self._remark

    @remark.setter
    def remark(self, new_remark) -> None:
        self._remark = new_remark

    @property
    def driver(self) -> WebDriver:
        """
        Get driver from Page.
        """
        return self._page._driver

    def find_elements(self) -> list[WebElement]:
        """
        Using the traditional find_elements method
        to locate elements without any waiting behavior.
        It is recommended for use in situations where no waiting is required.
        Note that if there are no any element found,
        it will return empty list `[]`.
        """
        return self.driver.find_elements(*self.locator)

    def wait(
        self,
        timeout: int | float | None = None,
        ignored_exceptions: WaitExcTypes | None = None
    ) -> WebDriverWait:
        """
        Get an object of WebDriverWait.
        The ignored exceptions include NoSuchElementException and StaleElementReferenceException
        to capture their stacktrace when a TimeoutException occurs.

        Args:
        - timeout: The maximum time in seconds to wait for the expected condition.
            By default, it initializes with the element timeout.
        - ignored_exceptions: iterable structure of exception classes ignored during calls.
            By default, it contains NoSuchElementException only.
        """
        self._wait_timeout = self.timeout if timeout is None else timeout
        return WebDriverWait(self.driver, self._wait_timeout, ignored_exceptions=ignored_exceptions)

    @property
    def wait_timeout(self):
        """
        Get the final waiting timeout of the element.
        If no element action has been executed yet,
        it will return None.
        """
        try:
            return self._wait_timeout
        except AttributeError:
            return None

    def __timeout_message(self, status: str) -> str:
        """
        Waiting for elements "{self.remark}" to become "{status}" timed out after {self._wait_timeout} seconds.
        """
        return f'Waiting for elements "{self.remark}" to become "{status}" timed out after {self._wait_timeout} seconds.'

    def find(
        self,
        index: int | None = None,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> list[WebElement] | WebElement | Literal[False]:
        """
        Selenium and Appium API.
        Wait for the element or elements to be `present`.

        Args:
        - index:
            - int: It will returns an element by list index of elements.
            - None: It will returns all elements.
        - timeout: Maximum time in seconds to wait for the element or elements to become present.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - list[WebElement]: All elements when index is None.
        - WebElement: Element by list index of elements when index is int.
        - False: No any element is present.
        """
        elements = self.wait_all_present(timeout, reraise)
        if index is not None:
            try:
                return elements[index]
            except TypeError:
                # Catch TypeError: False[index] if reraise is False.
                # We reraise TimeoutException to indicate that elements are not present after timeout.
                raise TimeoutException(self.__timeout_message('all present'))
        return elements

    @property
    def present_elements(self) -> list[WebElement]:
        """
        Obtaining all present webelements simply.
        The same as element.wait_all_present(reraise=True).
        Note that a TimeoutException will be raised
        if all elements are abesent within the timeout period.
        """
        return self.wait_all_present(reraise=True)

    @property
    def all_visible_elements(self) -> list[WebElement]:
        """
        Obtaining all visible webelements simply.
        The same as element.wait_all_visible(reraise=True).
        Note that a TimeoutException will be raised
        if at least one element is invisible or absent within the timeout period.
        """
        return self.wait_all_visible(reraise=True)

    @property
    def any_visible_elements(self) -> list[WebElement]:
        """
        Obtaining any visible webelements simply.
        The same as element.wait_any_visible(reraise=True).
        Note that a TimeoutException will be raised
        if all elements are invisible or absent within the timeout period.
        """
        return self.wait_any_visible(reraise=True)

    def wait_all_present(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> list[WebElement] | Literal[False]:
        """
        Waiting for `any elements to become present`.
        Note that `all` here means `at least one (any)` for
        the logic of find_elements is to find at least one matched elements.

        Args:
        - timeout: The maximum time (in seconds) to wait for the elements to reach the expected state.
            Defaults (None) to the elements' timeout value.
        - reraise: When the elements state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - list[WebElement] (Expected): The elements reached the expected status before the timeout.
        - False (Unexpected): The elements did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the elements did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.presence_of_all_elements_located(self.locator),
                self.__timeout_message('any elements are present'))
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_all_absent(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Waiting for `all elements to become absent`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the elements to reach the expected state.
            Defaults (None) to the elements' timeout value.
        - reraise: When the elements state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - True (Expected): The elements reached the expected status before the timeout.
        - False (Unexpected): The elements did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the elements did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.absence_of_all_elements_located(self.locator),
                self.__timeout_message('all elements are absent'))
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_all_visible(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> list[WebElement] | Literal[False]:
        """
        Waiting for `all elements to become visible`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the elements to reach the expected state.
            Defaults (None) to the elements' timeout value.
        - reraise: When the elements state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - list[WebElement] (Expected): The elements reached the expected status before the timeout.
        - False (Unexpected): The elements did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the elements did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout, StaleElementReferenceException).until(
                ecex.visibility_of_all_elements_located(self.locator),
                self.__timeout_message('all elements are visible'))
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_any_visible(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> list[WebElement] | Literal[False]:
        """
        Waiting for `any elements to become visible`.

        Args:
        - timeout: The maximum time (in seconds) to wait for the elements to reach the expected state.
            Defaults (None) to the elements' timeout value.
        - reraise: When the elements state is not as expected, the behavior can be set in the following ways:
            - bool: True indicates to reraise a TimeoutException; False means to return False.
            - None: Follow the config.Timeout.RERAISE setting, which is a boolean.
                Its logic is the same as the boolean, and the default is True.

        Returns:
        - list[WebElement] (Expected): The elements reached the expected status before the timeout.
        - False (Unexpected): The elements did not reach the expected status after the timeout
            if TimeoutException is not reraised.

        Exception:
        - TimeoutException: Raised if "reraise" is True and
            the elements did not reach the expected status after the timeout.
        """
        try:
            return self.wait(timeout, StaleElementReferenceException).until(
                ecex.visibility_of_any_elements_located(self.locator),
                self.__timeout_message('any elements are visible'))
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def are_all_present(self, timeout: int | float | None = None) -> bool:
        """
        Selenium and Appium API.
        Whether the all elements are present.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.

        Returns:
        - True: All the elements are present before timeout.
        - False: All the elements are still not present after timeout.
        """
        return True if self.wait_all_present(timeout, False) else False

    def are_all_visible(self) -> bool:
        """
        Selenium and Appium API.
        Whether all the elements are visible.

        Returns:
        - True: All the elements are visible.
        - False: At least one element is not visible.
        """
        for element in self.present_elements:
            if not element.is_displayed():
                return False
        return True

    def are_any_visible(self) -> bool:
        """
        Selenium and Appium API.
        Whether at least one element is visible.

        Returns:
        - True: At least one element is visible.
        - False: All the elements are not visible.
        """
        return True if [element for element in self.present_elements if element.is_displayed()] else False

    @property
    def quantity(self) -> int:
        """
        Selenium and Appium API.
        Get the quantity of all present elements.
        """
        try:
            return len(self.present_elements)
        except TimeoutException:
            return 0

    @property
    def all_visible_quantity(self) -> int:
        """
        Selenium and Appium API.
        Get the quantity of all visible elements.
        """
        try:
            return len(self.all_visible_elements)
        except TimeoutException:
            return 0

    @property
    def any_visible_quantity(self) -> int:
        """
        Selenium and Appium API.
        Get the quantity of any visible elements.
        """
        try:
            return len(self.any_visible_elements)
        except TimeoutException:
            return 0

    @property
    def texts(self) -> list[str]:
        """
        Selenium and Appium API.
        Gets texts of all present elements.
        """
        return [element.text for element in self.present_elements]

    @property
    def all_visible_texts(self) -> list[str]:
        """
        Selenium and Appium API.
        Gets texts of all visible elements.
        """
        return [element.text for element in self.all_visible_elements]

    @property
    def any_visible_texts(self) -> list[str]:
        """
        Selenium and Appium API.
        WebElements: find_elements(by, value)
        Gets texts of `at least one` visible element.
        """
        return [element.text for element in self.any_visible_elements]

    @property
    def rects(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations relative to the view and size of all present elements.
        """
        return [
            {'x': rect['x'], 'y': rect['y'], 'width': rect['width'], 'height': rect['height']}
            for element in self.present_elements
            for rect in [element.rect]
        ]

    @property
    def all_visible_rects(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations relative to the view and size of all visible elements.
        """
        return [
            {'x': rect['x'], 'y': rect['y'], 'width': rect['width'], 'height': rect['height']}
            for element in self.all_visible_elements
            for rect in [element.rect]
        ]

    @property
    def any_visible_rects(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations relative to the view and size of any visible elements.
        """
        return [
            {'x': rect['x'], 'y': rect['y'], 'width': rect['width'], 'height': rect['height']}
            for element in self.any_visible_elements
            for rect in [element.rect]
        ]

    @property
    def locations(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations of all present elements.
        """
        return [element.location for element in self.present_elements]

    @property
    def all_visible_locations(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations of all visible elements.
        """
        return [element.location for element in self.all_visible_elements]

    @property
    def any_visible_locations(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations of any visible elements.
        """
        return [element.location for element in self.any_visible_elements]

    @property
    def sizes(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets sizes of all present elements.
        Note that it will rearrange size to {'width': width, 'height': height}
        """
        return [
            {'width': size['width'], 'height': size['height']}
            for element in self.present_elements
            for size in [element.size]
        ]

    @property
    def all_visible_sizes(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets sizes of all visible elements.
        Note that it will rearrange size to {'width': width, 'height': height}
        """
        return [
            {'width': size['width'], 'height': size['height']}
            for element in self.all_visible_elements
            for size in [element.size]
        ]

    @property
    def any_visible_sizes(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets sizes of any visible elements.
        Note that it will rearrange size to {'width': width, 'height': height}
        """
        return [
            {'width': size['width'], 'height': size['height']}
            for element in self.any_visible_elements
            for size in [element.size]
        ]

    @property
    def centers(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets center locations relative to the view of all present elements.
        """
        return [
            {'x': int(rect['x'] + rect['width'] / 2), 'y': int(rect['y'] + rect['height'] / 2)}
            for element in self.present_elements
            for rect in [element.rect]
        ]

    @property
    def all_visible_centers(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets center locations relative to the view of all visible elements.
        """
        return [
            {'x': int(rect['x'] + rect['width'] / 2), 'y': int(rect['y'] + rect['height'] / 2)}
            for element in self.all_visible_elements
            for rect in [element.rect]
        ]

    @property
    def any_visible_centers(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets center locations relative to the view of any visible elements.
        """
        return [
            {'x': int(rect['x'] + rect['width'] / 2), 'y': int(rect['y'] + rect['height'] / 2)}
            for element in self.any_visible_elements
            for rect in [element.rect]
        ]

    def get_attributes(self, name: str) -> list[str | dict | None]:
        """
        Selenium and Appium API.
        Gets specific attributes or properties of all present elements.
        """
        return [element.get_attribute(name) for element in self.present_elements]

    def get_all_visible_attributes(self, name: str) -> list[str | dict | None]:
        """
        Selenium and Appium API.
        Gets specific attributes or properties of all visible elements.
        """
        return [element.get_attribute(name) for element in self.all_visible_elements]

    def get_any_visible_attributes(self, name: str) -> list[str | dict | None]:
        """
        Selenium and Appium API.
        Gets specific attributes or properties of any visible elements.
        """
        return [element.get_attribute(name) for element in self.any_visible_elements]

    def get_properties(self, name: str) -> list[WebElement | bool | dict | str]:
        """
        Selenium API.
        Gets specific properties of all present elements.
        """
        return [element.get_property(name) for element in self.present_elements]

    def get_all_visible_properties(self, name: str) -> list[WebElement | bool | dict | str]:
        """
        Selenium API.
        Gets specific properties of all visible elements.
        """
        return [element.get_property(name) for element in self.all_visible_elements]

    def get_any_visible_properties(self, name: str) -> list[WebElement | bool | dict | str]:
        """
        Selenium API.
        Gets specific properties of any visible elements.
        """
        return [element.get_property(name) for element in self.any_visible_elements]

    @property
    def locations_in_view(self) -> list[dict[str, int]]:
        """
        Appium API.
        Gets locations relative to the view of all present elements.
        """
        return [element.location_in_view for element in self.present_elements]

    @property
    def all_visible_locations_in_view(self) -> list[dict[str, int]]:
        """
        Appium API.
        Gets locations relative to the view of all visible elements.
        """
        return [element.location_in_view for element in self.all_visible_elements]

    @property
    def any_visible_locations_in_view(self) -> list[dict[str, int]]:
        """
        Appium API.
        Gets locations relative to the view of any visible elements.
        """
        return [element.location_in_view for element in self.any_visible_elements]

    def wait_all_not_present(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        DEPRECATED.
        Please use `wait_all_absent` instead.
        """
        warnings.warn('Please use "wait_all_absent" instead.', DeprecationWarning, stacklevel=2)
        return self.wait_all_absent(timeout, reraise)
