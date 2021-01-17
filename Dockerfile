FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim


WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev git curl --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./app/poetry.lock* /app/

COPY ./mealie /app
RUN poetry install --no-root --no-dev
COPY --from=build-stage /app/dist /app/dist
RUN rm -rf /app/test /app/.temp

ENV ENV prod
ENV APP_MODULE "app:app"

VOLUME [ "/app/data" ]
