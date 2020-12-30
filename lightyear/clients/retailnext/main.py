"""RetailNext pipeline class
"""

import json
import requests

from multiprocessing import current_process
from datetime import datetime, timedelta

from lightyear.core.logger import get_logger
from lightyear.core.bigquery import BigQuery
from lightyear.core import config as common_config
from .config import config


class RetailNext:

    def __init__(self, args):
        self.bigquery = BigQuery(**config.gcp)

    def monitor_proc(self, queue_1, queue_2):
        """Monitor process"""
        import time
        logger = get_logger(f"monitor-{self._process_id()}")
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


    def api_client_location_proc(self, queue_1):
        """RetailNext API client location process"""
        logger = get_logger(f"api-client-location-{self._process_id()}")
        logger.info(f"Process started")
        session = self._session()
        location_url = config.api['url'] + '/location'
        page_start = "0"
        count = 0
        while True:
            headers = {"X-Page-Length": "50", "X-Page-Start": page_start}
            response = session.get(location_url, headers=headers)
            data = response.json()
            for location in data["locations"]:
                queue_1.put(location)
                count += 1
            if "X-Page-Next" in response.headers:
                page_start = response.headers["X-Page-Next"]
            else:
                break
        logger.info(f"Process finished ({count} docs processed)")


    def api_client_datamine_proc(self, queue_1, queue_2):
        """RetailNext API client datamine process"""
        logger = get_logger(f"validator-{self._process_id()}")
        logger.info(f"Process started")
        session = self._session()
        datamine_url = config.api['url'] + '/datamine'
        date = self._last_day()
        first_day, last_day = self._date_ranges()
        count = 0
        while True:
            location = queue_1.get()
            if location == 'DONE':
                break
            else:
                logger.info(f"Getting metrics for location {location['name']}")
                query = {
                    'locations': [ location['id'] ],
                    'time_ranges': [ { 'type': 'store_hours' } ],
                    'group_bys': [ { 'value': 1, 'unit': 'hours', 'group': 'time' } ],
                    'date_ranges': [ { 'first_day': date, 'last_day': date } ],
                    'metrics': [ 'traffic_in', 'traffic_out' ]
                }
                response = session.post(datamine_url, data=json.dumps(query))
                queue_2.put(self._format(date, location, response.json()))
                count += 1
            if count % 100 == 0:
                logger.info(f"{count} docs sent to queue_2")
        logger.info(f"Process finished ({count} docs processed)")


    def bigquery_proc(self, queue_2):
        """BigQuery insert process"""
        logger = get_logger(f"bigquery-{self._process_id()}")
        logger.info(f"Process started")
        count = 0
        docs = []
        while True:
            doc = queue_2.get()
            if doc == 'DONE':
                #if docs:
                #    self.bigquery.insert(docs)
                break
            else:
                docs.append(doc)
                count += 1
                if count % 100 == 0:
                    #self.bigquery.insert(docs)
                    logger.info(f"{count} docs sent to bigquery")
                    docs = []
        logger.info(f"Process finished ({count} docs processed)")
    

    def _format(self, date, location, metrics):
        """Need to work on this..."""
        return {
            'date': date,
            'location': location,
            'metrics': metrics,
            'metadata': {
                'ingestion_time': datetime.now().strftime(common_config.time_format),
            },
        }


    def _first_day(self):
        return self._date_timedelta(2)

    def _last_day(self):
        return self._date_timedelta(1)

    def _date_ranges(self):
        return (self._first_day(), self._last_day())

    def _date_timedelta(self, days):
        date = datetime.today() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")

    def _session(self):
        session = requests.Session()
        session.auth = (config.api['access_key'], config.api['secret_key'])
        return session

    def _process_id(self):
        return current_process()._identity[0]

