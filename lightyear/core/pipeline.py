"""Pipeline base class
"""

from multiprocessing import current_process


class Pipeline:

    def __init__(self, config, args):
        self.config = config
        self.args = args

    def process_id(self, fn_name):
        name = ''
        for process in self.config.pipeline:
            if process['function'] == fn_name:
                name = process['name']
        id_ = current_process()._identity[0]
        return f"{name}-{id_}"
