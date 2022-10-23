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
}

change_user() {
    # If container is started as root then create a new user and switch to it
    if [ "$(id -u)" = "0" ]; then
        add_user
        chown -R $PUID:$PGID /app

        echo "Switching to dedicated user"
        exec gosu $PUID "$BASH_SOURCE" "$@"
    elif [ "$(id -u)" = $PUID ]; then
        echo "
        User uid:    $PUID
        User gid:    $PGID
        "
    fi
}

init() {
    # $MEALIE_HOME directory
    cd /app

    # Activate our virtual environment here
    . /opt/pysetup/.venv/bin/activate

    # Initialize Database Prerun
    poetry run python /app/mealie/db/init_db.py
}

if [ "$ARG1" == "reload" ]; then
    echo "Hot Reload!"

    init

    # Start API
    python /app/mealie/app.py
else
    echo "Production"

    change_user

    init

    GUNICORN_PORT=${API_PORT:-9000}

    # Start API

    if [ $WEB_GUNICORN == 'true' ]; then
        echo "Starting Gunicorn"
        gunicorn mealie.app:app -b 0.0.0.0:$GUNICORN_PORT -k uvicorn.workers.UvicornWorker -c /app/gunicorn_conf.py --preload
    else
        uvicorn mealie.app:app --host 0.0.0.0 --port $GUNICORN_PORT
    fi
fi
