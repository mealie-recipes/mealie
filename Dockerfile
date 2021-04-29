# build
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

# run
FROM python:3.9-buster

ENV PRODUCTION true
ENV POETRY_VERSION 1.1.6

RUN apt-get update && apt-get install -y \
    apt-transport-https \
    debian-archive-keyring \
    debian-keyring \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | apt-key add - \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee -a /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update && apt-get install -y \
    caddy \
    && rm -rf /var/lib/apt/lists/*

# poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# database drivers
RUN pip install --no-cache-dir "psycopg2-binary==2.8.6"

# project dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

# project code
COPY ./mealie /app/mealie
COPY ./alembic /app/alembic
COPY alembic.ini /app
COPY ./Caddyfile /app
COPY ./dev/data/templates /app/data/templates

# frontend build
COPY --from=build-stage /app/dist /app/dist

VOLUME [ "/app/data/" ]

EXPOSE 80

CMD /app/mealie/run.sh
