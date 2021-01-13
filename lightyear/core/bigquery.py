"""BigQuery module
"""

from datetime import datetime

import google.auth
from google.cloud import bigquery

from lightyear.core import config


class BigQuery:
    def __init__(self, project_id, dataset_id, table_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self._dummy = False
        self.client = self.get_client()

    def dummy(self, dummy=True):
        self._dummy = dummy

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

    def insert(self, docs, logger=None):
        if self._dummy:
            logger.info(f"Dummy mode on: avoid inserting {len(docs)} docs")
        else:
            table = self.client.get_table(self.table_uri())
            for doc in docs:
                doc["metadata"]["insertion_time"] = datetime.now().strftime(config.time_format)
            errors = self.client.insert_rows(table, docs)  # Make an API request.
            if errors and logger:
                logger.error(str(errors))
