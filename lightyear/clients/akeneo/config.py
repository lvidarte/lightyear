"""Akeneo Config class
"""


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
                "client_id": "4_3vrqtwj2zlc0oo8gok4wccccs8okso8c00woko4w0ocgkwww84",
                "secret": "2vsfqhorxam8kcw0kk4ws4s0s4g448s48coc8okow8k44ggc4s",
                "max_items_per_request": 100,
                "credentials": {
                    "grant_type": "password",
                    "username": "catalogapi_8178",
                    "password": "a929756f2",
                },
            },
            "tryano": {
                "name": "tryano",
                "api_url": "https://tryano.cloud.akeneo.com",
                "client_id": "4_2kv5pfy9c4g0sc08k4g8o8c4ggosso8ccg8sgks4gcg4sgkoo0",
                "secret": "3e87s6dxl8qos80k4sgw0gcsokcocgcowc8kw0kggckwc8sw00",
                "max_items_per_request": 100,
                "credentials": {
                    "grant_type": "password",
                    "username": "datateam_integration_1696",
                    "password": "34fb25c6b",
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
