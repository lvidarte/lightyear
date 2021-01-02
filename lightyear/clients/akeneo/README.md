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
[ INFO ] api_client-2 (pid 14) - Process started
[ INFO ] main-0 (pid 1) - Starting 4 formatter process
[ INFO ] formatter-3 (pid 18) - Process started
[ INFO ] formatter-4 (pid 19) - Process started
[ INFO ] main-0 (pid 1) - Starting 4 validator process
[ INFO ] formatter-5 (pid 20) - Process started
[ INFO ] formatter-6 (pid 21) - Process started
[ INFO ] validator-8 (pid 26) - Process started
[ INFO ] validator-7 (pid 25) - Process started
[ INFO ] validator-10 (pid 28) - Process started
[ INFO ] main-0 (pid 1) - Starting 2 bigquery process
[ INFO ] validator-9 (pid 27) - Process started
[ INFO ] bigquery-11 (pid 32) - Process started
[ INFO ] bigquery-12 (pid 33) - Process started
...
[ INFO ] api_client-2 (pid 14) - 100 docs sent to queue_1
[ INFO ] validator-10 (pid 28) - 7200 docs sent to queue_3
[ INFO ] bigquery-11 (pid 32) - 15100 docs sent to bigquery
[ INFO ] bigquery-12 (pid 33) - 14000 docs sent to bigquery
[ INFO ] api_client-2 (pid 14) - 29200 docs sent to queue_1
[ INFO ] formatter-6 (pid 21) - 7300 docs sent to queue_2
[ INFO ] formatter-3 (pid 18) - 7600 docs sent to queue_2
[ INFO ] validator-7 (pid 25) - 7300 docs sent to queue_3
[ INFO ] bigquery-12 (pid 33) - 14100 docs sent to bigquery
[ INFO ] api_client-2 (pid 14) - 29300 docs sent to queue_1
[ INFO ] formatter-5 (pid 20) - 7300 docs sent to queue_2
[ INFO ] validator-10 (pid 28) - 7300 docs sent to queue_3
[ INFO ] api_client-2 (pid 14) - 29400 docs sent to queue_1
[ INFO ] monitor-1 (pid 10) - Queue sizes: queue_1=30, queue_2=38, queue_3=9
[ INFO ] bigquery-11 (pid 32) - 15200 docs sent to bigquery
...
[ INFO ] monitor-1 (pid 10) - Queue sizes: queue_1=77, queue_2=6, queue_3=1
[ INFO ] bigquery-12 (pid 33) - 16700 docs sent to bigquery
[ INFO ] api_client-2 (pid 14) - Process finished (34897 docs processed)
[ INFO ] validator-7 (pid 25) - 8700 docs sent to queue_3
[ INFO ] bigquery-11 (pid 32) - 18000 docs sent to bigquery
[ INFO ] formatter-4 (pid 19) - 8500 docs sent to queue_2
[ INFO ] validator-8 (pid 26) - 8300 docs sent to queue_3
[ INFO ] main-0 (pid 1) - All api_client processes have finished
[ INFO ] formatter-5 (pid 20) - Process finished (8544 docs processed)
[ INFO ] formatter-3 (pid 18) - Process finished (9077 docs processed)
[ INFO ] formatter-6 (pid 21) - Process finished (8775 docs processed)
[ INFO ] formatter-4 (pid 19) - Process finished (8501 docs processed)
[ INFO ] main-0 (pid 1) - All formatter processes have finished
[ INFO ] validator-8 (pid 26) - Process finished (8300 docs processed)
[ INFO ] validator-10 (pid 28) - Process finished (8658 docs processed)
[ INFO ] validator-9 (pid 27) - Process finished (9225 docs processed)
[ INFO ] validator-7 (pid 25) - Process finished (8714 docs processed)
[ INFO ] main-0 (pid 1) - All validator processes have finished
[ INFO ] bigquery-11 (pid 32) - Process finished (18015 docs processed)
[ INFO ] bigquery-12 (pid 33) - Process finished (16882 docs processed)
[ INFO ] main-0 (pid 1) - All bigquery processes have finished
```

### Parallel running processes

```sh
$ docker exec <container-id> /bin/bash -c 'ps fax'
  PID TTY      STAT   TIME COMMAND
    1 pts/0    Ss+    0:00 python main.py akeneo --account=faces
   10 pts/0    S+     0:00 python main.py akeneo --account=faces
   14 pts/0    Sl+    0:02 python main.py akeneo --account=faces
   18 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   19 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   20 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   21 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   25 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   26 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   27 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   28 pts/0    Sl+    0:00 python main.py akeneo --account=faces
   32 pts/0    S+     0:00 python main.py akeneo --account=faces
   33 pts/0    S+     0:00 python main.py akeneo --account=faces
```
