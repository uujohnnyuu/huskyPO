# huskium

## Table of Contents
1. [Overview](#overview)
2. [Usage](#usage)
3. [Page Object Example Code](#page-object-example-code)
4. [Timeout Global Settings](#timeout-global-settings)
5. [Cache Global Settings](#cache-global-settings)
6. [Wait Actions](#wait-actions)
7. [Appium Extended Actions](#appium-extended-actions)
8. [Other Actions](#other-actions)
9. [Logstack](#logstack)
10. [Inheritance](#inheritance)
11. [TODO](#todo)

---

## Copyright
- Developer: Johnny Chou

---

## Overview
- **huskium** is a Page Object framework built on Selenium and Appium.
- It leverages Python’s data descriptors to simplify and enhance UI automation.

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

---

## Timeout Global Settings

1️⃣ **Global Timeout Configuration**
```python
from huskium import Timeout

Timeout.DEFAULT = 60  # Default timeout for all Elements (default is 30s)
Timeout.RERAISE = False  # Prevent raising exceptions on timeouts
```

2️⃣ **Priority Order for Timeout Values**
- **P1**: Method-Level (`page.element.wait_method(timeout=20)`)
- **P2**: Element-Level (`Element(..., timeout=10, ...)`)
- **P3**: Global-Level (`Timeout.DEFAULT = 60`)

---

## Cache Global Settings

1️⃣ **Enable/Disable Cache**
```python
from huskium import Cache

Cache.ELEMENT = False  # Disable caching globally
element = Element(..., cache=False)  # Disable caching for a specific element
```

2️⃣ **Cache Priority Order**
- **P1**: Element-Level (`Element(..., cache=False)`)
- **P2**: Global-Level (`Cache.ELEMENT = False`)

---

## Wait Actions

Below are the extended wait methods available:

```python
# Single Element
page.element.wait_visible()
page.element.wait_clickable()
page.element.wait_selected()

# Multiple Elements
page.elements.wait_all_visible()
page.elements.wait_any_visible()
```

🔹 **Reverse conditions**:  
```python
page.element.wait_invisible(present=False)  # Can be absent or invisible
page.element.wait_unclickable(present=False)
```

---

## Appium Extended Actions

🚀 **Enhanced Appium Actions**
```python
from huskium import Offset, Area

# Page swipe
page.swipe_by(Offset.UP, Area.FULL)

# Element flick until visible
page.element.flick_by(Offset.UP, Area.FULL)

# Drawing gestures (e.g., "9875321" for reverse Z)
dots = page.elements.locations
page.draw_gesture(dots, "9875321")
```

---

## Other Actions

```python
# ActionChains
page.element.move_to_element().drag_and_drop().perform()

# Select options
page.element.select_by_value("option_value")
```

---

## Logstack

🔹 **Custom Logging for Specific Frames**
```python
from huskium import logstack

logstack.config()  # Configure logging

logstack.info("Logging from function.", prefix="test")
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
