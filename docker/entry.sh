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
    if [ "$(id -u)" = $PUID ]; then
        echo "
        User uid:    $PUID
        User gid:    $PGID
        "
    elif [ "$(id -u)" = "0" ]; then
        # If container is started as root then create a new user and switch to it
        add_user
        chown -R $PUID:$PGID /app

        echo "Switching to dedicated user"
        exec gosu $PUID "$BASH_SOURCE" "$@"
    fi
}

init() {
    # $MEALIE_HOME directory
    cd /app

    # Activate our virtual environment here
    . /opt/pysetup/.venv/bin/activate
}

change_user
init

# Start API
HOST_IP=`/sbin/ip route|awk '/default/ { print $3 }'`

exec python /app/mealie/main.py
