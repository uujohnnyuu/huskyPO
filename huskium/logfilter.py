import inspect
import logging
import os

from .config import Log


class PrefixFilter(logging.Filter):
    """
    A prefix filter for logging,
    used to display log information for function frames where the prefix matches Log.PREFIX.

    Usage::

        import logging
        from huskium import Log, PrefixFilter

        # Whether using "logging" or "logger",
        # a filter object must be created if further operations or removal are needed.
        # If no modifications or removals are required, "PrefixFilter()" can be used directly.
        prefix_filter = PrefixFilter()

        # Example using "logging", filtering frames with names starting with "test".
        # For "logger", the same applies, just create a logger instance first.
        logging.getLogger().addFilter(prefix_filter)
        Log.PREFIX = "test"  # Default. Set to "None" to disable filtering.

        def some_func():
            # The filter applies here, locating frames starting with "test".
            logging.info(...)

        def test_func():
            # Logs from "test_func" are displayed, while "some_func" is filtered out.
            some_func()

        # Case-insensitive by default. To enforce case sensitivity:
        Log.LOWER = False

        def TesT_func():
            # Since case sensitivity is enforced, "TesT" is not recognized,
            # and "some_func" logs are displayed instead.
            some_func()

    """

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
                    record.funcName = original_funcname
                    record.filename = os.path.basename(frame.f_code.co_filename)
                    record.lineno = frame.f_lineno
                    return True
                frame = frame.f_back
        return True
