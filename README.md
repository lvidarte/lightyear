# Lightyear - Pipeline runner

Runs multiple parallel processes (fork) using queues as communication method.

## Common

```sh
$ python main.py --help
usage: lightyear [-h] [-l {error,warning,info,debug}] {akeneo} ...

Pipeline runner

positional arguments:
  {akeneo}

optional arguments:
  -h, --help            show this help message and exit
  -l {error,warning,info,debug}, --log-level {error,warning,info,debug}
                        error,warning,info,debug
```

## Requirements

- Python 3.8.5

## Python environment creation

```sh
python -m venv env
source env/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Python environment activation

```sh
source env/bin/activate
```

## Google Cloud credentials

```sh
export GCP_KEY_PATH={path-to-your-json-credentials-file}
```

## Docker run (currently runs a fixed command)

```sh
docker-compose up [--build]
```

## Check forked proceses in Docker container

```sh
docker exec lightyear /bin/bash -c 'ps fax'
```
