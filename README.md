# Lightyear - Pipeline runner

Runs multiple parallel processes (fork) using queues as communication method.

### Pipelines

- [Akeneo Pipeline](https://gitlab.com/chalhoub-data/lightyear/-/tree/master/lightyear/clients/akeneo)
- [RetailNext Pipeline](https://gitlab.com/chalhoub-data/lightyear/-/tree/master/lightyear/clients/retailnext)

### Command Line Interface

```sh
$ python main.py --help
usage: lightyear [-h] [-l {error,warning,info,debug}] {akeneo,retailnext} ...

Pipeline runner

positional arguments:
  {akeneo,retailnext}

optional arguments:
  -h, --help            show this help message and exit
  -l {error,warning,info,debug}, --log-level {error,warning,info,debug}
                        error,warning,info,debug
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

### Docker run (currently runs a fixed command)

```sh
docker-compose up [--build]
```

### Check forked proceses in Docker container

```sh
 docker exec lightyear /bin/bash -c 'ps fax'
```
