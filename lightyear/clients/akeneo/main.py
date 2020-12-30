"""Akeneo
"""

import os

import requests

from urllib.parse import urlsplit, parse_qs
from multiprocessing import current_process

from lightyear.core.logger import get_logger
from .config import config


class Akeneo:

    def __init__(self, args):
        self.credentials = config.api['accounts'][args.account]


    def auth(self):
        url = config.api['url'] + '/api/oauth/v1/token'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {config.api['key']}",
        }
        res = requests.post(url, json=self.credentials, headers=headers)
        if res.status_code == 200:
            return res.json()["access_token"]


    def parse_params(self, url):
        query = urlsplit(url).query
        params = parse_qs(query)
        return {k: v[0] for k, v in params.items()}


    def products(self, token, params=None):
        url = config.api['url'] + '/api/rest/v1/products'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if params is None:
            params = {
                "pagination_type": "search_after",
                "search_after": None,
                "limit": config.api['max_items_per_request'],
            }
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 200:
            doc = res.json()
            try:
                next_params = self.parse_params(doc["_links"]["next"]["href"])
            except:
                next_params = None
            return doc["_embedded"]["items"], next_params


    def monitor_proc(self, queue_1, queue_2):
        import time
        process_id = f"monitor-{current_process()._identity[0]}"
        logger = get_logger(process_id)
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
        process_id = f"api-client-{current_process()._identity[0]}"
        logger = get_logger(process_id)
        logger.info(f'Process started')
        token = self.auth()
        params = None
        count = 0
        while True:
            docs, next_params = self.products(token, params)
            for doc in docs:
                queue_1.put(doc)
            count += len(docs)
            logger.info(f'{count} docs sent to queue_1')
            if next_params:
                params = next_params
            else:
                break
        logger.info(f'Process finished ({count} docs processed)')


    def doc_validator_proc(self, queue_1, queue_2):
        process_id = f"validator-{current_process()._identity[0]}"
        logger = get_logger(process_id)
        logger.info(f'Process started')
        count = 0
        while True:
            doc = queue_1.get()
            if doc == 'DONE':
                break
            else:
                count += 1
                queue_2.put(doc)
            if count % 100 == 0:
                logger.info(f'{count} docs sent to queue_2')
        logger.info(f'Process finished ({count} docs processed)')


    def bigquery_proc(self, queue_2):
        process_id = f"bigquery-{current_process()._identity[0]}"
        logger = get_logger(process_id)
        logger.info(f'Process started')
        count = 0
        while True:
            doc = queue_2.get()
            if doc == 'DONE':
                break
            else:
                count += 1
                if count % 100 == 0:
                    logger.info(f'{count} docs sent to bigquery')
                    count_partial = 0
        logger.info(f'Process finished ({count} docs processed)')

