#!/bin/sh

# Get Reload Arg `run.sh reload` for dev server
ARG1=${1:-production}

# Initialize Database Prerun
python mealie/db/init_db.py
python mealie/services/image/minify.py

## Migrations
# TODO

if [ "$ARG1" = "reload" ] 
then
    echo "Hot reload"

    # Start API
    uvicorn mealie.app:app --host 0.0.0.0 --port 9000 --reload
else
    echo "Production config"
    # Web Server
    caddy start --config ./Caddyfile

    # Start API
    uvicorn mealie.app:app --host 0.0.0.0 --port 9000
fi