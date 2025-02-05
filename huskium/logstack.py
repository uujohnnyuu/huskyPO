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
from typing import Mapping

from .config import Log


def config(
    filename: str | None = './log.log',
    *,
    filemode='w',
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    style='%',
    level=logging.INFO,
    stream=None,
    handlers=None,
    force=None,
    encoding=None,
    errors=None
) -> None:
    """
    Simply set `logging.basicConfig()`.

    Usage::

        from huskium import logstack
        logstack.config('./xxx.log')

    """
    if isinstance(filename, (str, type(None))):
        outputkv = {"filename": filename}
        if filename is not None:
            abspath = os.path.abspath(filename)
            dirname = os.path.dirname(abspath)
            os.makedirs(dirname, exist_ok=True)
    if stream:
        outputkv = {"stream": stream}
    if handlers:
        outputkv = {"handlers": handlers}
    logging.basicConfig(
        **outputkv,  # type: ignore[arg-type]
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
    *,
    prefix: str | None = None,
    lower: bool = True,
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
            - If prefix is None, it will use `Log.PREFIX`.
                If both are None, it behaves the same as standard logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    logging.debug(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=get_stacklevel(prefix, lower, stacklevel),
        extra=extra
    )


def info(
    message: str,
    *,
    prefix: str | None = None,
    lower: bool = True,
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
            - If prefix is None, it will use `Log.PREFIX`.
                If both are None, it behaves the same as standard logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    logging.info(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=get_stacklevel(prefix, lower, stacklevel),
        extra=extra
    )


def warning(
    message: str,
    *,
    prefix: str | None = None,
    lower: bool = True,
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
            - If prefix is None, it will use `Log.PREFIX`.
                If both are None, it behaves the same as standard logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    logging.warning(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=get_stacklevel(prefix, lower, stacklevel),
        extra=extra
    )


def error(
    message: str,
    *,
    prefix: str | None = None,
    lower: bool = True,
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
            - If prefix is None, it will use `Log.PREFIX`.
                If both are None, it behaves the same as standard logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    logging.error(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=get_stacklevel(prefix, lower, stacklevel),
        extra=extra
    )


def exception(
    message: str,
    *,
    prefix: str | None = None,
    lower: bool = True,
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
            - If prefix is None, it will use `Log.PREFIX`.
                If both are None, it behaves the same as standard logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    logging.exception(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=get_stacklevel(prefix, lower, stacklevel),
        extra=extra
    )


def critical(
    message: str,
    *,
    prefix: str | None = None,
    lower: bool = True,
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
            - If prefix is None, it will use `Log.PREFIX`.
                If both are None, it behaves the same as standard logging.
        - excinfo: The same as logging `exc_info`.
        - stacklevel: Essentially the same as the logging stacklevel.
            - If a prefix is provided, this parameter specifies
                the stack level from which the search begins.
            - If the prefix is None, it behaves the same as the logging stacklevel.
        - extra: The same as logging `extra`.
    """
    logging.critical(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=get_stacklevel(prefix, lower, stacklevel),
        extra=extra
    )


def get_stacklevel(
    prefix: str | None = None,
    lower: bool = True,
    start: int = 1,
    outer: int = 1
) -> int:
    """
    Finds the stack level whose prefix is.

    Args:
        - prefix: The prefix of the target stack level.
        - lower: If True, the prefix is case-insensitive.
        - start: The stack level to start the search from.
        - outer: The outermost wrapping level of this function used for logging.

    Example of start and outer::

        # Example 1: Using info() for logging, directly calling get_stacklevel().
        def info():
            # start = 1 -> Start searching from info().
            # outer = 1 -> Search from the first wrapper of info(), treating it as logging.
            # stacklevel = start + outer = 2 -> get_stacklevel() starts from the first wrapper of info().
            get_stacklevel()

        # Example 2: Using info() for logging, but wrapped_stacklevel() wraps get_stacklevel().
        def info():
            # stacklevel = start + outer = 1 + 2 = 3
            # stacklevel = 1 -> wrapped_stacklevel().
            # stacklevel = 2 -> info().
            # stacklevel = 3 -> The module/function using info() for logging.
            wrapped_stacklevel()

        def wrapped_stacklevel():
            ...
            # wrapped_stacklevel() wraps get_stacklevel() for additional logic.
            # start = 1 -> Start searching from wrapped_stacklevel().
            # outer = 2 -> Search from the second wrapper, treating info() as logging.
            # stacklevel = start + outer = 3 -> get_stacklevel() starts from the first wrapper of info().
            get_stacklevel()

    """
    # Adjust start to the first frame of the actual logging.
    start += outer

    # Check prefix; if absent, return start directly.
    prefix = prefix or Log.PREFIX
    if prefix is None:
        return start
    if lower:
        prefix = prefix.lower()

    # Get the current frame.
    frame = inspect.currentframe()
    if frame is None:
        raise RuntimeError("Cannot obtain the current frame.")

    # level = 0 represents the current frame.
    level = start
    for _ in range(level):
        frame = frame.f_back
        if frame is None:
            break

    # Return stack level if a module or function matches the prefix.
    while frame:
        funcname = frame.f_code.co_name
        filename = os.path.basename(frame.f_code.co_filename)
        if lower:
            funcname = funcname.lower()
            filename = filename.lower()
        if funcname.startswith(prefix) or filename.startswith(prefix):
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
    frame = inspect.currentframe()
    if frame is None:
        raise RuntimeError("Cannot obtain the current frame.")

    # Navigate to the desired stack level
    for _ in range(start):
        frame = frame.f_back
        if frame is None:
            raise RuntimeError("Reached the top of the stack without finding the desired frame.")

    # Search for a frame that matches the condition
    frame_target = frame
    while frame:
        if (
            frame.f_code.co_name.startswith(prefix) or
            os.path.basename(frame.f_code.co_filename).startswith(prefix)
        ):
            frame_target = frame
            break
        frame = frame.f_back

    # Extract frame information
    filename = os.path.basename(frame_target.f_code.co_filename)
    lineno = str(frame_target.f_lineno)
    funcname = frame_target.f_code.co_name

    # Return the result in the desired format
    if to_dict:
        return {'filename': filename, 'lineno': lineno, 'funcname': funcname}
    return f'|{filename}:{lineno}|{funcname}|'


def _debug(message: str = '') -> None:
    if Log.INNER:
        debug(message, stacklevel=2)


def _info(message: str = '') -> None:
    if Log.INNER:
        info(message, stacklevel=2)


def _warning(message: str = '') -> None:
    if Log.INNER:
        warning(message, stacklevel=2)


def _error(message: str = '') -> None:
    if Log.INNER:
        error(message, stacklevel=2)


def _exception(message: str = '') -> None:
    if Log.INNER:
        exception(message, stacklevel=2)


def _critical(message: str = '') -> None:
    if Log.INNER:
        critical(message, stacklevel=2)
