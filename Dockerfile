FROM python:3.11-bookworm as builder

RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.11-slim-bookworm as runtime
RUN apt-get update && apt-get install -y wget && apt-get clean

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
COPY src ./src
COPY static ./static

ARG IPFS_GATEWAY=https://d16c97c2np8a2o.cloudfront.net/
ARG PROJECTS_JSON_URL=https://indexer-staging.fly.dev/data/1/projects.json
RUN wget -O /tmp/projects.json $PROJECTS_JSON_URL

ENV IPFS_GATEWAY=$IPFS_GATEWAY
ENV PROJECTS_JSON_PATH=/tmp/projects.json
CMD ["/bin/bash", "-c", "uvicorn --host 0.0.0.0 --port $PORT src.app:app"]


