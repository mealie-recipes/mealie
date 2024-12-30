# Installing with PostgreSQL

PostgreSQL might be considered if you need to support many concurrent users. In addition, some features are only enabled on PostgreSQL, such as fuzzy search.

**For Environment Variable Configuration, see** [Backend Configuration](./backend-config.md)

```yaml
services:
  mealie:
    image: ghcr.io/mealie-recipes/mealie:v2.4.1 # (3)
    container_name: mealie
    restart: always
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
      ALLOW_SIGNUP: "false"
      PUID: 1000
      PGID: 1000
      TZ: America/Anchorage
      BASE_URL: https://mealie.yourdomain.com
      # Database Settings
      DB_ENGINE: postgres
      POSTGRES_USER: mealie
      POSTGRES_PASSWORD: mealie
      POSTGRES_SERVER: postgres
      POSTGRES_PORT: 5432
      POSTGRES_DB: mealie
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    container_name: postgres
    image: postgres:15
    restart: always
    volumes:
      - mealie-pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: mealie
      POSTGRES_USER: mealie
      PGUSER: mealie
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  mealie-data:
  mealie-pgdata:
```

<!-- Updating This? Be Sure to also update the SQLite Annotations -->

1.  To access the mealie interface you only need to expose port 9000 on the mealie container. Here we expose port 9925 on the host, but feel free to change this to any port you like.
2.  Setting an explicit memory limit is recommended. Python can pre-allocate larger amounts of memory than is necessary if you have a machine with a lot of RAM. This can cause the container to idle at a high memory usage. Setting a memory limit will improve idle performance.
3.  You should double check this value isn't out of date when setting up for the first time; check the README and use the value from the "latest release" badge at the top - the format should be `vX.Y.Z`. Whilst a 'latest' tag is available, the Mealie team advises specifying a specific version tag and consciously updating to newer versions when you have time to read the release notes and ensure you follow any manual actions required (which should be rare).
