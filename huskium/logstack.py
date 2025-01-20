# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


"""
This is the logstack module for extending logging functionality,
designed to record frame information with a specified prefix name.
If you want to reference this logstack method to build your own model or extend it,
make sure that `get_stackinfo()` and `get_stacklevel()` are
encapsulated within the same function layer as `logging.method()`.
Otherwise, discrepancies in stack levels may occur.
"""


from __future__ import annotations

import inspect
import logging
import os
from typing import Mapping, TextIO

from .config import Log


_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'
_DATEFMT = '%Y-%m-%d %H:%M:%S'


def config(
    output: str | TextIO | list[logging.Handler] | None = './log.log',
    *,
    filemode: str = 'w',
    format: str = _FORMAT,
    datefmt: str = _DATEFMT,
    style: str = '%',
    level: int = logging.INFO,
    force: bool = False,
    encoding: str | None = None,
    errors: str | None = None
) -> None:
    """
    Simply set `logging.basicConfig()`.

    Usage::

        from huskium import logstack
        logstack.config('./xxx.log')

    """
    if isinstance(output, (str, type(None))):
        outputkv = {"filename": output}
        if output is not None:
            abspath = os.path.abspath(output)
            dirname = os.path.dirname(abspath)
            os.makedirs(dirname, exist_ok=True)
    elif isinstance(output, list):
        outputkv = {"handlers": output}
    else:
        outputkv = {"stream": output}
    logging.basicConfig(
        **outputkv,
        filemode=filemode,
        format=format,
        datefmt=datefmt,
        style=style,
        level=level,
        force=force,
        encoding=encoding,
        errors=errors
    )


def debug(
    message: str,
    prefix: str | None = 'test',
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calls `logging.debug()` method, and finds the stack which prefix is `prefix`.

    Args:
        - message: The same as logging `msg`.
        - prefix: The stack prefix that starts with it.
            - For example, `test` means the log will be displayed
                in the function `test_xxx()` or the module `test_xxx.py`.
            - If prefix is None, it is the same as logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    stacklevel += 1
    targetlevel = get_stacklevel(prefix, stacklevel) if prefix else stacklevel
    logging.debug(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=targetlevel,
        extra=extra
    )


def info(
    message: str,
    prefix: str | None = 'test',
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calls `logging.info()` method, and finds the stack which prefix is `prefix`.

    Args:
        - message: The same as logging `msg`.
        - prefix: The stack prefix that starts with it.
            - For example, `test` means the log will be displayed
                in the function `test_xxx()` or the module `test_xxx.py`.
            - If prefix is None, it is the same as logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    stacklevel += 1
    targetlevel = get_stacklevel(prefix, stacklevel) if prefix else stacklevel
    logging.info(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=targetlevel,
        extra=extra
    )


def warning(
    message: str,
    prefix: str | None = 'test',
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calls `logging.warning()` method, and finds the stack which prefix is `prefix`.

    Args:
        - message: The same as logging `msg`.
        - prefix: The stack prefix that starts with it.
            - For example, `test` means the log will be displayed
                in the function `test_xxx()` or the module `test_xxx.py`.
            - If prefix is None, it is the same as logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    stacklevel += 1
    targetlevel = get_stacklevel(prefix, stacklevel) if prefix else stacklevel
    logging.warning(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=targetlevel,
        extra=extra
    )


def error(
    message: str,
    prefix: str | None = 'test',
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calls `logging.error()` method, and finds the stack which prefix is `prefix`.

    Args:
        - message: The same as logging `msg`.
        - prefix: The stack prefix that starts with it.
            - For example, `test` means the log will be displayed
                in the function `test_xxx()` or the module `test_xxx.py`.
            - If prefix is None, it is the same as logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    stacklevel += 1
    targetlevel = get_stacklevel(prefix, stacklevel) if prefix else stacklevel
    logging.error(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=targetlevel,
        extra=extra
    )


def exception(
    message: str,
    prefix: str | None = 'test',
    excinfo: bool | tuple | None = True,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calls `logging.exception()` method, and finds the stack which prefix is `prefix`.

    Args:
        - message: The same as logging `msg`.
        - prefix: The stack prefix that starts with it.
            - For example, `test` means the log will be displayed
                in the function `test_xxx()` or the module `test_xxx.py`.
            - If prefix is None, it is the same as logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    stacklevel += 1
    targetlevel = get_stacklevel(prefix, stacklevel) if prefix else stacklevel
    logging.exception(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=targetlevel,
        extra=extra
    )


def critical(
    message: str,
    prefix: str | None = 'test',
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calls `logging.critical()` method, and finds the stack which prefix is `prefix`.

    Args:
        - message: The same as logging `msg`.
        - prefix: The stack prefix that starts with it.
            - For example, `test` means the log will be displayed
                in the function `test_xxx()` or the module `test_xxx.py`.
            - If prefix is None, it is the same as logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    stacklevel += 1
    targetlevel = get_stacklevel(prefix, stacklevel) if prefix else stacklevel
    logging.critical(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=targetlevel,
        extra=extra
    )


def get_stacklevel(prefix: str = 'test', start: int = 1) -> int:
    """
    Finds the stack level whose prefix is.

    Args:
        - prefix: The prefix of the target stack level.
        - start: The stack level to start the search from.
    """
    # Get the current frame.
    frame = inspect.currentframe()

    # level = 0 represents the current frame.
    level = start
    for _ in range(level):
        frame = frame.f_back

    # Start searching through the subsequent frames.
    # Once a module or function matches the prefix, return it's stack level.
    while frame:
        if frame.f_code.co_name.startswith(prefix) or \
           os.path.basename(frame.f_code.co_filename).startswith(prefix):
            return level
        frame = frame.f_back
        level += 1

    # If no matches are found, return the start stack level.
    return start


def get_stackinfo(
    prefix: str = 'test',
    start: int = 1,
    to_dict: bool = False
) -> str | dict[str, str]:
    """
    Finding the filename, lineno and funcname which the stack prefix is `prefix`.

    Args:
        - prefix: The prefix of the target stack level.
        - start: The stack level to start the search from.
        - to_dict: Determine the return type.

    Return:
        - to_dict is True: {'filename': 'xxx.py', 'lineno': '19', 'funcname': 'my_func'}
        - to_dict is False: '|xxx.py:19|my_func|'
    """
    # Get the current frame.
    frame = inspect.currentframe()

    # level = 0 represents the current frame.
    for _ in range(start):
        frame = frame.f_back

    # record the current starting frame and search for the one that matches the condition.
    # If no matching frame is found, use the default frame_target.
    frame_target = frame
    while frame:
        if frame.f_code.co_name.startswith(prefix) or \
           os.path.basename(frame.f_code.co_filename).startswith(prefix):
            frame_target = frame
            break
        frame = frame.f_back

    # After obtaining the final frame, return the filename, lineno, and funcname information.
    filename = os.path.basename(frame_target.f_code.co_filename)
    lineno = str(frame_target.f_lineno)
    funcname = frame_target.f_code.co_name

    # Let the user decide the format of the returned content.
    if to_dict:
        return {'filename': filename, 'lineno': lineno, 'funcname': funcname}
    return f'|{filename}:{lineno}|{funcname}|'


def _debug(message: str = '') -> None:
    if Log.RECORD:
        debug(message, stacklevel=2)


def _info(message: str = '') -> None:
    if Log.RECORD:
        info(message, stacklevel=2)


def _warning(message: str = '') -> None:
    if Log.RECORD:
        warning(message, stacklevel=2)


def _error(message: str = '') -> None:
    if Log.RECORD:
        error(message, stacklevel=2)


def _exception(message: str = '') -> None:
    if Log.RECORD:
        exception(message, stacklevel=2)


def _critical(message: str = '') -> None:
    if Log.RECORD:
        critical(message, stacklevel=2)
