# Development: Getting Started

After reading through the [Code Contributions Guide](http://127.0.0.1:8000/contributors/developers-guide/code-contributions/) and forking the repo you can start working. This project is developed with :whale: docker and as such you will be greatly aided by using docker for development. It's not necessary but it is helpful.

## With Docker
There are 2 scripts to help set up your development environment in dev/scripts/. 

`docker-compose.dev.sh` - Will spin up a docker development server
`docker-compose.sh` - Will spin up a docker production server

There are VSCode tasks created in the .vscode folder. You can use these to quickly execute the scripts above using the command palette.


## Without Docker
?? TODO

## Trouble Shooting

!!! Error "Symptom: Vue Development Server Wont Start"
    **Error:** `TypeError: Cannot read property 'upgrade' of undefined`

    **Solution:** You may be missing the `/frontend/.env.development.` The contents should be `VUE_APP_API_BASE_URL=http://127.0.0.1:9921`. This is a reference to proxy the the API requests from Vue to 127.0.0.1 at port 9921 where FastAPI should be running.

!!! Error "Symptom: FastAPI Development Server Wont Start"
    **Error:** `RuntimeError: Directory '/app/dist' does not exist`

    **Solution:** Create an empty /mealie/dist directory. This directory is served as static content by FastAPI. It is provided during the build process and may be missing in development. 

Run into another issue? [Ask for help on discord](https://discord.gg/R6QDyJgbD2)