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
FROM python:3.9.6-slim as python-base

ENV MEALIE_HOME="/app"

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

ENV PUID=911 \
    PGID=911

# create user account with default group
RUN groupadd -g $PGID mealie \
    && useradd -u $PUID  -g $PGID -d $MEALIE_HOME -s /bin/bash mealie \
    && mkdir $MEALIE_HOME

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
    && pip install -U --no-cache-dir pip

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.1.7
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install -E pgsql --no-dev

###############################################
# Development Image
###############################################
FROM python-base as development
ENV PRODUCTION=false

# copying poetry and venv into image
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# copy backend
COPY ./mealie $MEALIE_HOME/mealie
COPY ./poetry.lock ./pyproject.toml $MEALIE_HOME/

#! Future
# COPY ./alembic ./alembic.ini $MEALIE_HOME/

# venv already has runtime deps installed we get a quicker install
WORKDIR $MEALIE_HOME
RUN . $VENV_PATH/bin/activate && poetry install
WORKDIR /

RUN chmod +x $MEALIE_HOME/mealie/run.sh
ENTRYPOINT $MEALIE_HOME/mealie/run.sh "reload"

###############################################
# Production Image
###############################################
FROM python-base as production
ENV PRODUCTION=true
ARG DEBIAN_FRONTEND=noninteractive

# curl for used by healthcheck
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

# copying poetry and venv into image
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# copying caddy into image
COPY --from=builder-base /usr/bin/caddy /usr/bin/caddy

# copy backend
COPY ./mealie $MEALIE_HOME/mealie
COPY ./poetry.lock ./pyproject.toml $MEALIE_HOME/
COPY ./gunicorn_conf.py $MEALIE_HOME

#! Future
# COPY ./alembic ./alembic.ini $MEALIE_HOME/

# venv already has runtime deps installed we get a quicker install
WORKDIR $MEALIE_HOME
RUN . $VENV_PATH/bin/activate && poetry install -E pgsql --no-dev
WORKDIR /

# copy frontend
COPY --from=frontend-build /app/dist $MEALIE_HOME/dist
COPY ./dev/data/templates $MEALIE_HOME/data/templates
COPY ./Caddyfile $MEALIE_HOME
RUN mkdir /app/temp

RUN id -u mealie | xargs -I{} chown -R {}:{} $MEALIE_HOME
USER $PUID:$PGID
VOLUME [ "$MEALIE_HOME/data/" ]
ENV APP_PORT=9080

EXPOSE ${APP_PORT}

HEALTHCHECK CMD curl -f http://localhost:${APP_PORT} || exit 1

RUN chmod +x $MEALIE_HOME/mealie/run.sh
ENTRYPOINT $MEALIE_HOME/mealie/run.sh
