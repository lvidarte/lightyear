# Akeneo Pipeline

![Akeneo Pipeline](./akeneo_pipeline.png "Akeneo Pipeline")


## Command line options for Akeneo

```sh
$ python main.py akeneo --help
usage: lightyear akeneo [-h] [-a {faces,tryano}]

optional arguments:
  -h, --help            show this help message and exit
  -a {faces,tryano}, --account {faces,tryano}
                        The Akeneo account
```

## Log example

```sh
$ docker-compose up
Starting lightyear ... done
Attaching to lightyear
lightyear    | [ INFO ] main-0 (pid 1) - Starting 1 monitor process
lightyear    | [ INFO ] main-0 (pid 1) - Starting 1 api_client process
lightyear    | [ INFO ] main-0 (pid 1) - Starting 4 validator process
lightyear    | [ INFO ] api-client-2 (pid 12) - Process started
lightyear    | [ INFO ] validator-3 (pid 16) - Process started
lightyear    | [ INFO ] validator-5 (pid 18) - Process started
lightyear    | [ INFO ] validator-6 (pid 19) - Process started
lightyear    | [ INFO ] main-0 (pid 1) - Starting 2 bigquery process
lightyear    | [ INFO ] validator-4 (pid 17) - Process started
lightyear    | [ INFO ] bigquery-8 (pid 24) - Process started
lightyear    | [ INFO ] bigquery-7 (pid 23) - Process started
lightyear    | [ INFO ] api-client-2 (pid 12) - 100 docs sent to queue_1
lightyear    | [ INFO ] monitor-1 (pid 8) - Queue sizes: queue_1=9, queue_2=1
lightyear    | [ INFO ] api-client-2 (pid 12) - 200 docs sent to queue_1
lightyear    | [ INFO ] bigquery-7 (pid 23) - 100 docs sent to bigquery
lightyear    | [ INFO ] api-client-2 (pid 12) - Process finished (34873 docs processed)
lightyear    | [ INFO ] main-0 (pid 1) - All api_client processes have finished
lightyear    | [ INFO ] validator-3 (pid 16) - Process finished (8471 docs processed)
lightyear    | [ INFO ] validator-5 (pid 18) - Process finished (8680 docs processed)
lightyear    | [ INFO ] monitor-1 (pid 8) - Queue sizes: queue_1=81, queue_2=7
...
lightyear    | [ INFO ] validator-4 (pid 17) - Process finished (8576 docs processed)
lightyear    | [ INFO ] validator-6 (pid 19) - Process finished (9146 docs processed)
lightyear    | [ INFO ] main-0 (pid 1) - All validator processes have finished
lightyear    | [ INFO ] monitor-1 (pid 8) - Queue sizes: queue_1=0, queue_2=1
lightyear    | [ INFO ] bigquery-7 (pid 23) - 17500 docs sent to bigquery
lightyear    | [ INFO ] bigquery-7 (pid 23) - Process finished (17500 docs processed)
lightyear    | [ INFO ] bigquery-8 (pid 24) - Process finished (17373 docs processed)
lightyear    | [ INFO ] main-0 (pid 1) - All bigquery processes have finished
lightyear exited with code 0
```
