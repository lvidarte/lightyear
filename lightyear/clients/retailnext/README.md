# RetailNext Pipeline

![RetailNext Pipeline](./retailnext_pipeline.png "RetailNext Pipeline")

### BigQuery table

- `chb-prod-ingest-ecom.lightyear.retailnext`

### Command line options for RetailNext

```sh
$ python main.py retailnext --help
usage: lightyear retailnext [-h]

optional arguments:
  -h, --help  show this help message and exit
```

### Docker Composer run

```sh
$ docker-compose run lightyear python main.py retailnext
Creating lightyear_lightyear_run ... done
[ INFO ] main-0 (pid 1) - Starting 1 monitor process
[ INFO ] main-0 (pid 1) - Starting 1 api_client_location process
[ INFO ] api_client_location-2 (pid 13) - Process started
[ INFO ] main-0 (pid 1) - Starting 4 api_client_datamine process
[ INFO ] api_client_datamine-3 (pid 17) - Process started
[ INFO ] api_client_datamine-4 (pid 18) - Process started
[ INFO ] api_client_datamine-5 (pid 19) - Process started
[ INFO ] main-0 (pid 1) - Starting 2 bigquery process
[ INFO ] api_client_datamine-6 (pid 20) - Process started
[ INFO ] bigquery-7 (pid 24) - Process started
[ INFO ] bigquery-8 (pid 25) - Process started
[ INFO ] api_client_datamine-3 (pid 17) - Getting metrics for location Swarovski
[ INFO ] api_client_datamine-4 (pid 18) - Getting metrics for location UAE
[ INFO ] api_client_datamine-5 (pid 19) - Getting metrics for location KSA
[ INFO ] api_client_datamine-6 (pid 20) - Getting metrics for location Qatar
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=46, queue_2=0
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=46, queue_2=0
[ INFO ] api_client_datamine-6 (pid 20) - Getting metrics for location Kuwait
[ INFO ] api_client_datamine-4 (pid 18) - Getting metrics for location Abu Dhabi
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=94, queue_2=0
[ INFO ] api_client_datamine-3 (pid 17) - Getting metrics for location Dubai
[ INFO ] api_client_datamine-5 (pid 19) - Getting metrics for location Al Ain
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=92, queue_2=0
[ INFO ] api_client_datamine-6 (pid 20) - Getting metrics for location Riyad
[ INFO ] api_client_datamine-4 (pid 18) - Getting metrics for location Jeddah
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=131, queue_2=0
[ INFO ] api_client_datamine-6 (pid 20) - Getting metrics for location SWAROVSKI @ Hamra Mall
[ INFO ] api_client_datamine-4 (pid 18) - Getting metrics for location SWAROVSKI @ Hayatt Mall
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=129, queue_2=0
[ INFO ] api_client_datamine-3 (pid 17) - Getting metrics for location SWAROVSKI @ Nakheel Mall
[ INFO ] api_client_datamine-5 (pid 19) - Getting metrics for location SWAROVSKI @ Riyadh Park
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=127, queue_2=0
[ INFO ] api_client_datamine-6 (pid 20) - Getting metrics for location SWAROVSKI @ Riyadh Gallery
[ INFO ] api_client_datamine-4 (pid 18) - Getting metrics for location SWAROVSKI @ Kingdom Center
...
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=33, queue_2=0
[ INFO ] api_client_datamine-3 (pid 17) - Getting metrics for location SWAROVSKI @ Nakheel Dammam
[ INFO ] api_client_datamine-4 (pid 18) - Getting metrics for location Swarovski @ Al Maryah Central
[ INFO ] api_client_datamine-5 (pid 19) - Getting metrics for location Al Qassim
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=27, queue_2=0
[ INFO ] api_client_datamine-6 (pid 20) - Getting metrics for location SWAROVSKI @ Nakheel Plaza Qassim
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=25, queue_2=0
[ INFO ] api_client_datamine-5 (pid 19) - Getting metrics for location SWAROVSKI @ Faisaliya
[ INFO ] api_client_datamine-4 (pid 18) - Getting metrics for location ECOMMERCE - KSA
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=21, queue_2=0
[ INFO ] api_client_datamine-4 (pid 18) - Process finished (40 docs processed)
[ INFO ] api_client_datamine-6 (pid 20) - Process finished (40 docs processed)
[ INFO ] monitor-1 (pid 9) - Queue sizes: queue_1=1, queue_2=0
[ INFO ] api_client_datamine-3 (pid 17) - Process finished (40 docs processed)
[ INFO ] main-0 (pid 1) - All api_client_datamine processes have finished
[ INFO ] bigquery-7 (pid 24) - Process finished (67 docs processed)
[ INFO ] bigquery-8 (pid 25) - Process finished (92 docs processed)
[ INFO ] main-0 (pid 1) - All bigquery processes have finished
```

### Parallel running processes

```sh
$ docker exec <container-id> /bin/bash -c 'ps fax'
  PID TTY      STAT   TIME COMMAND
    1 ?        Ss     0:00 python main.py retailnext
    9 ?        S      0:00 python main.py retailnext
   13 ?        Sl     0:00 python main.py retailnext
   17 ?        Sl     0:00 python main.py retailnext
   18 ?        Sl     0:00 python main.py retailnext
   19 ?        Sl     0:00 python main.py retailnext
   20 ?        Sl     0:00 python main.py retailnext
   24 ?        S      0:00 python main.py retailnext
   25 ?        S      0:00 python main.py retailnext
```
