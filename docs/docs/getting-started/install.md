# Installation
To deploy docker on your local network it is highly recommended to use docker to deploy the image straight from dockerhub. Using the docker-compose below you should be able to get a stack up and running easily by changing a few default values and deploying. Currently the only supported database is Mongo. Mealie is looking for contributors to support additional databases. 


[Get Docker](https://docs.docker.com/get-docker/)

[Mealie Docker Image](https://hub.docker.com/r/hkotel/mealie)

## Env Variables

| Variables      | default | description                                                                                                                                             |
| -------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| mealie_db_name | mealie  | The name of the database to be created in Mongodb                                                                                                       |
| mealie_port    | 9000    | The port exposed by mealie. **do not change this if you're running in docker** If you'd like to use another port, map 9000 to another port of the host. |
| db_username    | root    | The Mongodb username you specified in your mongo container                                                                                              |
| db_password    | example | The Mongodb password you specified in your mongo container                                                                                              |
| db_host        | mongo   | The host address of MongoDB if you're in docker and using the same network you can use mongo as the host name                                           |
| db_port        | 27017   | the port to access MongoDB 27017 is the default for mongo                                                                                               |
| TZ             |         | You should set your time zone accordingly so the date/time features work correctly                                                                      |


## Docker Compose

```yaml
# docker-compose.yml
version: "3.1"
services:
  mealie:
    container_name: mealie
    image: hkotel/mealie:latest
    restart: always
    ports:
      - 9000:9000
    environment:
      db_username: root     # Your Mongo DB Username - Please Change
      db_password: example  # Your Mongo DB Password - Please Change
      db_host: mongo
      db_port: 27017    # The Default port for Mongo DB
      TZ: America/Anchorage
    volumes:
      - ./mealie/data/:/app/data/
      
  mongo:
    image: mongo
    restart: always
    volumes:
    - ./mongo:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: root  # Change!
      MONGO_INITDB_ROOT_PASSWORD: example   # Change!

  mongo-express: # Optional Mongo GUI
    image: mongo-express
    restart: always
    ports:
      - 9091:8081
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: root
      ME_CONFIG_MONGODB_ADMINPASSWORD: example

```

## Ansible Tasks Template

```yaml
- name: ensures Mealie directory dir exists
  file:
    path: "{{ docker_dir }}/mealie/"
    state: directory
    owner: "{{ main_user}}"
    group: "{{ main_group }}"

- name: ensures Mealie directory dir exists
  file:
    path: "{{ docker_dir }}/mealie/"
    state: directory
    owner: "{{ main_user}}"
    group: "{{ main_group }}"

- name: Deploy Monogo Database
  docker_container:
    name: mealie-mongo
    image: mongo
    restart_policy: unless-stopped
    networks:
      - name: web
    env:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: example


- name: deploy Mealie Docker Container
  docker_container:
    name: mealie
    image: hkotel/mealie:latest
    restart_policy: unless-stopped
    ports:
      - 9090:9000
    networks:
      - name: web
    mounts:
      - type: bind
        source: "{{ docker_dir }}/mealie"
        target: /app/data
    env:
      db_username: root
      db_password: example
      db_host: mealie-mongo
      db_port: "27017"

```

## Deployed as a Python Application
Alternatively, this project is built on Python and Mongodb. If you are dead set on deploying on a linux machine you can run this in an python environment with a dedicated MongoDatabase. Provided that you know thats how you want to host the application, I'll assume you know how to do that. I may or may not get around to writing this guide. I'm open to pull requests if anyone has a good guide on it. 