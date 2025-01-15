# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


from __future__ import annotations

import os
import logging


_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'


def basic(
    file: str = './log.log',
    level: int = logging.INFO,
    format: str = _FORMAT,
    datefmt: str = '%Y-%m-%d %H:%M:%S',
    filemode: str = 'w'
) -> None:
    """
    Simply set `logging.basicConfig()`.

    Args:
        - file: Relative or absolute path of the file.
        - others: The same as `logging.basicConfig()`.
    """
    abspath = os.path.abspath(file)
    dirname = os.path.dirname(abspath)
    os.makedirs(dirname, exist_ok=True)
    logging.basicConfig(
        level=level,
        format=format,
        datefmt=datefmt,
        filename=abspath,
        filemode=filemode
    )
    logging.info(f'file    : {file}')
    logging.info(f'abspath : {abspath}')
    logging.info(f'dirname : {dirname}')
