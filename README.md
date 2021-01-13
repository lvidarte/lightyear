# Lightyear - Pipeline runner

Run N multiple parallel processes ([fork](https://en.wikipedia.org/wiki/Fork_(system_call))) using queues as communication method.

Lightyear is flexible: you can create N kinds of different processes, launch N instances for each of them, and create N queues for communication.


### Pipelines

- [Akeneo Pipeline](https://gitlab.com/chalhoub-data/lightyear/-/tree/master/lightyear/clients/akeneo)
- [Brandquad Pipeline](https://gitlab.com/chalhoub-data/lightyear/-/tree/master/lightyear/clients/brandquad)
- [RetailNext Pipeline](https://gitlab.com/chalhoub-data/lightyear/-/tree/master/lightyear/clients/retailnext)

### Command Line Interface

```sh
$ python main.py --help
usage: lightyear [-h] [-l {error,warning,info,debug}] [-d] {akeneo,brandquad,retailnext} ...

Pipeline runner

positional arguments:
  {akeneo,brandquad,retailnext}

optional arguments:
  -h, --help            show this help message and exit
  -l {error,warning,info,debug}, --log-level {error,warning,info,debug}
                        set the logging level (default: info)
  -d, --dummy           avoid bigquery insertion
```

## Development

### Requirements

- Python 3.8.5

### Python environment creation

```sh
python -m venv env
source env/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Python environment activation

```sh
source env/bin/activate
```

### Google Cloud credentials

```sh
export GOOGLE_APPLICATION_CREDENTIALS={path-to-your-json-credentials-file}
```

### Docker run

```sh
docker-compose build
docker-compose run lightyear
```

### Check forked proceses in Docker container

```sh
 docker exec <container-id> /bin/bash -c 'ps fax'
```
