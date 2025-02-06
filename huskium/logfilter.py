import inspect
import logging
import os
import time

from .config import Log


class PrefixFilter(logging.Filter):

    def filter(self, record):
        # Do not use inspect.stack(), not even inspect.stack(0), as both are costly.
        frame = inspect.currentframe()
        if Log.PREFIX:
            prefix = Log.PREFIX.lower() if Log.LOWER else Log.PREFIX
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


logging.basicConfig(
    filename=None,
    filemode='w',
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG,
)


logger = logging.getLogger()
filter = PrefixFilter()
logger.addFilter(filter)


def has_filter_func():
    start = time.time()
    logger.info("log from has_filter_func()")
    end = time.time()
    consume = (end - start) * 1000
    logger.info(f"consume: {consume}\n")


def no_filter_func():
    start = time.time()
    logging.info("log from no_filter_func()")
    end = time.time()
    consume = (end - start) * 1000
    logging.info(f"consume: {consume}\n")


def test_func():
    has_filter_func()


def Test_func():
    has_filter_func()


def TesT_func():
    has_filter_func()


def non_test_func():
    has_filter_func()


# no_filter_func()
# no_filter_func()
# has_filter_func()
# has_filter_func()
# test_func()
# non_test_func()

test_func()

test_func()

Log.PREFIX = "xxx"
test_func()

Log.PREFIX = None
test_func()

Log.PREFIX = "test"
test_func()

Log.LOWER = False
Test_func()

Log.LOWER = True
Log.PREFIX = "teST"
TesT_func()
