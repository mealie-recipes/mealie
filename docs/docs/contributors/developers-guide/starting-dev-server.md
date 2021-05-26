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
`make help` Get an overview of the make commands

`make setup` Installs python and node dependencies

`make backend` Starts the backend server on port `9000`

`make frontend` Starts the frontend server on port `8080`

`make docs` Starts the documentation server on port `8000`

`make docker-dev` Builds docker-compose.dev.yml 

`make docker-prod` Builds docker-compose.yml to test for production

## Before you Commit! 

Before you commit any changes on the backend/python side you'll want to run `make format` to format all the code with black. `make lint` to check with flake8, and `make test` to run pytests. You can also use `make test-all` to run both `lint` and `test`. 

Run into another issue? [Ask for help on discord](https://discord.gg/QuStdQGSGK)