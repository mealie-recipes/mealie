###############################################
# Frontend Builder Image
###############################################
FROM node:lts-alpine as frontend-build
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

###############################################
# Base Image
###############################################
FROM python:3.9-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Builder Image
###############################################
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    libpq-dev \
    libwebp-dev \
    gnupg gnupg2 gnupg1 \
    debian-keyring \
    debian-archive-keyring \
    apt-transport-https \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | apt-key add - \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    caddy \
    && pip install -U pip

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.1.6
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install -E pgsql --no-dev

###############################################
# Production Image
###############################################
FROM python-base as production
ENV PRODUCTION=true

# copying poetry and venv into image
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# copying caddy into image
COPY --from=builder-base /usr/bin/caddy /usr/bin/caddy

WORKDIR /app

# copy backend
COPY ./mealie ./mealie
COPY ./poetry.lock ./pyproject.toml ./

# venv already has runtime deps installed we get a quicker install
# WORKDIR $PYSETUP_PATH
RUN . $VENV_PATH/bin/activate && poetry install -E pgsql --no-dev

# copy frontend
COPY --from=frontend-build /app/dist ./dist
COPY ./dev/data/templates ./data/templates
COPY ./Caddyfile ./

#! Future
# COPY ./alembic ./
# COPY ./alembic.ini ./

VOLUME [ "/app/data/" ]

EXPOSE 80

RUN chmod +x ./mealie/run.sh
ENTRYPOINT ./mealie/run.sh
