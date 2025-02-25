# huskium

## Table of Contents
- [Overview](#overview)
- [Usage](#usage)
- [Page Object Example Code](#page-object-example-code)
- [Timeout Settings](#timeout-settings)
- [Cache Settings](#cache-settings)
- [Log Settings](#log-settings)
- [Wait Actions](#wait-actions)
- [Appium Extended Actions](#appium-extended-actions)
- [Action Chains](#action-chains)
- [Select Actions](#select-actions)
- [Inheritance](#inheritance)
- [TODO](#todo)

---

## Copyright
### Developer: Johnny Chou

---

## Overview
- **huskium** is a Page Object framework built on Selenium and Appium.
- It leverages Python’s data descriptors to simplify and enhance UI automation.
- Currently tracking Appium v4.5.0 (released on 2025/01/22).
- Sphinx: https://uujohnnyuu.github.io/huskium/

---

## Usage
- **Build page objects** simply and elegantly using the `Page` and `Element(s)` classes.
- **Write test scripts** easily with the constructed Page objects.

---

## Page Object Example Code

### 1. Page Object
```python
# my_page.py

from huskium import Page, Element, Elements, By, dynamic

class MyPage(Page):

    # Static element: the standard way to define element.
    search_field = Element(By.NAME, 'q', remark='Search input box')
    search_results = Elements(By.TAG_NAME, 'h3', remark='All search results')
    search_result1 = Element(By.XPATH, '(//h3)[1]', remark='First search result')

    # Dynamic element: mainly used when element attributes are determined at runtime.
    @dynamic
    def search_result(self, order: int = 1):
        return Element(By.XPATH, f'(//h3)[{order}]', remark=f'Search result no.{order}')
```

### 2. Test Case
```python
# test_my_page.py

from selenium import webdriver
from my_page import MyPage

driver = webdriver.Chrome()
my_page = MyPage(driver)

my_page.get("https://google.com")

# Perform actions with automatic explicit waits.
my_page.search_field.send_keys("Selenium").submit()
my_page.search_results.wait_all_visible()
my_page.save_screenshot("screenshot.png")

assert "Selenium" in my_page.search_result1.text
my_page.search_result1.click()

driver.close()
```

### 3. Advanced Dynamic Element
```python
from huskium import Page, Element, By

class MyPage(Page):
    
    # Set a static element first. 
    static_search_result = Element()  

    # Method 1: Call `dynamic` to set `static_search_result`.
    def dynamic_search_result(self, order: int = 1):
        return self.static_search_result.dynamic(By.XPATH, f'(//h3)[{order}]', remark=f'NO.{order}')

    # Method 2: Use the data descriptor mechanism.
    def dynamic_search_result(self, order: int = 1):
        self.static_search_result = Element(By.XPATH, f'(//h3)[{order}]', remark=f'NO.{order}')
        return self.static_search_result
```

---

## Timeout Settings

### 1. Global Configuration
```python
from huskium import Timeout

# Default timeout for all Elements.
Timeout.DEFAULT = 30

# True: Raising TiemoutException if the process timed out.
# False: Return False if the process timed out.
Timeout.RERAISE = True
```

### 2. Priority
- **P1**: Method-Level (`page.element.wait_method(timeout=20)`)
- **P2**: Element-Level (`Element(..., timeout=10, ...)`)
- **P3**: Global-Level (`Timeout.DEFAULT = 60`)

---

## Cache Settings

### 1. Global Configuration
Caches the WebElement for each `Element` to improve performance.
Note that `Elements` does not support caching, as multiple elements are highly unstable.
```python
from huskium import Cache

# True: Caches the WebElement for each Element to improve performance.
# False: Does not cache the WebElement, re-locating the element for each operation.
Cache.ELEMENT = True
```

### 2. Priority
- **P1**: Element-Level (`Element(..., cache=False)`)
- **P2**: Global-Level (`Cache.ELEMENT = False`)

---

## Log Settings

### 1. Dubug Log Configuration
```python
from huskium import Log

# Capture log messages from frames where the name starts with 'test'.
# Set to None to disable filtering.
Log.PREFIX_FILTER.prefix = 'test'  

# Specify whether to filter logs by function name.
# If False, filtering is based on file (module) name instead.
Log.PREFIX_FILTER.funcframe = True

# Set to True for case-insensitive filtering.
Log.PREFIX_FILTER.lower = True
```

### 2. Debug Log Display Example
```log
# When Log.PREFIX_FILTER.prefix = None, logging behaves normally, 
# showing the first frame (stacklevel = 1).
2025-02-11 11:13:08 | DEBUG | element.py:574 | wait_clickable | Element(logout_button): Some message.

# When Log.PREFIX_FILTER.prefix = 'test', 
# logs display the first frame with a name starting with 'test' (stacklevel >= 1).
# This helps quickly trace the module and line where the issue occurs.
2025-02-11 11:13:22 | DEBUG | test_game.py:64 | test_game_flow | Element(logout_button): Some message.
```

### 3. Customize Log Filter
You can also apply the provided filters to your own logging as follows:
```python
from huskium import PrefixFilter, FuncPrefixFilter, FilePrefixFilter

# PrefixFilter includes both FuncPrefixFilter and FilePrefixFilter.
prefix_filter = PrefixFilter('test')
logging.getLogger().addFilter(prefix_filter)

# You can update the filter dynamically by accessing the attribute.
prefix_filter.prefix = 'others'
prefix_filter.funcframe = False
prefix_filter.lower = False

# If you only want to display module frames, directly use `FilePrefixFilter`.
run_module_filter = FilePrefixFilter('run')
logging.getLogger().addFilter(run_module_filter)

# If you only want to display func frames, directly use `FuncPrefixFilter`.
test_func_filter = FuncPrefixFilter('test')
logging.getLogger().addFilter(test_func_filter)
```
---

## Wait Actions

### 1. Basic Element Status
```python
# Single Element
page.element.wait_present()
page.element.wait_absent()
page.element.wait_visible()
page.element.wait_invisible()
page.element.wait_clickable()
page.element.wait_unclickable()
page.element.wait_selected()
page.element.wait_unselected()

# Multiple Elements
page.elements.wait_all_present()
page.elements.wait_all_absent()
page.elements.wait_all_visible()
page.elements.wait_any_visible()
```

### 2. Reverse Element States with Presence Check
```python
# For invisible and unclickable elements, absence is allowed by setting present=False:
page.element.wait_invisible(present=False)  # Can be either absent or invisible
page.element.wait_unclickable(present=False)  # Can be either absent or unclickable
```

---

## Appium Extended Actions

### Appium 2.0+ Usage
```python
from huskium import Offset, Area

# Page swipe or flick.
page.swipe_by()  # Default Offset.UP, Area.FULL
page.flick_by()  # Default Offset.UP, Area.FULL
page.swipe_by(Offset.UPPER_RUGHT, Area.FULL)
page.flick_by(Offset.LOWER_LEFT)

# Element swipe or flick until visible.
page.element.swipe_by()  # Default Offset.UP, Area.FULL
page.element.flick_by()  # Default Offset.UP, Area.FULL
page.element.swipe_by(Offset.UPPER_RUGHT)
page.element.flick_by(Offset.LOWER_LEFT, Area.FULL)

# Drawing gestures (e.g., "9875321" for reverse Z)
dots = page.elements.locations
page.draw_gesture(dots, "9875321")

# Drawing any lines between dots
dots = page.elements.locations
page.draw_lines(dots)
```

---

## Action Chains
```python
page.element.move_to_element().drag_and_drop().perform()
page.scroll_from_origin().double_click().perform()

# or
page.element.move_to_element().drag_and_drop()
page.scroll_from_origin().double_click()
...  # do something
page.perform()  # perform all actions
```

---

## Select Actions
```python
page.element.options
page.element.select_by_value("option_value")
```

---

## Inheritance

```python
from huskium import Page as HuskyPage, Element as HuskyElement

class Page(HuskyPage):
    def extended_func(self, par):
        ...

class Element(HuskyElement):
    def extended_func(self, par):
        ...
```

---

## TODO
- Keep tracking Appium version updates.
