#!/bin/bash
# Start Backend API

# Get PUID/PGID
PUID=${PUID:-911}
PGID=${PGID:-911}
BASH_SOURCE=${BASH_SOURCE:-$0}

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

change_user
init
GUNICORN_PORT=${API_PORT:-9000}

# Start API
hostip=`/sbin/ip route|awk '/default/ { print $3 }'`
if [ "$WEB_GUNICORN" = 'true' ]; then
    echo "Starting Gunicorn"
    exec gunicorn mealie.app:app -b 0.0.0.0:$GUNICORN_PORT --forwarded-allow-ips=$hostip -k uvicorn.workers.UvicornWorker -c /app/gunicorn_conf.py --preload
else
    exec uvicorn mealie.app:app --host 0.0.0.0 --forwarded-allow-ips=$hostip --port $GUNICORN_PORT
fi
