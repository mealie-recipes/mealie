###############################################
# Frontend Build
###############################################
FROM node:16 AS frontend-builder

WORKDIR /frontend

COPY frontend .

RUN yarn install \
    --prefer-offline \
    --frozen-lockfile \
    --non-interactive \
    --production=false \
    # https://github.com/docker/build-push-action/issues/471
    --network-timeout 1000000

RUN yarn generate

###############################################
# Base Image - Python
###############################################
FROM python:3.12-slim as python-base

ENV MEALIE_HOME="/app"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    VENV_PATH="/opt/mealie"

# prepend venv to path
ENV PATH="$VENV_PATH/bin:$PATH"

# create user account
RUN useradd -u 911 -U -d $MEALIE_HOME -s /bin/bash abc \
    && usermod -G users abc \
    && mkdir $MEALIE_HOME

###############################################
# Backend Package Build
###############################################
FROM python-base AS backend-builder
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

# prepend poetry to path
ENV PATH="$POETRY_HOME/bin:$PATH"

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=2.0.1
RUN curl -sSL https://install.python-poetry.org | python3 -

# install poetry plugins needed to build the package
RUN poetry self add "poetry-plugin-export>=1.9"

WORKDIR /mealie

# copy project files here to ensure they will be cached.
COPY poetry.lock pyproject.toml ./
COPY mealie ./mealie

# Copy frontend to package it into the wheel
COPY --from=frontend-builder /frontend/dist ./mealie/frontend

# Build the source and binary package
RUN poetry build --output=dist

# Create the requirements file, which is used to install the built package and
# its pinned dependencies later. mealie is included to ensure the built one is
# what's installed.
RUN export MEALIE_VERSION=$(poetry version --short) \
    && poetry export --only=main --extras=pgsql --output=dist/requirements.txt \
    && echo "mealie[pgsql]==$MEALIE_VERSION \\" >> dist/requirements.txt \
    && poetry run pip hash dist/mealie-$MEALIE_VERSION-py3-none-any.whl | tail -n1 | tr -d '\n' >> dist/requirements.txt \
    && echo " \\" >> dist/requirements.txt \
    && poetry run pip hash dist/mealie-$MEALIE_VERSION.tar.gz | tail -n1 >> dist/requirements.txt

###############################################
# Package Container
# Only role is to hold the packages, or be overriden by a --build-context flag.
###############################################
FROM scratch AS packages
COPY --from=backend-builder /mealie/dist /

###############################################
# Python Virtual Environment Build
###############################################
# Install packages required to build the venv, in parallel to building the wheel
FROM python-base AS venv-builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    libwebp-dev \
    # LDAP Dependencies
    libsasl2-dev libldap2-dev libssl-dev \
    gnupg gnupg2 gnupg1 \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv --upgrade-deps $VENV_PATH

# Install the wheel and all dependencies into the venv
FROM venv-builder-base AS venv-builder

# Copy built package (wheel) and its dependency requirements
COPY --from=packages * /dist/

# Install the wheel with exact versions of dependencies into the venv
RUN . $VENV_PATH/bin/activate \
    && pip install --require-hashes -r /dist/requirements.txt --find-links /dist

###############################################
# CRFPP Image
###############################################
FROM hkotel/crfpp as crfpp

RUN echo "crfpp-container"

###############################################
# Production Image
###############################################
FROM python-base as production
LABEL org.opencontainers.image.source="https://github.com/mealie-recipes/mealie"
ENV PRODUCTION=true
ENV TESTING=false

ARG COMMIT
ENV GIT_COMMIT_HASH=$COMMIT

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    gosu \
    iproute2 \
    libldap-common \
    libldap-2.5 \
    && rm -rf /var/lib/apt/lists/*

# create directory used for Docker Secrets
RUN mkdir -p /run/secrets

# copy CRF++ and add it to the library path
ENV LD_LIBRARY_PATH=/usr/local/lib
COPY --from=crfpp /usr/local/lib/ /usr/local/lib
COPY --from=crfpp /usr/local/bin/crf_learn /usr/local/bin/crf_learn
COPY --from=crfpp /usr/local/bin/crf_test /usr/local/bin/crf_test

# Copy venv into image. It contains a fully-installed mealie backend and frontend.
COPY --from=venv-builder $VENV_PATH $VENV_PATH


# Grab CRF++ Model Release
RUN python -m mealie.scripts.install_model

VOLUME [ "$MEALIE_HOME/data/" ]
ENV APP_PORT=9000

EXPOSE ${APP_PORT}

HEALTHCHECK CMD python -m mealie.scripts.healthcheck || exit 1

ENV HOST 0.0.0.0

EXPOSE ${APP_PORT}
COPY ./docker/entry.sh $MEALIE_HOME/run.sh

RUN chmod +x $MEALIE_HOME/run.sh
ENTRYPOINT ["/app/run.sh"]
