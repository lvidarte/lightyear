"""Lightyear Engine
"""

import importlib
import multiprocessing

from lightyear.core.bigquery import BigQuery
from lightyear.core.logger import get_logger


def run(client_config, args):
    logger = get_logger()
    module = importlib.import_module(client_config.module_name)
    client_obj = getattr(module, client_config.class_name)(client_config, args, BigQuery)
    context = multiprocessing.get_context("fork")
    queues = {name: context.Queue() for name in client_config.queues}
    pools = []

    for process in client_config.pipeline:
        if process["enabled"]:
            logger.info(f"Starting {process['instances']} {process['name']} process")
            params = tuple(queues[name] for name in process["queues"])
            # fmt: off
            pool = context.Pool(
                process["instances"],
                getattr(client_obj, process["function"]),
                params,
            )
            # fmt: on
            pool.close()
            pools.append((pool, process))

    for pool, process in pools:
        if process["join"]:
            pool.join()
            logger.info(f"All {process['name']} processes have finished")
        for queue in process["queues_to_close"]:
            for _ in range(queue["total_messages"]):
                queues[queue["name"]].put(queue["done_message"])
            queues[queue["name"]].close()

    for queue in queues.values():
        queue.join_thread()
