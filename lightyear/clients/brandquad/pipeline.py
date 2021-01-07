"""Brandquad pipeline class
"""

import time
from datetime import datetime

import requests

from lightyear.core import Pipeline
from lightyear.core import config as common_config
from lightyear.core.bigquery import BigQuery


class Brandquad(Pipeline):
    def __init__(self, config, args):
        super().__init__(config, args)
        self.bigquery = BigQuery(**self.config.gcp)

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
        """Brandquad API client process"""
        logger = self.get_logger("api_client_proc")
        logger.info("Process started")
        next_url = self.config.api["url"]
        count = 0
        while True:
            docs, next_url = self._products(next_url)
            for doc in docs:
                queue_1.put(doc)
            count += len(docs)
            logger.info(f"{count} docs sent to queue_1")
            if not next_url:
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
                # if docs:
                #    self.bigquery.insert(docs)
                break
            else:
                docs.append(doc)
                count += 1
                if count % 100 == 0:
                    # self.bigquery.insert(docs)
                    logger.info(f"{count} docs sent to bigquery")
                    docs = []
        logger.info(f"Process finished ({count} docs processed)")

    def _products(self, url):
        headers = {
            "Content-Type": "application/json",
            "TOKEN": self.config.api["token"],
            "APPID": self.config.api["appid"],
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            doc = res.json()
            return doc["results"], doc["next"]
        else:
            raise Exception(f"{res.status_code} {res.text}")

    def _format(self, product):
        """BigQuery document format"""
        # fmt: off
        return {
            "product": product,
            "metadata": {
                "ingestion_time": datetime.now().strftime(common_config.time_format),
            },
        }
        # fmt: on
