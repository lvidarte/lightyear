"""Akeneo pipeline class
"""

import requests

from urllib.parse import urlsplit, parse_qs
from datetime import datetime

from lightyear.core.bigquery import BigQuery
from lightyear.core import config as common_config
from lightyear.core import Pipeline


class Akeneo(Pipeline):

    def __init__(self, config, args):
        super().__init__(config, args)
        self.account = self.args.account
        self.credentials = self.config.api['accounts'][self.account]
        self.bigquery = BigQuery(**self.config.gcp)


    def monitor_proc(self, queue_1, queue_2):
        """Monitor process"""
        import time
        logger = self.get_logger('monitor_proc')
        while True:
            try:
                queue_1_size = queue_1.qsize()
                queue_2_size = queue_2.qsize()
                if queue_1_size or queue_2_size:
                    logger.info(f"Queue sizes: queue_1={queue_1_size}, queue_2={queue_2_size}")
                time.sleep(.1)
            except NotImplementedError:
                logger.error("Unable to show queue size (running macos?)")
                break


    def api_client_proc(self, queue_1):
        """Akeneo API client process"""
        logger = self.get_logger('api_client_proc')
        logger.info(f"Process started")
        token = self._auth()
        params = None
        count = 0
        while True:
            docs, next_params = self._products(token, params)
            for doc in docs:
                queue_1.put(doc)
            count += len(docs)
            logger.info(f"{count} docs sent to queue_1")
            if next_params:
                params = next_params
            else:
                break
        logger.info(f"Process finished ({count} docs processed)")


    def doc_validator_proc(self, queue_1, queue_2):
        """BigQuery doc validator"""
        logger = self.get_logger('doc_validator_proc')
        logger.info(f"Process started")
        count = 0
        while True:
            doc = queue_1.get()
            if doc == 'DONE':
                break
            else:
                count += 1
                queue_2.put(self._format(doc))
            if count % 100 == 0:
                logger.info(f"{count} docs sent to queue_2")
        logger.info(f"Process finished ({count} docs processed)")


    def bigquery_proc(self, queue_2):
        """BigQuery insert process"""
        logger = self.get_logger('bigquery_proc')
        logger.info(f"Process started")
        count = 0
        docs = []
        while True:
            doc = queue_2.get()
            if doc == 'DONE':
                if docs:
                    self.bigquery.insert(docs)
                break
            else:
                docs.append(doc)
                count += 1
                if count % 100 == 0:
                    self.bigquery.insert(docs)
                    logger.info(f"{count} docs sent to bigquery")
                    docs = []
        logger.info(f"Process finished ({count} docs processed)")
    

    def _format(self, doc):
        """Need to work on this..."""
        return {
            'id': doc['identifier'],
            'account': self.account,   # faces, tryano
            'enabled': doc['enabled'],
            'family': doc['family'],
            'created': doc['created'],
            'updated': doc['updated'],
            'metadata': {
                'ingestion_time': datetime.now().strftime(common_config.time_format),
            },
        }


    def _auth(self):
        url = self.config.api['url'] + '/api/oauth/v1/token'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.config.api['key']}",
        }
        res = requests.post(url, json=self.credentials, headers=headers)
        if res.status_code == 200:
            return res.json()["access_token"]


    def _parse_params(self, url):
        query = urlsplit(url).query
        params = parse_qs(query)
        return {k: v[0] for k, v in params.items()}


    def _products(self, token, params=None):
        url = self.config.api['url'] + '/api/rest/v1/products'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if params is None:
            params = {
                "pagination_type": "search_after",
                "search_after": None,
                "limit": self.config.api['max_items_per_request'],
            }
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 200:
            doc = res.json()
            try:
                next_params = self._parse_params(doc["_links"]["next"]["href"])
            except:
                next_params = None
            return doc["_embedded"]["items"], next_params
