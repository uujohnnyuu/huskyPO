import logging
import inspect
import os
import time


class TestFunctionFilter(logging.Filter):
    def filter(self, record):
        # Iterate through the current stack to find a function starting with `test_`
        for frame_record in inspect.stack(0):
            func_name = frame_record.function
            if func_name.startswith("test_"):
                record.funcName = func_name
                record.filename = os.path.basename(frame_record.filename)
                record.lineno = frame_record.lineno
                return True  # Successfully found a `test_` function, modify the log information
        return True  # If no `test_` function is found, keep the original logging behavior


class TestFunctionFilter2(logging.Filter):
    def filter(self, record):
        # Get the current frame
        frame = inspect.currentframe()
        while frame:
            func_name = frame.f_code.co_name  # Retrieve function name
            if func_name.startswith("test_"):  # Check if the function name starts with `test_`
                record.funcName = func_name
                record.filename = os.path.basename(frame.f_code.co_filename)
                record.lineno = frame.f_lineno
                return True  # Found a `test_` function, modify the log information and return
            frame = frame.f_back  # Move to the previous frame
        return True  # If no `test_` function is found, keep the original logging behavior


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
)


logger = logging.getLogger()
logger.addFilter(TestFunctionFilter())

logger2 = logging.getLogger()
logger2.addFilter(TestFunctionFilter2())


def some_func():
    start = time.time()
    logging.info("log from some_func()")
    end = time.time()
    consume = (end - start) * 1000
    logger.info(f"consume: {consume}")


def some_func2():
    start = time.time()
    logging.info("log from some_func2()")
    end = time.time()
    consume = (end - start) * 1000
    logger2.info(f"consume: {consume}")


def test_func():
    some_func()


def test_func2():
    some_func2()


test_func2()
test_func()
test_func2()
test_func()
test_func2()
