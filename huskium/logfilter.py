import logging
import inspect
import os


class TestFunctionFilter(logging.Filter):
    def filter(self, record):
        for frame_record in inspect.stack():
            func_name = frame_record.function
            if func_name.startswith("test"):
                record.funcName = func_name
                record.filename = os.path.basename(frame_record.filename)
                record.lineno = frame_record.lineno
                return True  # Success finding test frame.
        return True  # If not, keep origin.


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
)

logger = logging.getLogger()
logger.addFilter(TestFunctionFilter())


def some_func():
    logging.info("這是一條來自 some_func() 的 log")


def test_func():
    some_func()  # It should show test frame here, not some_func.


test_func()
