FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

FROM python:3.9-alpine

RUN apk add --no-cache  libxml2-dev libxslt-dev libxml2 caddy
ENV ENV prod
EXPOSE 80
WORKDIR /app

COPY ./pyproject.toml /app/

RUN apk add --update --no-cache --virtual .build-deps \
    curl \
    g++ \
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
COPY ./Caddyfile /app
COPY --from=build-stage /app/dist /app/dist
RUN rm -rf /app/test /app/.temp
RUN chmod +x run.sh

VOLUME [ "/app/data/" ]
ENTRYPOINT ["/app/run.sh"]
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
