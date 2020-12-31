# Akeneo Pipeline

![Akeneo Pipeline](./akeneo_pipeline.png "Akeneo Pipeline")

### BigQuery table

- `chb-prod-ingest-ecom.lightyear.akeneo`

### Command line options for Akeneo

```sh
$ python main.py akeneo --help
usage: lightyear akeneo [-h] [-a {faces,tryano}]

optional arguments:
  -h, --help            show this help message and exit
  -a {faces,tryano}, --account {faces,tryano}
                        the akeneo account
```

### Docker Composer run

```sh
$ docker-compose run lightyear python main.py akeneo --account=faces
Creating lightyear_lightyear_run ... done
[ INFO ] main-0 (pid 1) - Starting 1 monitor process
[ INFO ] main-0 (pid 1) - Starting 1 api_client process
[ INFO ] api_client-2 (pid 13) - Process started
[ INFO ] main-0 (pid 1) - Starting 4 validator process
[ INFO ] validator-3 (pid 17) - Process started
[ INFO ] validator-4 (pid 18) - Process started
[ INFO ] validator-5 (pid 19) - Process started
[ INFO ] validator-6 (pid 20) - Process started
[ INFO ] main-0 (pid 1) - Starting 2 bigquery process
[ INFO ] bigquery-7 (pid 24) - Process started
[ INFO ] bigquery-8 (pid 25) - Process started
[ INFO ] api_client-2 (pid 13) - 100 docs sent to queue_1
[ INFO ] api_client-2 (pid 13) - 200 docs sent to queue_1
[ INFO ] bigquery-7 (pid 24) - 100 docs sent to bigquery
[ INFO ] api_client-2 (pid 13) - 300 docs sent to queue_1
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=26, queue_2=23
...
[ INFO ] bigquery-8 (pid 25) - 2500 docs sent to bigquery
[ INFO ] api_client-2 (pid 13) - 5000 docs sent to queue_1
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=95, queue_2=0
...
[ INFO ] bigquery-7 (pid 24) - 17500 docs sent to bigquery
[ INFO ] bigquery-8 (pid 25) - 17300 docs sent to bigquery
[ INFO ] api_client-2 (pid 13) - 34887 docs sent to queue_1
[ INFO ] api_client-2 (pid 13) - Process finished (34887 docs processed)
[ INFO ] main-0 (pid 1) - All api_client processes have finished
[ INFO ] validator-6 (pid 20) - Process finished (9078 docs processed)
[ INFO ] validator-5 (pid 19) - Process finished (8432 docs processed)
[ INFO ] validator-4 (pid 18) - Process finished (8582 docs processed)
[ INFO ] validator-3 (pid 17) - Process finished (8795 docs processed)
[ INFO ] main-0 (pid 1) - All validator processes have finished
[ INFO ] bigquery-7 (pid 24) - Process finished (17504 docs processed)
[ INFO ] bigquery-8 (pid 25) - Process finished (17383 docs processed)
[ INFO ] main-0 (pid 1) - All bigquery processes have finished
```

### Parallel running processes

```sh
$ docker exec <container-id> /bin/bash -c 'ps fax'
  PID TTY      STAT   TIME COMMAND
    1 pts/0    Ss+    0:00 python main.py akeneo --account=faces
    9 pts/0    S+     0:00 python main.py akeneo --account=faces
   13 pts/0    Sl+    0:03 python main.py akeneo --account=faces
   17 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   18 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   19 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   20 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   24 pts/0    S+     0:00 python main.py akeneo --account=faces
   25 pts/0    S+     0:00 python main.py akeneo --account=faces
```
