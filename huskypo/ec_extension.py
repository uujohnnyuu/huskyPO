# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# All you need to know about this expected conditions extension (ECEX):

# 1. ECEX extends all methods related to element states,
# including present, visible, clickable, selected, and their opposites.

# 2. You can perform explicit waits using find_elements(*locator)[index]
# when you set index in each method.

# 3. ECEX separates the methods for locators and WebElements
# because these two approaches should handle exceptions differently,
# allowing for more comprehensive exception handling.


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
    Extended `presence_of_element_located`.
    Whether the element is present.

    Args:
    - locator: (by, value)
    - index:
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is present.

    Exception handling:
    - WebDriverWait:
        - NoSuchElementException (default)
    - Other external process: Unnecessary.

    """

    def _predicate(driver: WebDriver):
        return _find_element_by(driver, locator, index)

    return _predicate


def presence_of_all_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    Extended `presence_of_all_elements_located`.
    Whether there are `at least one` elements can be found by the locator.
    Note that `all` here means `at least one` for the logic of `find_elements`
    is to find `at least one matched elements`.

    Args:
    - locator: (by, value)

    Return:
    - list[WebElement]: WebElements.
    - []: No any elements are found.

    Exception handling:
    - WebDriverWait: Unnecessary.
    - Other external process: Unnecessary.
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

    Exception handling:
    - WebDriverWait: Unnecessary.
    - Other external process: Unnecessary.
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
    Whether `all the elements are absent` by the locator.
    Note that this is completely opposite to presence_of_all_elements_located.

    Args:
    - locator: (by, value)

    Return:
    - True: All the elements are absent.
    - False: At least one element is present.

    Exception handling:
    - WebDriverWait: Unnecessary.
    - Other external process: Unnecessary.
    """

    def _predicate(driver: WebDriver):
        return not driver.find_elements(*locator)

    return _predicate


def visibility_of_element_located(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `visibility_of_element_located`.
    Whether the element is visible.

    Args:
    - locator: (by, value)
    - index:
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is visible.
    - False: The element is present and invisible.

    Exception handling:
    - WebDriverWait:
        - NoSuchElementException (default)
        - StaleElementReferenceException
    - Other external process: Unnecessary.
    """

    def _predicate(driver: WebDriver):
        element = _find_element_by(driver, locator, index)
        return element if element.is_displayed() else False

    return _predicate


def visibility_of_element(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `visibility_of`.
    Whether the element is visible.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is visible.
    - False: The element is present and invisible.

    Exception handling:
    - WebDriverWait: Unnecessary.
    - Other external process:
        - StaleElementReferenceException: The element is stale and retry by the locator.
    """

    def _predicate(_):
        return element if element.is_displayed() else False

    return _predicate


def visibility_of_any_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    Extended `visibility_of_any_elements_located`.
    Whether any (at least one) elements are visible.

    Args:
    - locator: (by, value)

    Return:
    - list[WebElement]: At least one element is visible.
    - [] (empty list): All elements are present and invisible.

    Exception handling:
    - WebDriverWait:
        - NoSuchElementException: All elements are absent.
        - StaleElementReferenceException: At least one element is stale.
    - Other external process: Unnecessary.
    """

    def _predicate(driver: WebDriver):
        return [element for element in _find_elements_by(driver, locator) if element.is_displayed()]

    return _predicate


def visibility_of_all_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement] | Literal[False]]:
    """
    Extended `visibility_of_all_elements_located`.
    Whether all elements are visible.

    Args:
    - locator: (by, value)

    Return:
    - list[WebElement]: All elements are visible.
    - False: At least one of the element is present and invisible.

    Exception handling:
    - WebDriverWait:
        - NoSuchElementException: All the elements are absent.
        - StaleElementReferenceException: At least one element is staled.
    - Other external process: Unnecessary.
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
    Extended `invisibility_of_element_located`.
    This condition depends on the present parameter and has the following two cases:
    - present=True: Only allows the element to be present and invisible.
    - present=False: Allows the element to be present and invisible,
        or to be absent at all.

    Args:
    - locator: (by, value)
    - index:
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    - present: Whether the element should be present or not.
        - True: Element should be present and invisible.
        - False: Element can be present and invisible, or absent at all.

    Return:
    - WebElement: The element is present and invisible.
    - True: The element is absent and "present" is False.
    - False: The element is visible.

    Exception handing:
    - WebDriverWait (when "present" is True):
        - NoSuchElementException (default)
        - StaleElementReferenceException
    - Other external process: Unnecessary.
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
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `invisibility_of_element`.
    Whether the element is present and invisible.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is present and invisible.
    - False: The element is visible.

    Exception handing:
    - WebDriverWait: Unnecessary.
    - Other external process:
        - StaleElementReferenceException:
            - The element should be present: retry by the locator.
            - The element can be absent: return True.
    """

    def _predicate(_):
        return element if not element.is_displayed() else False

    return _predicate


def element_located_to_be_clickable(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_clickable`.
    Whether the element is clickable.

    Args:
    - locator: (by, value)
    - index:
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is clickable.
    - False: The element is present and unclickable.

    Exception handing:
    - WebDriverWait:
        - NoSuchElementException (default)
        - StaleElementReferenceException
    - Other external process: Unnecessary.
    """

    def _predicate(driver: WebDriver):
        element = _find_element_by(driver, locator, index)
        return element if element.is_displayed() and element.is_enabled() else False

    return _predicate


def element_to_be_clickable(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_clickable`.
    Whether the element is clickable.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is clickable.
    - False: The element is present and unclickable.

    Exception handling:
    - WebDriverWait: Unnecessary.
    - Other external process:
        - StaleElementReferenceException: The element is stale and retry by the locator.
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
    This condition depends on the present parameter and has the following two cases:
    - present=True: Only allows the element to be present and unclickable.
    - present=False: Allows the element to be present and unclickable,
        or to be absent at all.

    Args:
    - locator: (by, value)
    - index:
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    - present: Whether element should be present or not.
        - True: Element should be present and unclickable.
        - False: Element can be present and unclickable, or absent at all.

    Return:
    - WebElement: The element is present and unclickable.
    - True: The element is absent and "present" is False.
    - False: The element is clickable.

    Exception handing:
    - WebDriverWait (when "present" is True):
        - NoSuchElementException (default)
        - StaleElementReferenceException
    - Other external process: Unnecessary.
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
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is present and unclickable.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is present and unclickable.
    - False: The element is clickable.

    Exception handing:
    - WebDriverWait: Unnecessary.
    - Other external process:
        - StaleElementReferenceException:
            - The element should be present: retry by the locator.
            - The element can be absent: return True.
    """

    def _predicate(_):
        return element if not (element.is_displayed() and element.is_enabled()) else False

    return _predicate


def element_located_to_be_selected(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_located_to_be_selected`.
    Whether the element is selected.

    Args:
    - locator: (by, value)
    - index:
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is selected.
    - False: The element is unselected.

    Exception handing:
    - WebDriverWait:
        - NoSuchElementException (default)
        - StaleElementReferenceException
    - Other external process: Unnecessary.
    """

    def _predicate(driver: WebDriver):
        element = _find_element_by(driver, locator, index)
        return element if element.is_selected() else False

    return _predicate


def element_to_be_selected(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_selected`.
    Whether the element is selected.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is selected.
    - False: The element is unselected.

    Exception handling:
    - WebDriverWait: Unnecessary.
    - Other external process:
        - StaleElementReferenceException: The element is stale and retry by the locator.
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

    Exception handing:
    - WebDriverWait:
        - NoSuchElementException (default)
        - StaleElementReferenceException
    - Other external process: Unnecessary.
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

    Exception handling:
    - WebDriverWait: Unnecessary.
    - Other external process:
        - StaleElementReferenceException: The element is stale and retry by the locator.
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
