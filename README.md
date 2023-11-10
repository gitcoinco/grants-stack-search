## Installation

```sh
$ git clone https://github.com/gitcoinco/search
$ cd search
$ poetry install
```

**Note**: installation might currently be broken on some systems, see https://github.com/python-poetry/poetry/issues/8458 for workarounds.

## Dev setup

Copy `.env.example` to `.env` and customize it.

## Production setup

Customize env variables in `fly.production.toml`.

## Run service

```sh
poetry run task run
```

Useful URLs:

- a UI testbed http://localhost:8000/static/index.html
- API docs: http://localhost:8000/docs

## Run tests

One-shot:

```sh
poetry run task test
```

With file watching:

```sh
poetry run task test_watch
```

## Build and deploy

Build locally:

```sh
$ docker buildx build . --platform=linux/amd64 -t gitcoin-search
```

Build and deploy to Fly:

```sh
$ fly -c fly.production.toml deploy
```
