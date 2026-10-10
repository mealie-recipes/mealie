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
    )
    local var file_var secret_file secret_value

    # If any secrets are set, prefer them over base environment variables.
    for var in "${secret_supported_vars[@]}"; do
        file_var="${var}_FILE"
        if [ -n "${!file_var}" ]; then
            secret_file="${!file_var}"
            if [ ! -f "$secret_file" ] || [ ! -r "$secret_file" ]; then
                echo "ERROR: $file_var must point to a readable regular file." >&2
                return 1
            fi
            # Check the read separately: export would mask a failed substitution.
            if ! secret_value=$(cat -- "$secret_file" 2>/dev/null); then
                echo "ERROR: Unable to read the secret configured by $file_var." >&2
                return 1
            fi
            if [ -z "$secret_value" ]; then
                echo "ERROR: The secret configured by $file_var must not be empty." >&2
                return 1
            fi
            export "$var=$secret_value"
        fi
    done
}

change_user
init
load_secrets || exit 1

# Start API
HOST_IP=`/sbin/ip route|awk '/default/ { print $3 }'`

exec mealie
