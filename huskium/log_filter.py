# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


import inspect
import logging
import os

from .config import Log


class PrefixFilter(logging.Filter):
    """
    A prefix filter for logging.
    Displaying log information for frame where the name starts with Log.PREFIX.

    Usage::

        import logging

        from huskium import Log
        from huskium import PrefixFilter, FuncPrefixFilter, FilePrefixFilter

        # Apply a filter to customize logging.
        # PrefixFilter includes both FuncPrefixFilter and FilePrefixFilter.
        # If Log.FUNCNAME = True, FuncPrefixFilter is used; otherwise, FilePrefixFilter is applied.
        logging.getLogger().addFilter(PrefixFilter())

        # Use specific filters independently if needed, regardless of Log.FUNCNAME.
        logging.getLogger().addFilter(FilePrefixFilter())

        # It is recommended to configure logging per module for your structure.
        # Huskium’s core modules already define LOGGER, so Log settings control behavior externally.
        LOGGER = logging.getLogger(__name__)
        PREFIX_FILTER = PrefixFilter()
        LOGGER.addFilter(PREFIX_FILTER)

    """

    def __init__(self):
        super().__init__()
        self._funcfilter = FuncPrefixFilter()
        self._filefilter = FilePrefixFilter()

    def filter(self, record):
        if Log.FUNCFRAME:
            return self._funcfilter.filter(record)
        return self._filefilter.filter(record)


class FuncPrefixFilter(logging.Filter):

    def filter(self, record):
        if Log.PREFIX:
            prefix = Log.PREFIX.lower() if Log.LOWER else Log.PREFIX
            # Do not use inspect.stack(), not even inspect.stack(0), as both are costly.
            frame = inspect.currentframe()
            while frame:
                funcname = original_funcname = frame.f_code.co_name
                if Log.LOWER:
                    funcname = funcname.lower()
                if funcname.startswith(prefix):
                    record.filename = os.path.basename(frame.f_code.co_filename)
                    record.lineno = frame.f_lineno
                    record.funcName = original_funcname
                    return True
                frame = frame.f_back
        return True


class FilePrefixFilter(logging.Filter):

    def filter(self, record):
        if Log.PREFIX:
            prefix = Log.PREFIX.lower() if Log.LOWER else Log.PREFIX
            # Do not use inspect.stack(), not even inspect.stack(0), as both are costly.
            frame = inspect.currentframe()
            while frame:
                filename = original_filename = os.path.basename(frame.f_code.co_filename)
                if Log.LOWER:
                    filename = filename.lower()
                if filename.startswith(prefix):
                    record.filename = original_filename
                    record.lineno = frame.f_lineno
                    record.funcName = frame.f_code.co_name
                    return True
                frame = frame.f_back
        return True
