# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# If you want to reference this logstack method to construct your own model or extend it,
# you must understand the following points; otherwise, unexpected errors may occur.

# 1. We must ensure that the stack level of "get_stack_info" and "logging" are consistent
#       in order to use the level found by get_stack_info for logging.
# 2. This is why we do not encapsulate the calculation of target_level
#       into a function in each logging function.


from __future__ import annotations

import inspect
import logging
import os
from typing import Mapping

from .config import Log


def debug(
    message: object,
    starts_with: str = 'test',
    stack_adjust: int = 0,
    stack_info: bool = False,
    stack_level: int | None = None,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calling logging.debug method, and finding stacklevel starts with specific function name.
    """
    target_level = get_stack_level(starts_with, stack_adjust + 1) if stack_level is None else stack_level + 1
    logging.debug(message, stack_info=stack_info, stacklevel=target_level, extra=extra)


def info(
    message: str,
    starts_with: str = 'test',
    stack_adjust: int = 0,
    stack_info: bool = False,
    stack_level: int | None = None,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calling logging.info method, and finding stacklevel starts with specific function name.
    """
    target_level = get_stack_level(starts_with, stack_adjust + 1) if stack_level is None else stack_level + 1
    logging.info(message, stack_info=stack_info, stacklevel=target_level, extra=extra)


def warning(
    message: str,
    starts_with: str = 'test',
    stack_adjust: int = 0,
    stack_info: bool = False,
    stack_level: int | None = None,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calling logging.warning method, and finding stacklevel starts with specific function name.
    """
    target_level = get_stack_level(starts_with, stack_adjust + 1) if stack_level is None else stack_level + 1
    logging.warning(message, stack_info=stack_info, stacklevel=target_level, extra=extra)


def error(
    message: str,
    starts_with: str = 'test',
    stack_adjust: int = 0,
    stack_info: bool = False,
    stack_level: int | None = None,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calling logging.error method, and finding stacklevel starts with specific function name.
    """
    target_level = get_stack_level(starts_with, stack_adjust + 1) if stack_level is None else stack_level + 1
    logging.error(message, stack_info=stack_info, stacklevel=target_level, extra=extra)


def exception(
    message: str,
    starts_with: str = 'test',
    stack_adjust: int = 0,
    stack_info: bool = False,
    stack_level: int | None = None,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calling logging.exception method, and finding stacklevel starts with specific function name.
    """
    target_level = get_stack_level(starts_with, stack_adjust + 1) if stack_level is None else stack_level + 1
    logging.exception(message, stack_info=stack_info, stacklevel=target_level, extra=extra)


def critical(
    message: str,
    starts_with: str = 'test',
    stack_adjust: int = 0,
    stack_info: bool = False,
    stack_level: int | None = None,
    extra: Mapping[str, object] | None = None
) -> None:
    """
    Calling logging.critical method, and finding stacklevel starts with specific function name.
    """
    target_level = get_stack_level(starts_with, stack_adjust + 1) if stack_level is None else stack_level + 1
    logging.critical(message, stack_info=stack_info, stacklevel=target_level, extra=extra)


def get_stack_level(starts_with: str = 'test', stack_adjust: int = 0) -> int:
    """
    Finding the stacklevel which the funcname starts with `starts_with` string.

    Args:
    - starts_with: finding the target stack level which function name starts with it.
    - stack_adjust: setup the default stack level base on 1,
        e.g. stack_adjust = 2 -> default stack level will be 1 + 2 = 3
    """
    try:
        # Setting context=0 ignores source code lines and significantly speeds up the first call.
        frames = inspect.stack(0)
        stack_default = 1 + stack_adjust  # 0: get_stack_level
        for index, frame in enumerate(frames[stack_default:], start=stack_default):
            if frame.function.startswith(starts_with):
                return index
        return stack_default
    finally:
        del frames


def get_stack_infos(
    starts_with: str = 'test',
    stack_adjust: int = 0,
    to_dict: bool = False
) -> str | dict[str, str]:
    """
    Finding the filename, lineno and funcname by funcname starts with `starts_with` string.

    Args:
    - starts_with: The string to search the function name which starts with.
    - stack_adjust: Adjust the start stack level.
    - to_dict: Determine the return type.

    Return:
    - to_dict is True: {'filename': 'xxx.py', 'lineno': '19', 'funcname': 'my_func'}
    - to_dict is False: '|xxx.py:19|my_func|'
    """
    try:
        # Setting context=0 ignores source code lines and significantly speeds up the first call.
        frames = inspect.stack(0)
        stack_default = 1 + stack_adjust  # 0: get_stack_info
        frame_target = frames[stack_default]
        for frame in frames[stack_default:]:
            if frame.function.startswith(starts_with):
                frame_target = frame
                break
        filename = os.path.basename(frame_target.filename)
        lineno = str(frame_target.lineno)
        funcname = frame_target.function
        if to_dict:
            return {'filename': filename, 'lineno': lineno, 'funcname': funcname}
        return f'|{filename}:{lineno}|{funcname}|'
    finally:
        del frames


def _debug(message: str = '') -> None:
    if Log.RECORD:
        debug(message)


def _info(message: str = '') -> None:
    if Log.RECORD:
        info(message)


def _warning(message: str = '') -> None:
    if Log.RECORD:
        warning(message)


def _error(message: str = '') -> None:
    if Log.RECORD:
        error(message)


def _exception(message: str = '') -> None:
    if Log.RECORD:
        exception(message)


def _critical(message: str = '') -> None:
    if Log.RECORD:
        critical(message)
