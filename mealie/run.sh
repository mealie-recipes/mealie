#!/bin/sh

# Initialize Database Prerun
python mealie/db/init_db.py
python mealie/services/image/minify.py

## Migrations
# TODO

## Web Server
caddy start --config ./Caddyfile

# Start API
uvicorn mealie.app:app --host 0.0.0.0 --port 9000