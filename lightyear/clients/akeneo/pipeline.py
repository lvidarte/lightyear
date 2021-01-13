"""Akeneo pipeline class
"""

import time
from base64 import b64encode
from datetime import datetime
from urllib.parse import parse_qs, urlsplit

import requests

from lightyear.core import Pipeline, config


class Akeneo(Pipeline):
    def __init__(self, config, args, bigquery_cls):
        super().__init__(config, args, bigquery_cls)
        self.account = config.accounts[args.account]

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
                time.sleep(self.config.monitor_freq)
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
            if count % self.config.logger_buffer == 0:
                logger.info(f"{count} docs received from api")
            if next_params:
                params = next_params
            else:
                break
        logger.info(f"Process finished ({count} docs received)")

    def doc_formatter_proc(self, queue_1, queue_2):
        """Document format according to BigQuery schema"""
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
            if count % self.config.logger_buffer == 0:
                logger.info(f"{count} docs processed")
        logger.info(f"Process finished ({count} docs processed)")

    def doc_validator_proc(self, queue_2, queue_3):
        """Validate if doc already in BigQuery"""
        logger = self.get_logger("doc_validator_proc")
        logger.info("Process started")
        count = 0
        docs = []
        while True:
            doc = queue_2.get()
            if doc == "DONE":
                if docs:
                    self._validate_and_send(docs, queue_3)
                break
            else:
                docs.append(doc)
                count += 1
                if count % self.config.bigquery_select_buffer == 0:
                    self._validate_and_send(docs, queue_3)
                    docs = []
            if count % self.config.logger_buffer == 0:
                logger.info(f"{count} docs processed")
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
                    self.bigquery.insert(docs, logger)
                break
            else:
                docs.append(doc)
                count += 1
                if count % self.config.bigquery_insert_buffer == 0:
                    self.bigquery.insert(docs, logger)
                    logger.info(f"{count} docs sent to bigquery")
                    docs = []
        logger.info(f"Process finished ({count} docs processed)")

    def _format(self, doc):
        """BigQuery document format"""
        # fmt: off
        return {
            "id": doc["identifier"],
            "account": self.account["name"],  # faces, tryano
            "enabled": doc["enabled"],
            "family": doc["family"],
            "categories": ','.join(doc["categories"]) if doc["categories"] else None,
            "groups": str(doc["groups"]),
            "parent": doc["parent"],
            "values": self._parse_values(doc["values"]),
            "created": datetime.strptime(doc["created"], self.config.time_format).strftime(config.time_format),
            "updated": datetime.strptime(doc["updated"], self.config.time_format).strftime(config.time_format),
            "metadata": {
                "ingestion_time": self.ingestion_time,  # common value for all docs
                "insertion_time": None,  # it will set in bigquery insert action
            },
        }
        # fmt: on

    def _parse_values(self, values_dict):
        values = []
        for name, values_lst in values_dict.items():
            for item in values_lst:
                # fmt: off
                values.append({
                    "name": name,
                    "locale": item.get("locale"),
                    "scope": item.get("scope"),
                    "data": self._parse_data(item.get("data")),
                })
                # fmt: on
        return values

    def _parse_data(self, data_obj):
        if data_obj is None:
            return None
        elif isinstance(data_obj, list):
            return ",".join([str(s) for s in data_obj])
        else:
            return str(data_obj)

    def _validate_and_send(self, docs, queue):
        results = {d["id"]: {"updated": d["updated"], "insert": True} for d in docs}
        query = """
            SELECT id, updated
            FROM (
                SELECT id, updated, RANK() OVER(PARTITION BY id ORDER BY updated DESC) rank
                FROM `{}`
                WHERE account="{}" AND id IN ({})
            )
            WHERE rank=1
        """.format(
            self.bigquery.table_uri(),
            self.account["name"],
            ",".join([f"\"{d['id']}\"" for d in docs]),
        )
        for row in self.bigquery.query(query):
            row_updated = row.updated.strftime(config.time_format)
            if results[row.id]["updated"] == row_updated:
                results[row.id]["insert"] = False
        for doc in docs:
            if results[doc["id"]]["insert"]:
                queue.put(doc)

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
