"""Pipeline base class
"""

from multiprocessing import current_process

from lightyear.core.logger import get_logger


class Pipeline:

    def __init__(self, config, args):
        self.config = config
        self.args = args

    def get_logger(self, fn_name):
        return get_logger(self._process_id(fn_name))

    def _process_id(self, fn_name):
        name = ''
        for process in self.config.pipeline:
            if process['function'] == fn_name:
                name = process['name']
        id_ = current_process()._identity[0]
        return f"{name}-{id_}"

