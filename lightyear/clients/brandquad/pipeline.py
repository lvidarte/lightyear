"""Brandquad pipeline class
"""

import time
from datetime import datetime

import requests

from lightyear.core import Pipeline, config


class Brandquad(Pipeline):
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
                time.sleep(0.1)
            except NotImplementedError:
                logger.error("Unable to show queue size (running macos?)")
                break

    def api_client_proc(self, queue_1):
        """Brandquad API client process"""
        logger = self.get_logger("api_client_proc")
        logger.info("Process started")
        next_url = self.account["api_url"]
        count = 0
        while True:
            docs, next_url = self._products(next_url)
            for doc in docs:
                queue_1.put(doc)
            count += len(docs)
            if count % self.config.logger_buffer == 0:
                logger.info(f"{count} docs received from api")
            if not next_url:
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

    def _products(self, url):
        headers = {
            "Content-Type": "application/json",
            "TOKEN": self.account["token"],
            "APPID": self.account["appid"],
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            doc = res.json()
            return doc["results"], doc["next"]
        else:
            raise Exception(f"{res.status_code} {res.text}")

    def _format(self, doc):
        """BigQuery document format"""
        # fmt: off
        meta = doc["meta"]
        return {
            "id": meta["id"],
            "account": self.account["name"],
            "updated": datetime.fromtimestamp(meta["timestamp"]).strftime(config.time_format),
            "name": meta.get("name"),
            "version": meta.get("version"),
            "type": meta.get("type"),
            "abstract_level": meta.get("abstract_level"),
            "infomodel": meta.get("infomodel"),
            "product_model": meta["product_model"] if isinstance(meta.get("product_model"), str) else None,
            "parent_product": meta.get("parent_product"),
            "cover": meta["cover"] if isinstance(meta.get("cover"), str) else None,
            "status": meta.get("status"),
            "taxonomy": meta.get("taxonomy"),
            "progress": meta.get("progress", []),

            "attributes": self._parse_attributes(doc["attributes"]),
            "assets": self._parse_assets(doc["assets"]),
            "categories": doc["categories"],
            # "relations": doc["relations"],  # not info
            # "sets": doc["sets"],  # not info

            "metadata": {
                "ingestion_time": self.ingestion_time,  # common value for all docs
                "insertion_time": None,  # it will set in bigquery insert action
            },
        }
        # fmt: on

    def _parse_attributes(self, doc):
        attributes = []
        for name, attr in doc.items():
            if attr:
                attribute = {
                    "name": name,
                    "items": [],
                }
                if isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, dict):
                            attribute["items"].append(
                                {
                                    "name": item.get("name"),
                                    "locale": item.get("locale"),
                                    "value": self._parse_value(item.get("value", [])),
                                }
                            )
                        else:
                            attribute["items"].append(
                                {
                                    "name": None,
                                    "locale": None,
                                    "value": str(item),
                                }
                            )
                else:
                    attribute["items"].append(
                        {
                            "name": None,
                            "locale": None,
                            "value": str(attr),
                        }
                    )
                attributes.append(attribute)
        return attributes

    def _parse_value(self, value):
        if isinstance(value, list):
            return ",".join([str(o) for o in value])
        else:
            return str(value)

    def _parse_assets(self, assets):
        for item in assets:
            del item["dam"]["meta_info"]  # Always {}
            if "size" not in item["dam"] or not item["dam"]["size"]:
                item["dam"]["size"] = {
                    "width": None,
                    "height": None,
                }
        return assets

    def _validate_and_send(self, docs, queue):
        results = {d["id"]: {"updated": d["updated"], "insert": True} for d in docs}
        query = """
            SELECT id, updated
            FROM `{}`
            WHERE id IN ({})
        """.format(
            self.bigquery.table_uri(),
            ",".join([f"\"{d['id']}\"" for d in docs]),
        )
        for row in self.bigquery.query(query):
            row_updated = row.updated.strftime(config.time_format)
            if results[row.id]["updated"] == row_updated:
                results[row.id]["insert"] = False
        for doc in docs:
            if results[doc["id"]]["insert"]:
                queue.put(doc)
