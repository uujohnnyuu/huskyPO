# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

from .config import Log, Timeout, Appium, Offset, Area
from .page import Page
from .element import Element
from .elements import Elements
from .by import By
from .decorator import dynamic

# TODO deprecate
from .by import SwipeAction as SA
