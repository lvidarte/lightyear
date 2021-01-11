"""BigQuery module
"""

from datetime import datetime

import google.auth
from google.cloud import bigquery

from lightyear.core import config


class BigQuery:
    def __init__(self, project_id, dataset_id=None, table_id=None):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = self.get_client()

    def get_client(self):
        # fmt: off
        credentials, project = google.auth.default(scopes=[
            'https://www.googleapis.com/auth/bigquery',
        ])
        # fmt: on
        return bigquery.Client(project=self.project_id, credentials=credentials)

    def table_uri(self):
        return f"{self.project_id}.{self.dataset_id}.{self.table_id}"

    def query(self, query):
        query_job = self.client.query(query)
        return query_job.result()

    def insert(self, docs):
        table = self.client.get_table(self.table_uri())
        for doc in docs:
            doc["metadata"]["insertion_time"] = datetime.now().strftime(config.time_format)
        errors = self.client.insert_rows(table, docs)  # Make an API request.
        if errors:
            raise Exception(f"Insertion error - {errors}")
        return len(docs)
