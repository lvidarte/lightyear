"""RetailNext Config class
"""


class Config:
    def __init__(self):

        # fmt: off
        self.gcp = {
            "project_id": "chb-prod-ingest-ecom",
            "dataset_id": "lightyear",
            "table_id": "retailnext",
        }

        # Buffers
        self.logger_buffer = 1000
        self.bigquery_select_buffer = 100
        self.bigquery_insert_buffer = 100

        # Check queues every N seconds (mostly for debugging)
        self.monitor_freq = 0.1

        self.accounts = {
            "swarovski": {
                "name": "swarovski",
                "access_key": "722cae92-e991-11e9-9f8b-0000f94ce06d",
                "secret_key": "qj1GV8pCygSAvZ2jocZAwli4Hqo",
                "api_url": "https://swarovski-me.api.retailnext.net/v1",
            },
        }

        self.args = [
            (
                ("-a", "--account"),
                {
                    "help": "the retailnext account",
                    "choices": ["swarovski"],
                },
            ),
        ]

        self.queues = [
            "queue_1",
            "queue_2",
        ]

        self.module_name = "lightyear.clients.retailnext.pipeline"
        self.class_name = "RetailNext"

        self.pipeline = [
            {
                "name": "monitor",
                "function": "monitor_proc",
                "queues": [
                    "queue_1",
                    "queue_2",
                ],
                "instances": 1,
                "join": False,
                "queues_to_close": [],
            },
            {
                "name": "api_client_location",
                "function": "api_client_location_proc",
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
                "name": "api_client_datamine",
                "function": "api_client_datamine_proc",
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
                        "total_messages": 2,
                    }
                ],
            },
            {
                "name": "bigquery",
                "function": "bigquery_proc",
                "queues": [
                    "queue_2",
                ],
                "instances": 2,
                "join": True,
                "queues_to_close": [],
            },
        ]
        # fmt: on


config = Config()
