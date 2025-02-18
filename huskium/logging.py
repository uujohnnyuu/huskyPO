# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


import inspect
import logging
import os


# Filter
class PrefixFilter(logging.Filter):
    """
    A prefix filter for logging.  
    Displays log information for frames where the name starts with the target prefix.

    Usage::

        import logging
        from huskium import PrefixFilter

        # Create a filter object with prefix = 'test'
        filter = PrefixFilter('test')

        # Set up logging
        logging.addFilter(filter)

        # All logging will follow the filter logic, recording logs from frames with the prefix 'test'.
        logging.info(...)

    """

    def __init__(self, prefix: str | None = None, lower: bool = True, funcframe: bool = True):
        """
        Args:
            prefix: The frame prefix.
	        lower: True for case-insensitive matching; False for case-sensitive.
	        funcframe: True to filter function frames; False to filter file (module) frames.
        """
        super().__init__()
        self.prefix = prefix
        self.lower = lower
        self.funcframe = funcframe
        self._func = FuncPrefixFilter()
        self._file = FilePrefixFilter()

    def filter(self, record):
        f = self._func if self.funcframe else self._file
        f.prefix = self.prefix
        f.lower = self.lower
        return f.filter(record)


class FuncPrefixFilter(logging.Filter):

    def __init__(self, prefix: str | None = None, lower: bool = True):
        super().__init__()
        self.prefix = prefix
        self.lower = lower

    def filter(self, record):
        if self.prefix:
            prefix = self.prefix.lower() if self.lower else self.prefix
            # Do not use inspect.stack(), not even inspect.stack(0), as both are costly.
            frame = inspect.currentframe()
            while frame:
                funcname = original_funcname = frame.f_code.co_name
                if self.lower:
                    funcname = funcname.lower()
                if funcname.startswith(prefix):
                    record.filename = os.path.basename(frame.f_code.co_filename)
                    record.lineno = frame.f_lineno
                    record.funcName = original_funcname
                    return True
                frame = frame.f_back
        return True


class FilePrefixFilter(logging.Filter):

    def __init__(self, prefix: str | None = None, lower: bool = True):
        super().__init__()
        self.prefix = prefix
        self.lower = lower

    def filter(self, record):
        if self.prefix:
            prefix = self.prefix.lower() if self.lower else self.prefix
            # Do not use inspect.stack(), not even inspect.stack(0), as both are costly.
            frame = inspect.currentframe()
            while frame:
                filename = original_filename = os.path.basename(frame.f_code.co_filename)
                if self.lower:
                    filename = filename.lower()
                if filename.startswith(prefix):
                    record.filename = original_filename
                    record.lineno = frame.f_lineno
                    record.funcName = frame.f_code.co_name
                    return True
                frame = frame.f_back
        return True


# Adapter
class PageElementLoggerAdapter(logging.LoggerAdapter):

    def __init__(self, logger, petype, remark):
        super().__init__(logger, {"petype": petype, "remark": remark})

    def process(self, msg, kwargs):
        return f'{self.extra["petype"]}({self.extra["remark"]}): {msg}', kwargs
