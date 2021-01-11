"""Pipeline base class
"""

from datetime import datetime
from multiprocessing import current_process

from lightyear.core import config as common_config
from lightyear.core.logger import get_logger


class Pipeline:
    def __init__(self, config, args, bigquery_cls):
        self.config = config
        self.args = args
        self.bigquery = bigquery_cls(**config.gcp)
        self.ingestion_time = datetime.now().strftime(common_config.time_format)

    def get_logger(self, fn_name):
        return get_logger(self._process_id(fn_name))

    def _process_id(self, fn_name):
        process_name = ""
        for process in self.config.pipeline:
            if process["function"] == fn_name:
                process_name = process["name"]
                break
        id_ = current_process()._identity[0]
        return f"{process_name}-{id_}"
