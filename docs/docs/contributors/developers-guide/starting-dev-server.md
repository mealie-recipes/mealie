# Development: Getting Started

!!! warning
    Be sure to use the [Nightly version](https://nightly.mealie.io/) of the docs to ensure you're up to date with
    the latest changes.

After reading through the [Code Contributions Guide](../developers-guide/code-contributions.md) and forking the repo you can start working. This project is developed with :whale: docker and as such you will be greatly aided by using docker for development. It's not necessary but it is helpful.

## With [VSCode Dev Containers](https://code.visualstudio.com/docs/remote/containers)

Prerequisites

- Docker
- Visual Studio Code

### Linux and MacOS

First ensure that docker is running. Then when you clone the repo and open with VS Code you should see a popup asking you to reopen the project inside a development container. Click yes and it will build the development container and run the setup required to run both the backend API and the frontend webserver. This also pre-configures pre-commit hooks to ensure that the code is up to date before committing.

### Windows

Make sure the VSCode Dev Containers extension is installed, then select "Dev Containers: Clone Repository in Container Volume..." in the command palette (F1). Select your forked repo and choose the `mealie-next` branch, which contains the latest changes. This mounts your repository directly in WSL2, which [greatly improves the performance of the container](https://code.visualstudio.com/docs/devcontainers/containers#_quick-start-open-a-git-repository-or-github-pr-in-an-isolated-container-volume), and enables hot-reloading for the frontend. Running the container on a mounted volume may not work correctly on Windows due to WSL permission mapping issues.

!!! tip
    For slow terminal checkout the solution in this [GitHub Issue](https://github.com/microsoft/vscode/issues/133215)

    ```bash
    git config oh-my-zsh.hide-info 1
    ```

## Without Dev Containers

### Prerequisites

- [Python 3.12](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Node v16.x](https://nodejs.org/en/)
- [yarn](https://classic.yarnpkg.com/lang/en/docs/install/#mac-stable)
- [task](https://taskfile.dev/#/installation)

### Installing Dependencies

Once the prerequisites are installed you can cd into the project base directory and run `task setup` to install the python and node dependencies, and download the NLP model.

=== "Linux / macOS"

    ```bash
    # Naviate To The Root Directory
    cd /path/to/project

    # Utilize the Taskfile to Install Dependencies
    task setup
    ```

## Postgres

The taskfile has two commands that need to be run to run the development environment against a postgres database.

- `task dev:services` - This will start the postgres database, and a smtp server for email testing.
- `task py:postgres` - This will run that backend API configured for the local postgres database.

## Starting The Server

Now you're ready to start the servers. You'll need two shells open, One for the server and one for the frontend.

=== "Linux / macOS"

    ```bash
    # Terminal #1
    task py

    # Terminal #2
    task ui
    ```

## Internationalization

### Frontend

We use vue-i18n package for internationalization. Translations are stored in json format located in [frontend/lang/messages](https://github.com/mealie-recipes/mealie/tree/mealie-next/frontend/lang/messages).

### Backend

Translations are stored in json format located in [mealie/lang/messages](https://github.com/mealie-recipes/mealie/tree/mealie-next/mealie/lang/messages).

### Quick frontend localization with VS Code

[i18n Ally for VScode](https://marketplace.visualstudio.com/items?itemName=lokalise.i18n-ally) is helpful for generating new strings to translate using Code Actions. It also has a nice feature, which shows translations in-place when editing code.

A few settings must be tweaked to make the most of its features. Some settings are stored on project level, but most of them have to be set manually in your workspace or user settings.\
We've found that the following settings work best:

```
  "i18n-ally.enabledFrameworks": ["vue"],
  "i18n-ally.extract.autoDetect": true,
  "i18n-ally.dirStructure": "auto",
  "i18n-ally.extract.targetPickingStrategy": "global-previous",
  "i18n-ally.displayLanguage": "en-US",
  "i18n-ally.keystyle": "nested",
  "i18n-ally.sourceLanguage": "en-US",
```
