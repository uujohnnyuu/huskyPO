# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


from selenium.common.exceptions import StaleElementReferenceException

from .logging import PrefixFilter
from .exception import _ForcedRelocationException


# logging
PREFIX_FILTER = PrefixFilter()

# exception
ELEMENT_REFERENCE_EXCEPTIONS = (_ForcedRelocationException, AttributeError, StaleElementReferenceException)
EXCLUDED_ELEMENT_REFERENCE_EXCEPTIONS = (_ForcedRelocationException, AttributeError)
EXTENDED_IGNORED_EXCEPTIONS = (StaleElementReferenceException,)


# Page, Element, Elements
class _Name:
    _page = '_page'
    _wait_timeout = '_wait_timeout'
    _present_cache = '_present_cache'
    _visible_cache = '_visible_cache'
    _clickable_cache = '_clickable_cache'
    _select_cache = '_select_cache'
    _caches = [_present_cache, _visible_cache, _clickable_cache, _select_cache]
