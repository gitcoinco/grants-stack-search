## Installation

```sh
$ git clone https://github.com/gitcoinco/search
$ cd search
$ poetry install
```

**Note**: installation might currently be broken on some systems, see https://github.com/python-poetry/poetry/issues/8458 for workarounds.

## Setup

Download data for a given combination of chain and round IDs:

```sh
$ APPLICATIONS_DOWNLOADER_DOWNLOAD_DIR=.var/applications-by-round \
  APPLICATIONS_DOWNLOADER_CHAIN_ID=10 \
  APPLICATIONS_DOWNLOADER_ROUND_IDS=0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871,0xc5FdF5cFf79e92FAc1d6Efa725c319248D279200,0x9331FDe4Db7b9d9d1498C09d30149929f24cF9D5,0xb6Be0eCAfDb66DD848B0480db40056Ff94A9465d,0x2871742B184633f8DC8546c6301cbC209945033e,0x8de918F0163b2021839A8D84954dD7E8e151326D \
  poetry run task download_applications
```

Copy `.env.example` to `.env` and edit `.env` so that `APPLICATIONS_DIR` points to where you downloaded applications files.

## Run service

```sh
poetry run task watch_run_app
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
$ fly deploy
```

Inspect the Dockerfile to see what build arguments are available to customize the build. E.g. to specify a different set of rounds:

```sh
$ fly deploy --build-arg APPLICATIONS_DOWNLOADER_ROUND_IDS=0x123,0x456,0x789
```
