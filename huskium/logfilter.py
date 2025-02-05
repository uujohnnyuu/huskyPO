import inspect
import logging
import os
import time

from .config import Log


class PrefixFilter(logging.Filter):

    def filter(self, record):
        # Avoid inspect.stack(0), as it is costly.
        frame = inspect.currentframe()
        while frame:
            funcname = frame.f_code.co_name
            if funcname.startswith(Log.PREFIX):
                record.funcName = funcname
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


def non_test_func():
    has_filter_func()


no_filter_func()
no_filter_func()
has_filter_func()
has_filter_func()
test_func()
non_test_func()
