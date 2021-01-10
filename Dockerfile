FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -r requirements.txt 

COPY ./mealie /app
COPY --from=build-stage /app/dist /app/dist
RUN rm -rf /app/test /app/temp

ENV ENV prod
ENV APP_MODULE "app:app"

VOLUME [ "/app/data" ]
