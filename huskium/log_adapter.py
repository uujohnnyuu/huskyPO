# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskium/
# GitHub: https://github.com/uujohnnyuu/huskium


import logging


class PageElementLoggerAdapter(logging.LoggerAdapter):

    def __init__(self, logger, petype, remark):
        super().__init__(logger, {"petype": petype, "remark": remark})

    def process(self, msg, kwargs):
        return f'{self.extra["petype"]}({self.extra["remark"]}): {msg}', kwargs
