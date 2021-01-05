"""RetailNext pipeline class
"""

import json
import requests

from datetime import datetime, timedelta

from lightyear.core.bigquery import BigQuery
from lightyear.core import config as common_config
from lightyear.core import Pipeline


class RetailNext(Pipeline):

    def __init__(self, config, args):
        super().__init__(config, args)
        self.bigquery = BigQuery(**self.config.gcp)


    def monitor_proc(self, queue_1, queue_2):
        """Monitor process"""
        import time
        logger = self.get_logger('monitor_proc')
        logger.info(f"Process started")
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
        logger = self.get_logger('api_client_location_proc')
        logger.info(f"Process started")
        session = self._session()
        location_url = self.config.api['url'] + '/location'
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
        logger = self.get_logger('api_client_datamine_proc')
        logger.info(f"Process started")
        session = self._session()
        datamine_url = self.config.api['url'] + '/datamine'
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


    def _format(self, date, location, metrics):
        """BigQuery document format"""
        del location['attributes']
        if 'address' in location:
            location['address'] = location['address'].get('street_address')
        return {
            'date': date,
            'location': location,
            'metrics': metrics['metrics'],
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
        session.auth = (
            self.config.api['access_key'],
            self.config.api['secret_key'],
        )
        return session