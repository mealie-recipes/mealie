#!/bin/sh

## Migrations
# TODO

# Database Init

## Web Server
caddy start --config ./Caddyfile

## Start API
uvicorn mealie.app:app --host 0.0.0.0 --port 9000