# huskium
---

## Copyright
- Developer: Johnny Chou
---

## Overview
- **huskium** is a Page Object framework built on Selenium and Appium.
- **huskium** leverages Python’s data descriptors to simplify and enhance UI automation.
---

## Usage
- **Build page objects** simply and elegantly using the `Page` and `Element(s)` classes.
- **Write test scripts** simply and elegantly using the constructed Page objects.
---

## Page Object Example Code
1. Construct a Page object in any Python file, each page recommended to be a separate Page class.
```python
# my_page.py


from huskium import Page, Element, Elements
from huskium import By
from huskium import dynamic


class MyPage(Page):
    
    # Static element: The most common way to set up Page objects.
    # Element is a data descriptor of Page, allowing simple setup as shown below:
    search_field = Element(By.NAME, 'q', remark='Search input box')
    search_results = Elements(By.TAG_NAME, 'h3', remark='All search results')
    search_result1 = Element(By.XPATH, '(//h3)[1]', remark='First search result')
    
    # Dynamic element: Rarely used, typically determined during test case execution.
    # Must use @dynamic to enable the descriptor's functionality.
    @dynamic
    def search_result(self, order: int = 1):
        return Element(By.XPATH, f'(//h3)[{order}]', remark=f'Search result no.{order}')
    
    # For dynamic elements as properties, use the following format:
    @property
    @dynamic
    def keyword_results(self):
        return Elements(By.XPATH, f'//*[contains(text(), "{Keyword.text1}")]')
    
    # To record dynamic elements statically, use standard data descriptor dynamic assignment:
    # 1. Create a data descriptor object (e.g., static_element).
    static_element = Element()
    
    # 2. Define a function and call "dynamic" to assign a value to "static_element".
    # The logic for dynamic parameters is the same as in Element.
    # After calling "dynamic_element", you can also use "static_element" to operate it.
    def dynamic_element(self, par):
        return self.static_element.dynamic(By.XPATH, f'//*[contains(text(), "{par}")]')
    
    # 3. Use the standard method for a data descriptor.
    def dynamic_element(self, par):
        self.static_element = Element(By.XPATH, f'//*[contains(text(), "{par}")]')
        return self.static_element
```

2. After constructing the Page object, you can begin writing test cases.
```python
# test_my_page.py


from selenium import webdriver
from my_page import MyPage


class TestMyPage:
    
    driver = webdriver.Chrome()

    # Set up a page object. All actions will be triggered from this object.
    my_page = MyPage(driver)

    # The Page object can also call driver-related methods.
    my_page.get("https://google.com")

    # Example of a wait usage:
    # Wait until an element is visible, then take a screenshot.
    my_page.search_field.wait_visible()
    my_page.save_screenshot("my/file/image1.png")

    # All actions automatically handle explicit waits.
    # No need to manually call wait methods unless required, 
    # e.g. Equivalent to: 
    # my_page.search_field.wait_clickable().send_keys(keyword).wait_clickable().submit()
    my_page.search_field.send_keys(keyword).submit()

    # Various wait states are available.
    my_page.loading_image.wait_absent()
    my_page.search_results.wait_all_visible()
    my_page.save_screenshot("my/file/image2.png")

    # Assertions can be made directly:
    search_keyword = 'dinner'
    assert my_page.keyword_results(search_keyword).quantity > 1
    assert search_keyword in my_page.search_result1.text

    # Reuse found elements through existing sessions:
    # Once an element (e.g., `my_page.search_result1`) is located, 
    # it will use the same session unless the element becomes stale.
    # No need to store the found element in a separate variable.
    # Just perform actions directly:
    my_page.search_result1.click()
    ...

    driver.close()
```
---

## Timeout Global Settings
1.	In addition to setting timeouts for individual elements and methods, 
a global timeout setting is also available. See the example below:
```python
from huskium import Timeout


# Set the default timeout for all Elements.
# The huskium default is 30 seconds. You can change it as needed:
Timeout.DEFAULT = 60

# If you don’t want any waiting, you can also set it to 0:
Timeout.DEFAULT = 0

# Set the reraise behavior for timeouts on all Elements.
# The huskium default is True, with the following logic:
# True: Raise a TimeoutException if the element times out.
# False: Return False if the element times out, without raising a TimeoutException.
Timeout.RERAISE = False
```

2.	The priority order for timeout values is as follows:
- P1: Method-Level:
    - `page.element.wait_method(timeout=20)`
- P2: Element-Level:
    - `element = Element(..., timeout=10, ...)`
- P3: Global-Level:
    - `Timeout.DEFAULT = 60`

3.	The priority order for timeout reraise behavior is as follows:
- P1: Method-Level:
    - `page.element.wait_method(reraise=True)`
- P2: Global-Level:
    - `Timeout.RERAISE = False`
---

## Cache Global Settings
1. Cache determines whether the `Element` class should reference a previously located `WebElement` 
for actions or locate the element again for each action.  
2. The benefits of Cache are evident when the same `Element` is accessed multiple times, 
such as performing `.text` followed by `.click()`.
3. Note that `Elements` does not support cache. 
For multiple elements, the state can be highly unstable, 
so each action must locate the elements again to ensure expected behavior.  
```python
from huskium import Cache


# Set the default cache for all Element.
# The default is True. You can change it as needed:
Cache.ELEMENT = False


# You can also configure the cache for an individual Element:
element = Element(..., cache=False)
```

4.	The priority order for cache value is as follows:
- P1: Element-Level:
    - `element = Element(..., cache=False)`
- P2: Global-Level:
    - `Cache.ELEMENT = False`
---

## Wait Actions
We offer a comprehensive set of wait methods, 
extending the official expected_conditions in `ec_extension.py` 
and encapsulating them into corresponding methods. 
Below are the extended methods for Element(s):
```python
# Element
page.element.wait_present()
page.element.wait_absent()
page.element.wait_visible()
page.element.wait_invisible()
page.element.wait_clickable()
page.element.wait_unclickable()
page.element.wait_selected()
page.element.wait_unselected()

# Elements
page.elements.wait_all_present()
page.elements.wait_all_absent()
page.elements.wait_all_visible()
page.elements.wait_any_visible()

# You can set default timeout and reraise behavior for all wait functions.
page.element.wait_visible(timeout=10, reraise=True)
# Recommended to use default settings (timeout=30, reraise=True) for simplicity.
page.element.wait_visible()

# For reverse conditions like invisible and unclickable, 
# use the "present" parameter to define if existence is required.
# Element must be present and invisible (default).
page.element.wait_invisible(present=True)
# Element can be absent or [present and invisible].
page.element.wait_invisible(present=False)
# Element must be present and unclickable (default).
page.element.wait_unclickable(present=True)
# Element can be absent or [present and unclickable].
page.element.wait_unclickable(present=False)

# Selection states are tied to user actions, 
# so the element must be present; no "present" parameter is provided.
page.element.wait_selected()
page.element.wait_unselected()
```
---

## Appium Extended Actions
We have extended Appium with highly convenient action features, including:
```python
# Offset allows you to define swipe directions. 
# It supports eight standard directions: 
# UP, DOWN, LEFT, RIGHT, UPPER_LEFT, UPPER_RIGHT, LOWER_LEFT, LOWER_RIGHT.
# Area lets you define the swipeable range, 
# defaulting to the full device screen (FULL), or you can customize it.

from huskium import Offset, Area

# Page swiping. Refer to function docstrings for details.
page.swipe_by(Offset.UP, Area.FULL)
page.swipe_by(Offset.DOWN)
page.swipe_by(Offset.LEFT)
page.swipe_by(Offset.RIGHT)
page.swipe_by(Offset.UPPER_LEFT)
page.swipe_by(Offset.UPPER_RIGHT)
page.swipe_by(Offset.LOWER_LEFT)
page.swipe_by(Offset.LOWER_RIGHT)

# Page flicking. Refer to function docstrings for details.
# All Offset directions are supported.
page.flick_by(Offset.UP, Area.FULL)

# Element swiping until an element is visible.
# All Offset directions are supported.
page.element.swipe_by(Offset.UP, Area.FULL)

# Element flicking until an element is visible.
# All Offset directions are supported.
page.element.flick_by(Offset.UP, Area.FULL)

# Page draw lines.
# Define dots coordinates
dots = [{"x": x1, "y": y1}, {"x": x2, "y": y2}, {"x": x3, "y": y3}, ...]
# Alternatively, use element locations if available
dots = page.elements.locations
page.draw_lines(dots)

# Page draw gesture.
# 9-grid coordinates, or define your own
dots = page.elements.locations  
# 9-grid gesture string (1–9 represent grid positions). This example draws a reverse Z.
gesture = "9875321"  
page.draw_gesture(dots, gesture)
```
---

## Other Actions
All Selenium and Appium features are included. Here are some examples:
```python
# ActionChains
page.element.scroll_to_element().perform()
page.element.move_to_element().drag_and_drop().perform()

# Temporarily store ActionChains and execute later
page.element.move_to_element().drag_and_drop()
...  # Process other logic before executing perform()
page.element.perform()

# Select options
page.element.options
page.element.select_by_value()
```
---

## Logstack
Using logstack to log specific frame information.
The logstack module extends logging functionality, 
allowing you to capture information for specific frames, 
such as those starting with a designated prefix (e.g., test), 
without tracing all frames manually.
```python
from huskium import logstack

# Configure logging using either logging.basicConfig() or logstack.config().
# logstack.config() simplifies the default settings. You can use it as shown below
# to output the log file to "./log.log".
logstack.config()

# Use logstack in your code to log specific frames
def some_func():
    ...
    # Logs information from the first frame with the prefix (default: test)
    logstack.info("Log from some function.", prefix="test")

def test_func():
    ...
    # Logs frame info for test_func, not some_func
    some_func()

# Example log output:
# 2025-01-04 18:20:48 | INFO | testing.py:32 | test_func | Log from some function.
```

## Inheritance
You can also extend the Page and Element classes to include custom methods. 
There’s no need to manually handle descriptors, and the inheritance usage remains unchanged.
```python
from huskium import Page as HuskyPage
from huskium import Element as HuskyElement


class Page(HuskyPage):

    def extended_func(self, par):
        ...


class Element(HuskyElement):

    def extended_func(self, par):
        ...
```
---

## TODO
Keep tracking the Appium version.  
