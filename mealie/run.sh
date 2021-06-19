#!/bin/bash

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

# Get Reload Arg `run.sh reload` for dev server
ARG1=${1:-production}

# # Initialize Database Prerun
poetry run python /app/mealie/db/init_db.py
poetry run python /app/mealie/services/image/minify.py

# Migrations
# TODO
    # Migrations
    # Set Port from ENV Variable

if [ "$ARG1" == "reload" ]
then
    echo "Hot Reload!"

    # Start API
    python /app/mealie/app.py
else
    echo "Production"
    # Web Server
    caddy start --config ./Caddyfile

    # Start API
    uvicorn mealie.app:app --host 0.0.0.0 --port 9000
fi

