# Development: Getting Started

After reading through the [Code Contributions Guide](https://hay-kot.github.io/mealie/contributors/developers-guide/code-contributions/) and forking the repo you can start working. This project is developed with :whale: docker and as such you will be greatly aided by using docker for development. It's not necessary but it is helpful.

## With Docker
Prerequisites

- Docker
- docker-compose

You can easily start the development stack by running `make docker-dev` in the root of the project directory. This will run and build the docker-compose.dev.yml file. 

## Without Docker
Prerequisites

- Python 3.9+
- Poetry
- Nodejs
- npm

Once the prerequisites are installed you can cd into the project base directory and run `make setup` to install the python and node dependencies. Once that is complete you can run `make backend` and `make vue` to start the backend and frontend servers. 

## Make File Reference 
`make setup` installs python and node dependencies

`make backend` Starts the backend server on port `9000`

`make vue` Starts the frontend server on port `8080`

`make docs` Starts the documentation server on port `8000`

`make docker-dev` Builds docker-compose.dev.yml 

`make docker-prod` Builds docker-compose.yml to test for production


## Trouble Shooting

!!! Error "Symptom: Vue Development Server Wont Start"
    **Error:** `TypeError: Cannot read property 'upgrade' of undefined`

    **Solution:** You may be missing the `/frontend/.env.development.` The contents should be `VUE_APP_API_BASE_URL=http://127.0.0.1:9921`. This is a reference to proxy the the API requests from Vue to 127.0.0.1 at port 9921 where FastAPI should be running.

!!! Error "Symptom: FastAPI Development Server Wont Start"
    **Error:** `RuntimeError: Directory '/app/dist' does not exist`

    **Solution:** Create an empty /mealie/dist directory. This directory is served as static content by FastAPI. It is provided during the build process and may be missing in development. 

Run into another issue? [Ask for help on discord](https://discord.gg/QuStdQGSGK)