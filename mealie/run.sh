#!/bin/bash

set -e

# Get Reload Arg `run.sh reload` for dev server
ARG1=${1:-production}

# Get PUID/PGID
PUID=${PUID:-911}
PGID=${PGID:-911}

add_user() {
    groupmod -o -g "$PGID" abc
    usermod -o -u "$PUID" abc

    echo "
    User uid:    $(id -u abc)
    User gid:    $(id -g abc)
    "
    chown -R abc:abc /app
}

init() {
    # $MEALIE_HOME directory
    cd /app
    # Activate our virtual environment here
    . /opt/pysetup/.venv/bin/activate

    # Initialize Database Prerun
    poetry run python /app/mealie/db/init_db.py
    poetry run python /app/mealie/services/image/minify.py
}

# Migrations
# TODO
    # Migrations
    # Set Port from ENV Variable

if [ "$ARG1" == "reload" ]; then
    echo "Hot Reload!"

    init

    # Start API
    python /app/mealie/app.py
else
    echo "Production"

    add_user
    init

    # Web Server
    caddy start --config /app/Caddyfile

    # Start API
    # uvicorn mealie.app:app --host 0.0.0.0 --port 9000
    gunicorn mealie.app:app -b 0.0.0.0:9000 -k uvicorn.workers.UvicornWorker -c /app/gunicorn_conf.py --preload
fi
