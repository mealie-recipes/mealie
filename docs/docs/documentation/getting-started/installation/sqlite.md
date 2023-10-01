# Installing with SQLite

SQLite is a popular, open source, self-contained, zero-configuration database that is the ideal choice for Mealie when you have 1-20 Users. Below is a ready to use docker-compose.yaml file for deploying Mealie on your server.

**For Environmental Variable Configuration See:**

- [Configuration](./backend-config.md)

```yaml
---
version: "3.7"
services:
  mealie:
    image: ghcr.io/mealie-recipes/mealie:nightly
    container_name: mealie
    ports:
        - "9925:9000" # (1)
    deploy:
      resources:
        limits:
          memory: 1000M # (2)
    volumes:
      - mealie-data:/app/data/
    environment:
    # Set Backend ENV Variables Here
      - ALLOW_SIGNUP=true
      - PUID=1000
      - PGID=1000
      - TZ=America/Anchorage
      - MAX_WORKERS=1
      - WEB_CONCURRENCY=1
      - BASE_URL=https://mealie.yourdomain.com
    restart: always

volumes:
  mealie-data:
    driver: local
```

<!-- Updating This? Be Sure to also update the Postgres Annotations -->

1.  To access the mealie interface you only need to expose port 9000 on the container. Here we expose port 9925 on the host, but feel free to change this to any port you like.
2.  Setting an explicit memory limit is recommended. Python can pre-allocate larger amounts of memory than is necessary if you have a machine with a lot of RAM. This can cause the container to idle at a high memory usage. Setting a memory limit will improve idle performance.
