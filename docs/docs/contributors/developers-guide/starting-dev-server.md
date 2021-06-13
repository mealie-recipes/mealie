# Development: Getting Started

After reading through the [Code Contributions Guide](../developers-guide/code-contributions.md) and forking the repo you can start working. This project is developed with :whale: docker and as such you will be greatly aided by using docker for development. It's not necessary but it is helpful.

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

Once the prerequisites are installed you can cd into the project base directory and run `make setup` to install the python and node dependencies. Once that is complete you can run `make backend` and `make frontend` to start the backend and frontend servers. 

## Make File Reference 

Run `make help` for reference

```
clean-purge          ⚠️ Removes All Developer Data for a fresh server start
clean                🧹 Remove all build, test, coverage and Python artifacts
clean-pyc            🧹 Remove Python file artifacts
clean-test           🧹 Remove test and coverage artifacts
test-all             🧪 Check Lint Format and Testing
test                 🧪 Run tests quickly with the default Python
lint                 🧺 Check style with flake8
coverage             ☂️ Check code coverage quickly with the default Python
setup                🏗 Setup Development Instance
backend              🎬 Start Mealie Backend Development Server
frontend             🎬 Start Mealie Frontend Development Server
frontend-build       🏗 Build Frontend in frontend/dist
docs                 📄 Start Mkdocs Development Server
docker-dev           🐳 Build and Start Docker Development Stack
docker-prod          🐳 Build and Start Docker Production Stack
code-gen             🤖 Run Code-Gen Scripts

```

## Before you Commit! 

Before you commit any changes on the backend/python side you'll want to run `make format` to format all the code with black. `make lint` to check with flake8, and `make test` to run pytests. You can also use `make test-all` to run both `lint` and `test`. 

Run into another issue? [Ask for help on discord](https://discord.gg/QuStdQGSGK){:target="_blank"}