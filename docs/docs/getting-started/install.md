# Installation
To deploy docker on your local network it is highly recommended to use docker to deploy the image straight from dockerhub. Using the docker-compose below you should be able to get a stack up and running easily by changing a few default values and deploying. Currently MongoDB and SQLite are supported. MongoDB support will be dropped in v0.2.0 so it is recommended to go with SQLite for new deployments. Postrgres support is planned, however for most loads you may find SQLite performant enough for most use cases.  


[Get Docker](https://docs.docker.com/get-docker/)

[Mealie Docker Image](https://hub.docker.com/r/hkotel/mealie)


## Quick Start - Docker CLI
Deployment with the Docker CLI can be done with `docker run` and specify the database type, in this case `sqlite`, setting the exposed port `9000`, mounting the current directory, and pull the latest image. After the image is up an running you can navigate to http://your.ip.addres:9000 and you'll should see mealie up and running!

```shell
docker run \
    -e db_type='sqlite' \
    -p 9000:80 \
    -v `pwd`:'/app_data/' \
    hkotel/mealie:latest

```

## Docker Compose with SQLite
Deployment with docker-compose is the recommended method for deployment. The example below will create an instance of mealie available on port `9000` with the data volume mounted from the local directory. To use, create a docker-compose.yml file, paste the contents below and save. In the terminal run `docker-compose up -d` to start the container. 

```yaml
version: "3.1"
services:
  mealie:
    container_name: mealie
    image: hkotel/mealie:latest
    restart: always
    ports:
      - 9000:80
    environment:
      db_type: sqlite
      TZ: America/Anchorage
    volumes:
      - ./mealie/data/:/app_data

```

## Env Variables

| Variables   | default | description                                                                                                                                             |
| ----------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| db_type     | sqlite  | The database type to be used. Current Options 'sqlite'                                                                                                  |
| mealie_port | 9000    | The port exposed by mealie. **do not change this if you're running in docker** If you'd like to use another port, map 9000 to another port of the host. |
| api_docs    | True    | Turns on/off access to the API documentation locally.                                                                                                   |
| TZ          |         | You should set your time zone accordingly so the date/time features work correctly                                                                      |


## Deployed as a Python Application
Alternatively, this project is built on Python and SQLite. If you are dead set on deploying on a linux machine you can run this in an python virtual env. Provided that you know thats how you want to host the application, I'll assume you know how to do that. I may or may not get around to writing this guide. I'm open to pull requests if anyone has a good guide on it. 
