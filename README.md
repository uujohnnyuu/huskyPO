# huskyPO

## Copyright
- Developer: Johnny Chou

## Overview
- huskyPO stands for husky Page Object, named 'husky' due to the author's fondness.
- Constructed using Python's data descriptors, it's a UI Page Object package.
- Enables developers to build Python Selenium/Appium UI automation scripts more easily and elegantly.

## Features
- Significantly simplifies and beautifully constructs Page objects and test scripts.
- Encapsulates and integrates commonly used methods of Selenium and Appium, with optimizations in certain functions.
- Uses explicit waiting as the core driving mechanism, and extends some official explicit waiting methods.

## Usage
- Build page objects simply and elegantly using the `Page` and `Element(s)` classes.
- Write test scripts simply and elegantly using the constructed Page objects.

## Example Code
1. First, construct a Page object in any Python file, each page recommended to be a separate Page class.
2. For example, in the my_page.py file:

```python
from huskypo import Page, Element, Elements
from huskypo import By
from huskypo import dynamic


class MyPage(Page):
    
    # Static elements, equivalent to the normal setup of page objects.
    # Similar to constructing Python instance objects.
    search_field = Element(By.NAME, 'q', remark='Search input box')
    search_results = Elements(By.TAG_NAME, 'h3', remark='All search results')
    search_result1 = Element(By.XPATH, '//h3[1]', remark='First search result')
    

    # Dynamic elements, suitable for special test scenarios 
    # where element locator info is decided at runtime during the test case.
    # Typically, dynamic elements make up a very small proportion; 
    # if the test environment is robust and stable, 
    # it's advisable to mostly use static elements.
    # Dynamic elements need to be written as instance methods of the Page class, 
    # and must be decorated with @dynamic to function properly.
    @dynamic
    def search_result(self, order: int = 1):
        return Element(By.XPATH, f'//h3[{order}]', remark=f'Search result no.{order}')

    @dynamic
    def keyword_results(self, keyword: str):
        return Elements(By.XPATH, f'//*[contains(text(), "{keyword}")]')


    # If you must set dynamic elements as properties, follow this order:
    @property
    @dynamic
    def keyword_results(self):
        return Elements(By.XPATH, f'//*[contains(text(), "{Keyword.text1}")]')


    # If you want to record information about dynamic elements and reuse it, 
    # it is recommended to revert to the official standard data descriptor dynamic assignment method.

    # 1. You must first create an object of a data descriptor, such as static_element.

    # 2. Create a function corresponding to static_element and assign a value to static_element,
    # This assignment method utilizes the "__set__" method of the data descriptor. 
    # The parameters given is the same as the way of initializing the "Element".

    # 3. When executing the testcase, first call dynamic_element. 
    # If the subsequent elements no longer change, you can directly use static_element for operations.

    static_element = Element()

    def dynamic_element(self, par) -> Element:
        # __set__ will get the tuple and assign it to Element to initialize static_element.
        # The logic of tuple is exactly the same as the method of placing parameters in an Element, 
        # such as (by, value, index, timeout, remark).
        # It also includes other configuration methods mentioned in the Element documentation, 
        # such as (by, value, remark), and so on.
        self.static_element = (By.XPATH, f'//*[contains(text(), "{par}")]', f'This is {par}')  
        return self.static_element

    def dynamic_element(self, par) -> Element:
        # If you want to clearly specify parameter names, you can also use a dictionary.
        self.static_element = {
            'by': By.XPATH, 
            'value': f'//*[contains(text(), "{par}")]', 
            'remark': f'This is {par}'}
        return self.static_element
```

3. After constructing the Page object in my_page.py, you can begin writing test cases.
4. For example, the content of the test_my_page.py file:
```python
from selenium import webdriver
from my_page import MyPage

class TestMyPage:
    
    driver = webdriver.Chrome()
    my_page = MyPage(driver)

    my_page.get("https://google.com")
    my_page.search_field.wait_present()
    my_page.save_screenshot("my/file/path/image.png")

    search_keyword = 'automation'
    my_page.search_field.send_keys(keyword, Keys.ENTER)
    my_page.search_results.wait_any_visible()
    my_page.save_screenshot("my/file/path/image.png")

    assert my_page.keyword_results(search_keyword).quantity > 1
    assert search_keyword in my_page.search_result1.text

    my_page.search_result1.click()
    ...

    driver.close()
```

5. By using the simple examples above, you can see how we can construct Page objects and write scripts intuitively and beautifully with Page, Element(s) classes, and using page.element.method() style.

6. All the element finding processes rely on explicit waiting methods, the core mainly being the official WebDriverWait and expected_conditions, this package extends the commonly used conditions of present, visible, clickable, selected in the Element(s) class and the driver methods and other page-related operations are encapsulated in the Page class.

## TODO
- Continuously monitor new features in Selenium 4.0 / Appium 2.0.
- Keep an eye on potential bugs and performance issues.
- Continue to optimize compatibility with exception handling and type hints.
