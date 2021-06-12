FROM python:3.8-slim as build-stage
WORKDIR /app
RUN pip install --no-cache-dir mkdocs mkdocs-material
COPY . .
RUN mkdocs build

FROM caddy:alpine
WORKDIR /app
COPY ./Caddyfile /etc/caddy/Caddyfile
COPY --from=build-stage /app/site /srv