"""Akeneo Config class
"""


class Config:

    def __init__(self):

        self.gcp = {
            'project_id': 'chb-prod-ingest-ecom',
            'dataset_id': 'lightyear',
            'table_id': 'akeneo',
        }

        self.api = {
            'url': 'https://chalhoub.cloud.akeneo.com',
            'key': 'NF8zdnJxdHdqMnpsYzBvbzhnb2s0d2NjY2NzOG9rc284YzAwd29rbzR3MG9jZ2t3d3c4NDoydnNmcWhvcnhhbThrY3cwa2s0d3M0czBzNGc0NDhzNDhjb2M4b2tvdzhrNDRnZ2M0cw==',
            'max_items_per_request': 100,
            'accounts': {
                'faces': {
                    "grant_type": "password",
                    "username": "catalogapi_8178",
                    "password": "a929756f2",
                },
                'tryano': {
                    "grant_type": "password",
                    "username": "catalogapi_8178",
                    "password": "a929756f2",
                },
            },
        }

        self.args = [
            (
                ('-a', '--account'),
                {
                    'help': 'the akeneo account',
                    'choices': ['faces', 'tryano'],
                },
            ),
        ]

        self.queues = [
            'queue_1',
            'queue_2',
        ]

        self.module_name = 'lightyear.clients.akeneo.main'
        self.class_name = 'Akeneo'

        self.pipeline = [
            {
                'name': 'monitor',
                'function': 'monitor_proc',
                'queues': [
                    'queue_1',
                    'queue_2',
                ],
                'instances': 1,
                'join': False,
                'queues_to_close': [],
            },
            {
                'name': 'api_client',
                'function': 'api_client_proc',
                'queues': [
                    'queue_1',
                ],
                'instances': 1,
                'join': True,
                'queues_to_close': [
                    {
                        'name': 'queue_1',
                        'done_message': 'DONE',
                        'total_messages': 4,
                    }
                ],
            },
            {
                'name': 'validator',
                'function': 'doc_validator_proc',
                'queues': [
                    'queue_1',
                    'queue_2',
                ],
                'instances': 4,
                'join': True,
                'queues_to_close': [
                    {
                        'name': 'queue_2',
                        'done_message': 'DONE',
                        'total_messages': 2,
                    }
                ],
            },
            {
                'name': 'bigquery',
                'function': 'bigquery_proc',
                'queues': [
                    'queue_2',
                ],
                'instances': 2,
                'join': True,
                'queues_to_close': [],
            },
        ]


config = Config()
