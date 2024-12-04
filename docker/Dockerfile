FROM node:16 as builder

WORKDIR /app

COPY ./frontend .

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
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# create user account
RUN useradd -u 911 -U -d $MEALIE_HOME -s /bin/bash abc \
    && usermod -G users abc \
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
    # LDAP Dependencies
    libsasl2-dev libldap2-dev libssl-dev \
    gnupg gnupg2 gnupg1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -U --no-cache-dir pip

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.3.1
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install -E pgsql --only main

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

# copying poetry and venv into image
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

ENV LD_LIBRARY_PATH=/usr/local/lib
COPY --from=crfpp /usr/local/lib/ /usr/local/lib
COPY --from=crfpp /usr/local/bin/crf_learn /usr/local/bin/crf_learn
COPY --from=crfpp /usr/local/bin/crf_test /usr/local/bin/crf_test

# copy backend
COPY ./mealie $MEALIE_HOME/mealie
COPY ./poetry.lock ./pyproject.toml $MEALIE_HOME/

# venv already has runtime deps installed we get a quicker install
WORKDIR $MEALIE_HOME
RUN . $VENV_PATH/bin/activate && poetry install -E pgsql --only main
WORKDIR /

# Grab CRF++ Model Release
RUN python $MEALIE_HOME/mealie/scripts/install_model.py

VOLUME [ "$MEALIE_HOME/data/" ]
ENV APP_PORT=9000

EXPOSE ${APP_PORT}

HEALTHCHECK CMD python $MEALIE_HOME/mealie/scripts/healthcheck.py || exit 1

# ----------------------------------
# Copy Frontend

ENV STATIC_FILES=/spa/static
COPY --from=builder /app/dist  ${STATIC_FILES}

ENV HOST 0.0.0.0

EXPOSE ${APP_PORT}
COPY ./docker/entry.sh $MEALIE_HOME/run.sh

RUN chmod +x $MEALIE_HOME/run.sh
ENTRYPOINT ["/app/run.sh"]
