# RetailNext Pipeline

![RetailNext Pipeline](./retailnext_pipeline.png "RetailNext Pipeline")

### BigQuery table

- `chb-prod-ingest-ecom.lightyear.retailnext`

### Command line options for RetailNext

```sh
$ python main.py retailnext --help
usage: lightyear retailnext [-h]

optional arguments:
  -h, --help            show this help message and exit
```

### Parallel running processes

```sh
$ docker exec lightyear /bin/bash -c 'ps fax'
  PID TTY      STAT   TIME COMMAND
    1 ?        Ss     0:00 python main.py retailnext
    8 ?        S      0:00 python main.py retailnext
   12 ?        Sl     0:00 python main.py retailnext
   16 ?        Sl     0:00 python main.py retailnext
   17 ?        Sl     0:00 python main.py retailnext
   18 ?        Sl     0:00 python main.py retailnext
   19 ?        Sl     0:00 python main.py retailnext
   23 ?        S      0:00 python main.py retailnext
   24 ?        S      0:00 python main.py retailnext
```
