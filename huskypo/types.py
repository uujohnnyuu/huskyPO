# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO


from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver as SeleniumWebDriver
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from appium.webdriver.webelement import WebElement as AppiumWebElement


WebDriver = SeleniumWebDriver | AppiumWebDriver
WebElement = SeleniumWebElement | AppiumWebElement

WebDriverTuple = (SeleniumWebDriver, AppiumWebDriver)
WebElementTuple = (SeleniumWebElement, AppiumWebElement)
