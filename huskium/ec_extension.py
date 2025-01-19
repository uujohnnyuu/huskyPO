# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium

"""
All you need to know about this Expected Conditions Extension (ECEX):
1. ECEX extends all methods related to element states.
2. Allows explicit waits using `find_elements(*locator)[index]`.
   You can set the `index` parameter in each method.
3. Separates methods for locators and WebElements to enable more robust exception management.
"""


from __future__ import annotations

from typing import Callable, Literal

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from .types import AppiumWebDriver, WebDriver, WebElement


def _find_element_by(
    driver: WebDriver,
    locator: tuple[str, str],
    index: int | None
) -> WebElement:
    """
    index:
        - None: `driver.find_element(*locator)`
        - int: `driver.find_elements(*locator)[index]`,
            and treat `IndexError` as `NoSuchElementException`.
    """
    if index is None:
        return driver.find_element(*locator)
    try:
        return driver.find_elements(*locator)[index]
    except IndexError:
        raise NoSuchElementException


def _find_elements_by(
    driver: WebDriver,
    locator: tuple[str, str]
) -> list[WebElement]:
    """
    Return driver.find_elements(*locator).
    if elements == []: raise NoSuchElementException
    """
    elements = driver.find_elements(*locator)
    if elements == []:
        raise NoSuchElementException
    return elements


def presence_of_element_located(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement]:
    """
    Whether the element is present.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]

    Return:
        - WebElement: The element is present.

    WebDriverWait ignored exceptions:
        - NoSuchElementException (default)

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        return _find_element_by(driver, locator, index)

    return _predicate


def presence_of_all_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    Whether there are at least one elements can be found by the locator.
    Note that "all" here means "at least one"
    for the logic of "find_elements" is to find "at least one matched elements".

    Args:
        - locator: (by, value)

    Return:
        - list[WebElement]: WebElements.
        - []: No any elements are found.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        return driver.find_elements(*locator)

    return _predicate


def absence_of_element_located(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], bool]:
    """
    Whether the element is absent.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]

    Return:
        - True: The element is absent.
        - False: The element is present.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        try:
            _find_element_by(driver, locator, index)
            return False
        except NoSuchElementException:
            return True

    return _predicate


def absence_of_all_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], bool]:
    """
    Whether all the elements are absent by the locator.
    This is completely opposite to `presence_of_all_elements_located`.

    Args:
        - locator: (by, value)

    Return:
        - True: All the elements are absent.
        - False: At least one element is present.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        return not driver.find_elements(*locator)

    return _predicate


def visibility_of_element_located(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is visible.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]

    Return:
        - WebElement: The element is visible.
        - False: The element is present and invisible.

    WebDriverWait ignored exceptions:
        - NoSuchElementException (default)
        - StaleElementReferenceException (optional)

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        element = _find_element_by(driver, locator, index)
        return element if element.is_displayed() else False

    return _predicate


def visibility_of_element(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is visible.

    Args:
        - element: WebElement

    Return:
        - WebElement: The element is visible.
        - False: The element is present and invisible.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - StaleElementReferenceException (optional): retry by `visibility_of_element_located`.
    """

    def _predicate(_):
        return element if element.is_displayed() else False

    return _predicate


def visibility_of_any_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    Whether any (at least one) elements are visible.

    Args:
        - locator: (by, value)

    Return:
        - list[WebElement]: At least one element is visible.
        - [] (empty list): All elements are present and invisible.

    WebDriverWait ignored exceptions:
        - NoSuchElementException (default): All elements are absent.
        - StaleElementReferenceException (optional): At least one element is stale.

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        return [
            element
            for element in _find_elements_by(driver, locator)
            if element.is_displayed()
        ]

    return _predicate


def visibility_of_all_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement] | Literal[False]]:
    """
    Whether all elements are visible.

    Args:
        - locator: (by, value)

    Return:
        - list[WebElement]: All elements are visible.
        - False: At least one of the element is present and invisible.

    WebDriverWait ignored exceptions:
        - NoSuchElementException (default): All the elements are absent.
        - StaleElementReferenceException (optional): At least one element is staled.

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        elements = _find_elements_by(driver, locator)
        for element in elements:
            if not element.is_displayed():
                return False
        return elements

    return _predicate


def invisibility_of_element_located(
    locator: tuple[str, str],
    index: int | None,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Whether the element is invisible.
    The logic for invisibility is determined by the "present" parameter.
    See the Args section for details.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]
        - present: Whether the element must be present or not.
            - True: The element must be present and invisible.
            - False: The element can be absent.

    Return:
        - WebElement: The element is present and invisible.
        - True: The element is absent and "present" is False.
        - False: The element is visible.

    WebDriverWait ignored exceptions (when "present" is True):
        - NoSuchElementException (default)
        - StaleElementReferenceException (optional)

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if not element.is_displayed() else False
        except (NoSuchElementException, StaleElementReferenceException):
            if present:
                raise
            return True

    return _predicate


def invisibility_of_element(
    element: WebElement,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Whether the element is invisible.
    The logic for invisibility is determined by the "present" parameter.
    See the Args section for details.

    Args:
        - element: WebElement
        - present: Whether the element must be present or not.
            - True: The element must be present and invisible.
            - False: The element can be absent.

    Return:
        - WebElement: The element is present and invisible.
        - True: The element is absent and "present" is False.
        - False: The element is visible.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - StaleElementReferenceException (optional): retry by `invisibility_of_element_located`.
    """

    def _predicate(_):
        try:
            return element if not element.is_displayed() else False
        except StaleElementReferenceException:
            if present:
                raise
            return True

    return _predicate


def element_located_to_be_clickable(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is clickable.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is clickable.
    - False: The element is present and unclickable.

    WebDriverWait ignored exceptions:
        - NoSuchElementException (default)
        - StaleElementReferenceException (optional)

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        element = _find_element_by(driver, locator, index)
        return element if element.is_displayed() and element.is_enabled() else False

    return _predicate


def element_to_be_clickable(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is clickable.

    Args:
        - element: WebElement

    Return:
        - WebElement: The element is clickable.
        - False: The element is present and unclickable.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - StaleElementReferenceException (optional): Retry by `element_located_to_be_clickable`.
    """

    def _predicate(_):
        return element if element.is_displayed() and element.is_enabled() else False

    return _predicate


def element_located_to_be_unclickable(
    locator: tuple[str, str],
    index: int | None,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Whether the element is unclickable.
    The logic for being unclickable is determined by the "present" parameter.
    See the Args section for details.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]
        - present: Whether element must be present or not.
            - True (default): The element must be present and unclickable.
            - False: The element can be absent.

    Return:
        - WebElement: The element is present and unclickable.
        - True: The element is absent and "present" is False.
        - False: The element is clickable.

    WebDriverWait ignored exceptions (when "present" is True):
        - NoSuchElementException (default)
        - StaleElementReferenceException (optional)

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if not (element.is_displayed() and element.is_enabled()) else False
        except (NoSuchElementException, StaleElementReferenceException):
            if present:
                raise
            return True

    return _predicate


def element_to_be_unclickable(
    element: WebElement,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Whether the element is present and unclickable.
    The logic for being unclickable is determined by the "present" parameter.
    See the Args section for details.

    Args:
        - element: WebElement
        - present: Whether element must be present or not.
            - True (default): The element must be present and unclickable.
            - False: The element can be absent.

    Return:
        - WebElement: The element is present and unclickable.
        - True: The element is absent and "present" is False.
        - False: The element is clickable.

    WebDriverWait ignored exceptions (when "present" is True):
        - Unnecessary

    External exception handling:
        - StaleElementReferenceException (optional): Retry by `element_located_to_be_unclickable`.
    """

    def _predicate(_):
        try:
            return element if not (element.is_displayed() and element.is_enabled()) else False
        except StaleElementReferenceException:
            if present:
                raise
            return True

    return _predicate


def element_located_to_be_selected(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is selected.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]

    Return:
        - WebElement: The element is selected.
        - False: The element is unselected.

    WebDriverWait ignored exceptions:
        - NoSuchElementException (default)
        - StaleElementReferenceException (optional)

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        element = _find_element_by(driver, locator, index)
        return element if element.is_selected() else False

    return _predicate


def element_to_be_selected(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is selected.

    Args:
        - element: WebElement

    Return:
        - WebElement: The element is selected.
        - False: The element is unselected.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - StaleElementReferenceException (optional): Retry by `element_located_to_be_selected`.
    """

    def _predicate(_):
        return element if element.is_selected() else False

    return _predicate


def element_located_to_be_unselected(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is unselected.

    Args:
        - locator: (by, value)
        - index:
            - None: driver.find_element(*locator)
            - int: driver.find_elements(*locator)[index]

    Return:
        - WebElement: The element is unselected.
        - False: The element is selected.

    WebDriverWait ignored exceptions:
        - NoSuchElementException (default)
        - StaleElementReferenceException (optional)

    External exception handling:
        - Unnecessary
    """

    def _predicate(driver: WebDriver):
        element = _find_element_by(driver, locator, index)
        return element if not element.is_selected() else False

    return _predicate


def element_to_be_unselected(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is unselected.

    Args:
        - element: WebElement

    Return:
        - WebElement: The element is unselected.
        - False: The element is selected.

    WebDriverWait ignored exceptions:
        - Unnecessary

    External exception handling:
        - StaleElementReferenceException (optional): Retry by `element_located_to_be_unselected`.
    """

    def _predicate(_):
        return element if not element.is_selected() else False

    return _predicate


def webview_is_present(
    switch: bool = True,
    index: int = -1
) -> Callable[[AppiumWebDriver], list[str] | Literal[False]]:
    """
    Whether "WEBVIEW" context is present.

    Args:
        - switch: Switch to the WEBVIEW context when it exists and "switch" is True.
        - index: Switch to the specified context index, defaulting to the most recently appeared.

    Returns:
        - list[str] (contexts): Returns all current contexts when a WEBVIEW exists.
        - False: Returns False when no WEBVIEW exists.
    """

    def _predicate(driver: AppiumWebDriver):
        contexts = driver.contexts
        if any('WEBVIEW' in context for context in contexts):
            if switch:
                driver.switch_to.context(contexts[index])
            return contexts
        return False

    return _predicate
