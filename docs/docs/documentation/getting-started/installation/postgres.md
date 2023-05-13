# Installing with PostgreSQL

PostgreSQL might be considered if you need to support many concurrent users. In addition, some features are only enabled on PostgreSQL, such as fuzzy search.

**For Environmental Variable Configuration See:**

- [Frontend Configuration](./frontend-config.md)
- [Backend Configuration](./backend-config.md)

```yaml
---
version: "3.7"
services:
  mealie-frontend:
    image: hkotel/mealie:frontend-v1.0.0beta-5
    container_name: mealie-frontend
    depends_on:
      - mealie-api
    environment:
    # Set Frontend ENV Variables Here
      - API_URL=http://mealie-api:9000 # (1)
    restart: always
    ports:
      - "9925:3000" # (2)
    volumes:
      - mealie-data:/app/data/ # (3)
  mealie-api:
    image: hkotel/mealie:api-v1.0.0beta-5
    container_name: mealie-api
    deploy:
      resources:
        limits:
          memory: 1000M # (4)
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
    image: postgres
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

1. Whoa whoa whoa, what is this nonsense? The API_URL is the URL the frontend container uses to proxy api requests to the backend server. In this example, the name `mealie-api` resolves to the `mealie-api` container which runs the API server on port 9000. This allows you to access the API without exposing an additional port on the host.
    <br/> <br/> **Note** that both containers must be on the same docker-network for this to work.
2.  To access the mealie interface you only need to expose port 3000 on the mealie-frontend container. Here we expose port 9925 on the host, feel free to change this to any port you like.
3.  Mounting the data directory to the frontend is now required to access the images/assets directory. This can be mounted read-only. Internally the frontend containers runs a Caddy proxy server that serves the assets requested to reduce load on the backend API.
4.  Setting an explicit memory limit is recommended. Python can pre-allocate larger amounts of memory than is necessary if you have a machine with a lot of RAM. This can cause the container to idle at a high memory usage. Setting a memory limit will improve idle performance.
