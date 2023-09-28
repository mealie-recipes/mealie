# Installing with PostgreSQL

PostgreSQL might be considered if you need to support many concurrent users. In addition, some features are only enabled on PostgreSQL, such as fuzzy search.

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
        - "9925:9000"
    deploy:
      resources:
        limits:
          memory: 1000M # (1)
    depends_on:
      - postgres
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

    # Database Settings
      - DB_ENGINE=postgres
      - POSTGRES_USER=mealie
      - POSTGRES_PASSWORD=mealie
      - POSTGRES_SERVER=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=mealie
    restart: always
  postgres:
    container_name: postgres
    image: postgres:15
    restart: always
    volumes:
      - ./mealie-pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: mealie
      POSTGRES_USER: mealie

volumes:
  mealie-data:
    driver: local
  mealie-pgdata:
    driver: local
```

<!-- Updating This? Be Sure to also update the SQLite Annotations -->

1.  To access the mealie interface you only need to expose port 9000 on the mealie container. Here we expose port 9925 on the host, but feel free to change this to any port you like.
2.  Setting an explicit memory limit is recommended. Python can pre-allocate larger amounts of memory than is necessary if you have a machine with a lot of RAM. This can cause the container to idle at a high memory usage. Setting a memory limit will improve idle performance.
