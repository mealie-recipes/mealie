# Advanced Installation

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

    If you are experiencing a problem with manual deployment, please do not submit a github issue unless it is related to an aspect of the application. For deployment help, the [discord server](https://discord.gg/QuStdQGSGK) is a better place to find support.

Alternatively, this project is built on Python and SQLite so you may run it as a python application on your server. This is not a supported options for deployment and is only here as a reference for those who would like to do this on their own. To get started you can clone this repository into a directory of your choice and use the instructions below as a reference for how to get started.

There are three parts to the Mealie application

- Frontend/Static Files
- Backend API
- Proxy Server

### Frontend/ Static Files

The frontend static files are generated with `npm run build`. This is done during the build process with docker. If you choose to deploy this as a system application you must do this process yourself. In the project directory run `cd frontend` to change directories into the frontend directory and run `npm install` and then `npm run build`. This will generate the static files in a `dist` folder in the frontend directory.

### Backend API

The backend API is build with Python, FastAPI, and SQLite and requires Python 3.9, and Poetry. Once the requirements are installed, in the project directory you can run the command `poetry install` to create a python virtual environment and install the python dependencies.

Once the dependencies are installed you should be ready to run the server. To initialize that database you need to first run `python mealie/db/init_db.py`. Then to start The web server, you run the command `uvicorn mealie.app:app --host 0.0.0.0 --port 9000`

### Proxy Server

You must use a proxy server to server up the static files created with `npm run build` and proxy requests to the API. In the docker build this is done with Caddy. You can use the CaddyFile in the section above as a reference. One important thing to keep in mind is that you should drop any trailing `/` in the url. Not doing this may result in failed API requests.

[workers_per_core]: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/2daa3e3873c837d5781feb4ff6a40a89f791f81b/README.md#workers_per_core
[max_workers]: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/2daa3e3873c837d5781feb4ff6a40a89f791f81b/README.md#max_workers
[web_concurrency]: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/2daa3e3873c837d5781feb4ff6a40a89f791f81b/README.md#web_concurrency
