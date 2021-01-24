FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

FROM python:3.8-alpine

RUN apk add --no-cache git curl libxml2-dev libxslt-dev libxml2 
ENV ENV prod
EXPOSE 80
WORKDIR /app

COPY ./pyproject.toml /app/

RUN apk add --update --no-cache --virtual .build-deps \
    g++ \
    py-lxml \
    python3-dev \
    musl-dev \
    gcc \
    build-base && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false && \
    cd /app/ && poetry install --no-root --no-dev && \
    apk --purge del .build-deps


COPY ./mealie /app
COPY --from=build-stage /app/dist /app/dist
RUN rm -rf /app/test /app/.temp


VOLUME [ "/app_data/" ]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

# ---------------------------------- #
# Old Docker File
# ---------------------------------- #

# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
# FROM mrnr91/uvicorn-gunicorn-fastapi:python3.8


# WORKDIR /app

# RUN apt-get update -y && \
#     apt-get install -y python-pip python-dev git curl python3-dev libxml2-dev libxslt1-dev zlib1g-dev --no-install-recommends && \
#     rm -rf /var/lib/apt/lists/* && \
#     curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
#     cd /usr/local/bin && \
#     ln -s /opt/poetry/bin/poetry && \
#     poetry config virtualenvs.create false

# COPY ./pyproject.toml /app/

# COPY ./mealie /app
# RUN poetry install --no-root --no-dev
# COPY --from=build-stage /app/dist /app/dist
# RUN rm -rf /app/test /app/.temp

# ENV ENV prod
# ENV APP_MODULE "app:app"

# VOLUME [ "/app/data" ]
