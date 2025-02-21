# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


"""
`logstack` will be deprecated in huskium v1.1.0+. 
Use `huskium.logging.PrefixFilter()` instead.
"""


from __future__ import annotations

import warnings
import inspect
import logging
import os
from typing import Mapping

from .config import Log


WARN_MSG = '"logstack" will be deprecated in huskium v1.1.0+. Use "huskium.logging.PrefixFilter()" instead.'


warnings.simplefilter("default", DeprecationWarning)
warnings.warn(WARN_MSG, DeprecationWarning, stacklevel=2)


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
    lower: bool | None = None,
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
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
    lower: bool | None = None,
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
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
    lower: bool | None = None,
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
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
    lower: bool | None = None,
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
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
    lower: bool | None = None,
    excinfo: bool | tuple | None = True,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
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
    lower: bool | None = None,
    excinfo: bool | tuple | None = None,
    stackinfo: bool = False,
    stacklevel: int = 1,
    extra: Mapping[str, object] | None = None
) -> None:
    logging.critical(
        message,
        exc_info=excinfo,
        stack_info=stackinfo,
        stacklevel=get_stacklevel(prefix, lower, stacklevel),
        extra=extra
    )


def get_stacklevel(
    prefix: str | None = None,
    lower: bool | None = None,
    start: int = 1,
    outer: int = 1
) -> int:
    # Adjust start to the first frame of the actual logging.
    start += outer

    # If final prefix is None, return start directly.
    prefix = prefix or Log._PREFIX
    if prefix is None:
        return start

    # Set lower.
    if lower is None:
        lower = Log._LOWER
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
        funcname = frame.f_code.co_name
        filename = os.path.basename(frame.f_code.co_filename)
        if funcname.startswith(prefix) or filename.startswith(prefix):
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
