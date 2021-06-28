# build
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build


FROM python:3.9-slim-buster

ENV PRODUCTION true
ENV POETRY_VERSION 1.1.6


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    curl \
    gnupg gnupg2 gnupg1  \
    apt-transport-https \
    debian-archive-keyring \
    debian-keyring \
    libpq-dev \
    libwebp-dev \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | apt-key add - \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee -a /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    caddy \
    && apt autoremove \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get remove -y apt-transport-https debian-keyring g++ gnupg gnupg2 gnupg1 


RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# project dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false
RUN poetry install -E pgsql --no-dev --no-interaction --no-ansi

COPY ./mealie /app/mealie
RUN poetry config virtualenvs.create false \
    && poetry install -E pgsql --no-dev

#! Future
# COPY ./alembic /app
# COPY alembic.ini /app
COPY ./Caddyfile /app
COPY ./dev/data/templates /app/data/templates

# frontend build
COPY --from=build-stage /app/dist /app/dist

VOLUME [ "/app/data/" ]

EXPOSE 80

HEALTHCHECK CMD curl -f http://localhost || exit 1

CMD /app/mealie/run.sh
