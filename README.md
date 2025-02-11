# huskium

## Table of Contents
1. [Overview](#overview)
2. [Usage](#usage)
3. [Page Object Example Code](#page-object-example-code)
4. [Timeout Global Settings](#timeout-global-settings)
5. [Cache Global Settings](#cache-global-settings)
6. [Log Global Settings](#log-global-settings)
7. [Wait Actions](#wait-actions)
8. [Appium Extended Actions](#appium-extended-actions)
9. [Action Chains](#action-chains)
10. [Select Actions](#select-actions)
11. [Inheritance](#inheritance)
12. [TODO](#todo)

---

## Copyright
- Developer: Johnny Chou

---

## Overview
- **huskium** is a Page Object framework built on Selenium and Appium.
- It leverages Python’s data descriptors to simplify and enhance UI automation.
- Currently tracking Appium v4.5.0 (released on 2025/01/22).

---

## Usage
- **Build page objects** simply and elegantly using the `Page` and `Element(s)` classes.
- **Write test scripts** easily with the constructed Page objects.

---

## Page Object Example Code

### 1️⃣ Constructing a Page Object
Create a Page object in a separate Python file:

```python
# my_page.py

from huskium import Page, Element, Elements, By, dynamic

class MyPage(Page):
    # Static element definition
    search_field = Element(By.NAME, 'q', remark='Search input box')
    search_results = Elements(By.TAG_NAME, 'h3', remark='All search results')
    search_result1 = Element(By.XPATH, '(//h3)[1]', remark='First search result')

    # Dynamic element example
    @dynamic
    def search_result(self, order: int = 1):
        return Element(By.XPATH, f'(//h3)[{order}]', remark=f'Search result no.{order}')
```

### 2️⃣ Writing Test Cases

```python
# test_my_page.py

from selenium import webdriver
from my_page import MyPage

driver = webdriver.Chrome()
my_page = MyPage(driver)

my_page.get("https://google.com")

# Perform actions with automatic explicit waits
my_page.search_field.send_keys("Selenium").submit()
my_page.search_results.wait_all_visible()
my_page.save_screenshot("screenshot.png")

assert "Selenium" in my_page.search_result1.text
my_page.search_result1.click()

driver.close()
```

### 3️⃣ Advanced Dynamic Element
```python
from huskium import Page, Element, By

class MyPage(Page):
    
    # Set a static element first. 
    static_search_result = Element()  

    # Method 1: Call `dynamic` to set `static_search_result`.
    def dynamic_search_result(self, order: int = 1):
        return self.static_search_result.dynamic(By.XPATH, f'(//h3)[{order}]', remark=f'Search NO.{order}')

    # Method 2: Use the data descriptor mechanism.
    def dynamic_search_result(self, order: int = 1):
        self.static_search_result = Element(By.XPATH, f'(//h3)[{order}]', remark=f'Search NO.{order}')
        return self.static_search_result
```

---

## Timeout Global Settings

### 1️⃣ Global Timeout Configuration
```python
from huskium import Timeout

Timeout.DEFAULT = 60  # Default timeout for all Elements (default is 30s)
Timeout.RERAISE = False  # Prevent raising exceptions on timeouts
```

### 2️⃣ Priority Order for Timeout Values
- **P1**: Method-Level (`page.element.wait_method(timeout=20)`)
- **P2**: Element-Level (`Element(..., timeout=10, ...)`)
- **P3**: Global-Level (`Timeout.DEFAULT = 60`)

---

## Cache Global Settings

### 1️⃣ Enable/Disable Cache
```python
from huskium import Cache

Cache.ELEMENT = False  # Disable caching globally
element = Element(..., cache=False)  # Disable caching for a specific element
```

### 2️⃣ Cache Priority Order
- **P1**: Element-Level (`Element(..., cache=False)`)
- **P2**: Global-Level (`Cache.ELEMENT = False`)

---

## Log Global Settings

### 1️⃣ Inner Debug Log
```python
from huskium import Log

# Capture log messages from frames where the name starts with 'test'.
# Set to None to disable filtering.
Log.PREFIX = 'test'  

# Specify whether to filter logs by function name.
# If False, filtering is based on filename (module) instead.
Log.FUNCFRAME: bool = True

# Set to True for case-insensitive filtering.
Log.LOWER: bool = True
```

### 2️⃣ Log Filter
```python
from huskium import PrefixFilter, FuncnamePrefixFilter, FilenamePrefixFilter

# Apply a filter to customize logging.
# PrefixFilter includes both FuncnamePrefixFilter and FilenamePrefixFilter.
# If Log.FUNCNAME = True, FuncnamePrefixFilter is used; otherwise, FilenamePrefixFilter is applied.
logging.getLogger().addFilter(PrefixFilter())

# Use specific filters independently if needed, regardless of Log.FUNCNAME.
logging.getLogger().addFilter(FilenamePrefixFilter())

# It is recommended to configure logging per module.
# Huskium’s core modules already define LOGGER, so Log settings control behavior externally.
LOGGER = logging.getLogger(__name__)
FILTER = FuncnamePrefixFilter()
LOGGER.addFilter(FILTER)
```

### 3️⃣ Log Display Example
```log
# When Log.PREFIX = None, logging behaves normally, showing the first frame (stacklevel = 1).
2025-02-11 11:13:08 | DEBUG | element.py:574 | wait_clickable | Element(logout_button): Some message.

# When Log.PREFIX = 'test', logs display the first frame with a name starting with 'test' (stacklevel >= 1).
# This helps quickly trace the module and line where the issue occurs.
2025-02-11 11:13:22 | DEBUG | test_game.py:64 | test_game_flow | Element(logout_button): Some message.
```

---

## Wait Actions

### 1️⃣ Basic Element Status

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

### 2️⃣ Reverse Element States with Presence Check
```python
# For invisible and unclickable elements, absence is allowed by setting present=False:
page.element.wait_invisible(present=False)  # Can be either absent or invisible
page.element.wait_unclickable(present=False)  # Can be either absent or unclickable
```

---

## Appium Extended Actions

### Enhanced Appium Actions (Appium 2.0+)
```python
from huskium import Offset, Area

# Page swipe
page.swipe_by(Offset.UP, Area.FULL)

# Element flick until visible
page.element.flick_by(Offset.UP, Area.FULL)

# Drawing gestures (e.g., "9875321" for reverse Z)
dots = page.elements.locations
page.draw_gesture(dots, "9875321")

# Drawing any lines between dots
dots = page.elements.locations
page.draw_lines(dots)
```

---

### Action Chains

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

### Select Actions

```python
page.element.options
page.element.select_by_value("option_value")
```

---

## Inheritance

🔹 **Extending Page and Element Classes**
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
