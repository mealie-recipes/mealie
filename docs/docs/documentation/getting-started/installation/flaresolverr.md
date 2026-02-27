# Flaresolverr

:octicons-tag-24: v3.12.0

Mealie's [flaresolverr](https://github.com/FlareSolverr/FlareSolverr) integration helps to pull recipes from sites with aggressive bot protection.

## Configuration

To enable flaresolverr, you must run a flaresolverr instance locally. Make sure your machine can support the additional resource usage required for flaresolverr. If you are using docker-compose, you can add the following to your yaml file:

```yaml
services:
  mealie:
    ...
    environment:
      FLARESOLVERR_URL: flaresolverr:8191

  flaresolverr:
    container_name: mealie-flaresolverr
    image: ghcr.io/flaresolverr/flaresolverr:latest
    restart: 'unless-stopped'
    environment:
      - LOG_LEVEL=info
      - LOG_HTML=false
    ports:
      - 8191:8191
```

For most users, specifying the FLARESOLVERR_URL is all you need to do inside mealie.
