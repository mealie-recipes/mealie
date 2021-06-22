# Installation
To deploy mealie on your local network it is highly recommended to use docker to deploy the image straight from dockerhub. Using the docker-compose below you should be able to get a stack up and running easily by changing a few default values and deploying. You can deploy with either SQLite (default) or Postgres. SQLite is sufficient for most use cases. Additionally, with mealies automated backup and restore functionality, you can easily move between SQLite and Postgres as you wish. 


[Get Docker](https://docs.docker.com/get-docker/){:target="_blank"}

[Mealie on Dockerhub](https://hub.docker.com/r/hkotel/mealie){:target="_blank"}

 - linux/amd64 
 - linux/arm64


## Quick Start - Docker CLI
Deployment with the Docker CLI can be done with `docker run` and specify the database type, in this case `sqlite`, setting the exposed port `9925`, mounting the current directory, and pull the latest image. After the image is up and running you can navigate to http://your.ip.address:9925 and you'll should see mealie up and running!

```shell
docker run \
    -p 9925:80 \
    -v `pwd`:'/app/data/' \
    hkotel/mealie:latest

```

!!! tip "Default Credentials"
    **Username:** changeme@email.com 

    **Password:** MyPassword

## Docker Compose with SQLite
Deployment with docker-compose is the recommended method for deployment. The example below will create an instance of mealie available on port `9925` with the data volume mounted from the local directory. To use, create a docker-compose.yml file, paste the contents below and save. In the terminal run `docker-compose up -d` to start the container. 

```yaml
version: "3.1"
services:
  mealie:
    container_name: mealie
    image: hkotel/mealie:latest
    restart: always
    ports:
      - 9925:80
    environment:
      TZ: America/Anchorage
    volumes:
      - ./mealie/data/:/app/data

```

## Docker Compose with Postgres *(BETA)*
Postgres support was introduced in v0.5.0. At this point it should be used with caution and frequent backups. 

```yaml
version: "3.1"
services:
  mealie:
    container_name: mealie
    image: hkotel/mealie:latest
    restart: always
    ports:
      - 9090:80
    environment:
      DB_ENGINE: postgres # Optional: 'sqlite', 'postgres'
      POSTGRES_USER: mealie
      POSTGRES_PASSWORD: mealie
      POSTGRES_SERVER: postgres
      POSTGRES_PORT: 5432
      POSTGRES_DB: mealie
  postgres:
    container_name: postgres
    image: postgres
    restart: always
    environment:
      POSTGRES_PASSWORD: mealie
      POSTGRES_USER: mealie
```

## Env Variables

| Variables         | Default               | Description                                                                         |
| ----------------- | --------------------- | ----------------------------------------------------------------------------------- |
| DEFAULT_GROUP     | Home                  | The default group for users                                                         |
| DEFAULT_EMAIL     | changeme@email.com    | The default username for the superuser                                              |
| BASE_URL          | http://localhost:8080 | Used for Notifications                                                              |
| DB_ENGINE         | sqlite                | Optional: 'sqlite', 'postgres'                                                      |
| POSTGRES_USER     | mealie                | Postgres database user                                                              |
| POSTGRES_PASSWORD | mealie                | Postgres database password                                                          |
| POSTGRES_SERVER   | postgres              | Postgres database server address                                                    |
| POSTGRES_PORT     | 5432                  | Postgres database port                                                              |
| POSTGRES_DB       | mealie                | Postgres database name                                                              |
| TOKEN_TIME        | 2                     | The time in hours that a login/auth token is valid                                  |
| API_PORT          | 9000                  | The port exposed by backend API. **do not change this if you're running in docker** |
| API_DOCS          | True                  | Turns on/off access to the API documentation locally.                               |
| TZ                | UTC                   | Must be set to get correct date/time on the server                                  |


## Raspberry Pi 4

!!! tip "Fatal Python error: init_interp_main: can't initialize time"
    Some users experience an problem with running the linux/arm/v7 container on Raspberry Pi 4. This is not a problem with the Mealie container, but with a bug in the hosts Docker installation.
    
    Update the host RP4 using [instructions](https://github.com/linuxserver/docker-papermerge/issues/4#issuecomment-735236388){:target="_blank"}, summarized here:

    ```shell
    wget http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb
    sudo dpkg -i libseccomp2_2.5.1-1_armhf.deb
    ```



## Advanced 
!!! warning "Not Required"
    The items below are completely optional and are not required to manage or install your Mealie instance. 

### Custom Caddy File
The Docker image provided by Mealie contains both the API and the html bundle in one convenient image. This is done by using a proxy server to serve different parts of the application depending on the URL/URI. Requests sent to `/api/*` or `/docs` will be directed to the API, anything else will be served the static web files. Below is the default Caddyfile that is used to proxy requests. You can override this file by mounting an alternative Caddyfile to `/app/Caddyfile`. 

```
{
	auto_https off
  admin off
}

:80 {
  @proxied path /api/* /docs /openapi.json
  
  root * /app/dist
  encode gzip
  uri strip_suffix /
  
  handle_path /api/recipes/image/* {
    root * /app/data/img/
    file_server
  }

  handle @proxied {
    reverse_proxy http://127.0.0.1:9000 
  }

  handle {
    try_files {path}.html {path} /
    file_server 
  }

}
```

## Deployed without Docker
!!! error "Unsupported Deployment"
    If you are experiencing a problem with manual deployment, please do not submit a github issue unless it is related to an aspect of the application. For deployment help, the [discord server](https://discord.gg/QuStdQGSGK){:target="_blank"} is a better place to find support. 

Alternatively, this project is built on Python and SQLite so you may run it as a python application on your server. This is not a supported options for deployment and is only here as a reference for those who would like to do this on their own. To get started you can clone this repository into a directory of your choice and use the instructions below as a reference for how to get started. 

There are three parts to the Mealie application

- Frontend/Static Files
- Backend API
- Proxy Server

### Frontend/ Static Files
The frontend static files are generated with `npm run build`. This is done during the build process with docker. If you choose to deploy this as a system application you must do this process yourself. In the project directory run `cd frontend` to change directories into the frontend directory and run `npm install` and then `npm run build`. This will generate the static files in a `dist` folder in the frontend directory.

### Backend API
The backend API is build with Python, FastAPI, and SQLite and requires Python 3.9, and Poetry. Once the requirements are installed, in the project directory you can run the command `poetry install` to create a python virtual environment and install the python dependencies.

Once the dependencies are installed you should be ready to run the server. To initialize that database you need to first run	`python mealie/db/init_db.py`. Then to start The web server, you run the command `uvicorn mealie.app:app --host 0.0.0.0 --port 9000`


### Proxy Server
You must use a proxy server to server up the static files created with `npm run build` and proxy requests to the API. In the docker build this is done with Caddy. You can use the CaddyFile in the section above as a reference. One important thing to keep in mind is that you should drop any trailing `/` in the url. Not doing this may result in failed API requests. 

