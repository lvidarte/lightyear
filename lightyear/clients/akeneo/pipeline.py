"""Akeneo pipeline class
"""

import time
from base64 import b64encode
from datetime import datetime
from urllib.parse import parse_qs, urlsplit

import requests

from lightyear.core import Pipeline
from lightyear.core import config as common_config
from lightyear.core.bigquery import BigQuery


class Akeneo(Pipeline):
    def __init__(self, config, args):
        super().__init__(config, args)
        self.account = config.accounts[args.account]
        self.bigquery = BigQuery(**config.gcp)

    def monitor_proc(self, queue_1, queue_2, queue_3):
        """Monitor process"""
        logger = self.get_logger("monitor_proc")
        logger.info("Process started")
        while True:
            try:
                queue_1_size = queue_1.qsize()
                queue_2_size = queue_2.qsize()
                queue_3_size = queue_3.qsize()
                if queue_1_size or queue_2_size or queue_3_size:
                    logger.info(f"Queue sizes: queue_1={queue_1_size}, queue_2={queue_2_size}, queue_3={queue_3_size}")
                time.sleep(0.1)
            except NotImplementedError:
                logger.error("Unable to show queue size (running macos?)")
                break

    def api_client_proc(self, queue_1):
        """Akeneo API client process"""
        logger = self.get_logger("api_client_proc")
        logger.info("Process started")
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

    def doc_formatter_proc(self, queue_1, queue_2):
        """Custom format"""
        logger = self.get_logger("doc_formatter_proc")
        logger.info("Process started")
        count = 0
        while True:
            doc = queue_1.get()
            if doc == "DONE":
                break
            else:
                count += 1
                queue_2.put(self._format(doc))
            if count % 100 == 0:
                logger.info(f"{count} docs sent to queue_2")
        logger.info(f"Process finished ({count} docs processed)")

    def doc_validator_proc(self, queue_2, queue_3):
        """Validate if doc already in BigQuery"""
        logger = self.get_logger("doc_validator_proc")
        logger.info("Process started")
        count = 0
        while True:
            doc = queue_2.get()
            if doc == "DONE":
                break
            else:
                count += 1
                queue_3.put(doc)  # Check here if doc already in bigquery
            if count % 100 == 0:
                logger.info(f"{count} docs sent to queue_3")
        logger.info(f"Process finished ({count} docs processed)")

    def bigquery_proc(self, queue_3):
        """BigQuery insert process"""
        logger = self.get_logger("bigquery_proc")
        logger.info("Process started")
        count = 0
        docs = []
        while True:
            doc = queue_3.get()
            if doc == "DONE":
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
        # fmt: off
        return {
            "id": doc["identifier"],
            "account": self.account["name"],  # faces, tryano
            "enabled": doc["enabled"],
            "family": doc["family"],
            "created": doc["created"],
            "updated": doc["updated"],
            "metadata": {
                "ingestion_time": datetime.now().strftime(common_config.time_format),
            },
        }
        # fmt: on

    def _auth(self):
        url = self.account["api_url"] + "/api/oauth/v1/token"
        key = b64encode(f'{self.account["client_id"]}:{self.account["secret"]}'.encode("ascii"))
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {key.decode()}",
        }
        res = requests.post(url, json=self.account["credentials"], headers=headers)
        if res.status_code == 200:
            return res.json()["access_token"]
        else:
            raise Exception(f"{res.status_code} {res.text}")

    def _parse_params(self, url):
        query = urlsplit(url).query
        params = parse_qs(query)
        return {k: v[0] for k, v in params.items()}

    def _products(self, token, params=None):
        url = self.account["api_url"] + "/api/rest/v1/products"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if params is None:
            params = {
                "pagination_type": "search_after",
                "search_after": None,
                "limit": self.account["max_items_per_request"],
            }
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 200:
            doc = res.json()
            try:
                next_params = self._parse_params(doc["_links"]["next"]["href"])
            except Exception:
                next_params = None
            return doc["_embedded"]["items"], next_params
        else:
            raise Exception(f"{res.status_code} {res.text}")
