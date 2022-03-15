# Development: Getting Started

!!! warning
    Be sure to use the [Nightly version](https://nightly.mealie.io/) of the docs to ensure you're up to date with
    the latest changes.

After reading through the [Code Contributions Guide](../developers-guide/code-contributions.md) and forking the repo you can start working. This project is developed with :whale: docker and as such you will be greatly aided by using docker for development. It's not necessary but it is helpful.

## With VS Code Dev Containers

Prerequisites

- Docker
- Visual Studio Code

First ensure that docker is running. Then when you clone the repo and open with VS Code you should see a popup asking you to reopen the project inside a development container. Click yes and it will build the development container and run the setup required to run both the backend API and the frontend webserver. This also pre-configures pre-commit hooks to ensure that the code is up to date before committing.

Checkout the makefile for all of the available commands.

!!! tip
    For slow terminal checkout the solution in this [GitHub Issue](https://github.com/microsoft/vscode/issues/133215)

    ```bash
    git config oh-my-zsh.hide-info 1
    ```

## Without Dev Containers
### Prerequisites

- [Python 3.10](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Node v16.x](https://nodejs.org/en/)
- [yarn](https://classic.yarnpkg.com/lang/en/docs/install/#mac-stable)

### Installing Dependencies

Once the prerequisites are installed you can cd into the project base directory and run `make setup` to install the python and node dependencies.

=== "Linux / MacOs"

    ```bash
    # Naviate To The Root Directory
    cd /path/to/project

    # Utilize the Makefile to Install Dependencies
    make setup
    ```

=== "Windows"

    ``` powershell
    # Install Python Dependencies
    Set-Directory -Path "C:\path\to\project"
    poetry install

    # Install Node Dependencies
    Set-Directory frontend
    yarn install
    ```

### Setting ENV Variables

Before you start the server you MUST copy the `template.env` and `frontend/template.env` files to their respective locations with the name `.env` and `frontend/.env` respectively. The application will-not run without these files.

### Starting The Server

Once that is complete you're ready to start the servers. You'll need two shells open, One for the server and one for the frontend.

=== "Linux / MacOs"

    ```bash
    # Terminal #1
    make backend

    # Terminal #2
    make frontend
    ```

=== "Windows"

    ``` powershell
    # Terminal # 1
	poetry run python mealie/db/init_db.py # Initialize the database
	poetry run python mealie/app.py # start application

    # Terminal # 2
    Set-Directory frontend
    yarn run dev
    ```

## Make File Reference

Run `make help` for reference. If you're on a system that doesn't support makefiles in most cases you can use the commands directly in your terminal by copy/pasting them from the Makefile.

```
docs                 📄 Start Mkdocs Development Server
code-gen             🤖 Run Code-Gen Scripts
setup                🏗  Setup Development Instance
setup-model          🤖 Get the latest NLP CRF++ Model
clean-data           ⚠️  Removes All Developer Data for a fresh server start
clean-pyc            🧹 Remove Python file artifacts
clean-test           🧹 Remove test and coverage artifacts
backend-clean        🧹 Remove all build, test, coverage and Python artifacts
backend-test         🧪 Run tests quickly with the default Python
backend-format       🧺 Format, Check and Flake8
backend-all          🧪 Runs all the backend checks and tests
backend-coverage     ☂️  Check code coverage quickly with the default Python
backend              🎬 Start Mealie Backend Development Server
frontend             🎬 Start Mealie Frontend Development Server
frontend-build       🏗  Build Frontend in frontend/dist
frontend-generate    🏗  Generate Code for Frontend
frontend-lint        🧺 Run yarn lint
docker-dev           🐳 Build and Start Docker Development Stack
docker-prod          🐳 Build and Start Docker Production Stack

```
