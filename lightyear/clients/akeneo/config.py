"""Akeneo Config class
"""
import os


class Config:
    def __init__(self):

        # fmt: off
        self.gcp = {
            "project_id": "chb-prod-ingest-ecom",
            "dataset_id": "lightyear",
            "table_id": "akeneo",
        }

        # Buffers
        self.logger_buffer = 1000
        self.bigquery_select_buffer = 100
        self.bigquery_insert_buffer = 100

        # Check queues every N seconds (mostly for debugging)
        self.monitor_freq = 0.1

        # Datetime format for created and updated fields
        self.time_format = "%Y-%m-%dT%H:%M:%S%z"

        self.accounts = {
            "faces": {
                "name": "faces",
                "api_url": "https://chalhoub.cloud.akeneo.com",
                "client_id": os.environ.get('AKENEO_FACES_CLIENT_ID'),
                "secret": os.environ.get('AKENEO_FACES_SECRET'),
                "max_items_per_request": 100,
                "credentials": {
                    "grant_type": "password",
                    "username": os.environ.get('AKENEO_FACES_CREDENTIALS_USERNAME'),
                    "password": os.environ.get('AKENEO_FACES_CREDENTIALS_PASSWORD'),
                },
            },
            "tryano": {
                "name": "tryano",
                "api_url": "https://tryano.cloud.akeneo.com",
                "client_id": os.environ.get('AKENEO_TRYANO_CLIENT_ID'),
                "secret": os.environ.get('AKENEO_TRYANO_SECRET'),
                "max_items_per_request": 100,
                "credentials": {
                    "grant_type": "password",
                    "username": os.environ.get('AKENEO_TRYANO_CREDENTIALS_USERNAME'),
                    "password": os.environ.get('AKENEO_TRYANO_CREDENTIALS_PASSWORD'),
                },
            },
        }

        self.args = [
            (
                ("-a", "--account"),
                {
                    "help": "the akeneo account",
                    "choices": ["faces", "tryano"],
                },
            ),
        ]

        self.queues = [
            "queue_1",
            "queue_2",
            "queue_3",
        ]

        self.module_name = "lightyear.clients.akeneo.pipeline"
        self.class_name = "Akeneo"

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
