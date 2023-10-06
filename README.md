## Installation

```sh
$ git clone https://github.com/gitcoinco/search-spike
$ cd search-spike
$ poetry install
```

## Setup

Copy `.env.example` to `.env`, then download `projects.json` and set the `PROJECTS_JSON_PATH` accordingly:

```sh
$ cp .env.example .env
$ wget -O /tmp/projects.json https://indexer-staging.fly.dev/data/1/projects.json
$ echo 'PROJECTS_JSON_PATH=/tmp/projects.json' >>.env
```

## Run service and web UI:

```sh
poetry run task watch_run_app
```

Then open http://localhost:8000/static/index.html

## Run experiments

We're (ab)using pytest as a testbed for experiments with hot reload. (Use `@pytest.mark.only` and `@pytest.mark.skip` to switch experiments on and off.)

```sh
poetry run task test_watch
```

Experiments other than the search based on Chroma DB may be out of date.
