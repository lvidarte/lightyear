"""Main Config
"""

from lightyear.clients.akeneo import config as akeneo_config
from lightyear.clients.brandquad import config as brandquad_config
from lightyear.clients.retailnext import config as retailnext_config


class Config:
    def __init__(self):

        # fmt: off
        self.gcp = {
            "project_id": "chb-prod-ingest-ecom",
            "dataset_id": "",
            "table_id": "",
        }

        self.clients = {
            "akeneo": akeneo_config,
            "brandquad": brandquad_config,
            "retailnext": retailnext_config,
        }

        self.date_format = "%Y-%m-%d"
        self.time_format = "%Y-%m-%d %H:%M:%S.%f"

        self.slack = {
            "url": "https://hooks.slack.com/services/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",
        }
        # fmt: on


config = Config()
