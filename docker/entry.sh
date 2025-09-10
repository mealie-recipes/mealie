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
    . /opt/mealie/bin/activate
}

load_secrets() {
    # Each of these environment variables will support a `_FILE` suffix that allows
    # for setting the environment variable through the Docker Compose secret
    # pattern.
    local -a secret_supported_vars=(
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "POSTGRES_SERVER"
        "POSTGRES_PORT"
        "POSTGRES_DB"
        "POSTGRES_URL_OVERRIDE"

        "SMTP_HOST"
        "SMTP_PORT"
        "SMTP_USER"
        "SMTP_PASSWORD"

        "LDAP_SERVER_URL"
        "LDAP_QUERY_PASSWORD"

        "OIDC_CONFIGURATION_URL"
        "OIDC_CLIENT_ID"
        "OIDC_CLIENT_SECRET"

        "OPENAI_BASE_URL"
        "OPENAI_API_KEY"
    )

    # If any secrets are set, prefer them over base environment variables.
    for var in "${secret_supported_vars[@]}"; do
        file_var="${var}_FILE"
        if [ -n "${!file_var}" ]; then
            export "$var=$(<"${!file_var}")"
        fi
    done
}

change_user
init
load_secrets

# Start API
HOST_IP=`/sbin/ip route|awk '/default/ { print $3 }'`

exec mealie
