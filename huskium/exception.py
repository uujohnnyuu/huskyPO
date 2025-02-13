# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


class _ForcedRelocationException(Exception):
    """
    Used internally in Element._if_force_relocate() when cache = False,
    allowing the process to directly relocate the element without checking the cache attribute.
    """
    pass
