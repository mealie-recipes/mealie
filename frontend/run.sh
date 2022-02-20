# Production entry point for the frontend docker container

# Web Server
caddy start --config /app/Caddyfile

# Start Node Application
yarn start -p 3001