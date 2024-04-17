## Installation

```sh
$ git clone https://github.com/gitcoinco/search
$ cd search
$ poetry install
```

**Note**: installation might currently be broken on some systems, see https://github.com/python-poetry/poetry/issues/8458 for workarounds.

## Development

Copy `.env.example` to `.env` and customize it.

Run:

```sh
poetry run task dev
```

Useful URLs:

- a UI testbed http://localhost:8000/static/index.html
- API docs: http://localhost:8000/docs

Run tests one-shot:

```sh
poetry run task test
```

Run tests continuously:

```sh
poetry run task test_watch
```

Build locally:

```sh
$ docker buildx build . --platform=linux/amd64 -t gitcoin-search
```

## Production

Run local production build:

```sh
poetry install --without dev --no-root && rm -rf /tmp/poetry_cache   
```

Customize env variables in `fly.production.toml`.

Build and deploy to Fly:

```sh
$ fly -c fly.production.toml deploy
```
