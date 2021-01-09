FROM node:lts-alpine as build-stage
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY ./mealie /app
COPY ./mealie/data/templates/recipes.md /app/data/templates/recipes.md
COPY --from=build-stage /app/dist /app/dist
RUN rm -rf /app/test /app/temp

ENV ENV prod

VOLUME [ "/app/data" ]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]