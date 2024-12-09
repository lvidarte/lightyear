"""Brandquad Config class
"""
import os


class Config:
    def __init__(self):

        # fmt: off
        self.gcp = {
            "project_id": "chb-prod-ingest-ecom",
            "dataset_id": "lightyear",
            "table_id": "brandquad",
        }

        # Buffers
        self.logger_buffer = 1000
        self.bigquery_select_buffer = 100
        self.bigquery_insert_buffer = 100

        # Check queues every N seconds (mostly for debugging)
        self.monitor_freq = 0.1

        self.accounts = {
            "level": {
                "name": "level",
                "appid": "LVL",
                "token": os.environ.get('BRANDQUAD_LEVEL_TOKEN'),
                "api_url": "https://level.brandquad.io/api/public/v3/products/",
            },
        }

        self.args = [
            (
                ("-a", "--account"),
                {
                    "help": "the brandquad account",
                    "choices": ["level"],
                },
            ),
        ]

        self.queues = [
            "queue_1",
            "queue_2",
            "queue_3",
        ]

        self.module_name = "lightyear.clients.brandquad.pipeline"
        self.class_name = "Brandquad"

        self.pipeline = [
            {
                "name": "monitor",
                "enabled": False,
                "function": "monitor_proc",
                "queues": [
                    "queue_1",
                    "queue_2",
                    "queue_3",
                ],
                "instances": 1,
                "join": False,
                "queues_to_close": [],
            },
            {
                "name": "api_client",
                "enabled": True,
                "function": "api_client_proc",
                "queues": [
                    "queue_1",
                ],
                "instances": 1,
                "join": True,
                "queues_to_close": [
                    {
                        "name": "queue_1",
                        "done_message": "DONE",
                        "total_messages": 4,
                    }
                ],
            },
            {
                "name": "formatter",
                "enabled": True,
                "function": "doc_formatter_proc",
                "queues": [
                    "queue_1",
                    "queue_2",
                ],
                "instances": 4,
                "join": True,
                "queues_to_close": [
                    {
                        "name": "queue_2",
                        "done_message": "DONE",
                        "total_messages": 4,
                    }
                ],
            },
            {
                "name": "validator",
                "enabled": True,
                "function": "doc_validator_proc",
                "queues": [
                    "queue_2",
                    "queue_3",
                ],
                "instances": 4,
                "join": True,
                "queues_to_close": [
                    {
                        "name": "queue_3",
                        "done_message": "DONE",
                        "total_messages": 2,
                    }
                ],
            },
            {
                "name": "bigquery",
                "enabled": True,
                "function": "bigquery_proc",
                "queues": [
                    "queue_3",
                ],
                "instances": 2,
                "join": True,
                "queues_to_close": [],
            },
        ]
        # fmt: on


config = Config()
