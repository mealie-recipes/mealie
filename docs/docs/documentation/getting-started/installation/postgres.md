# Installing with PostgreSQL

Postgres support was introduced in v0.5.0. At this point it should be used with caution and frequent backups.

**For Environmental Variable Configuration See:**

- [Frontend Configuration](/mealie/documentation/getting-started/installation/frontend-config/)
- [Backend Configuration](/mealie/documentation/getting-started/installation/backend-config/)

```yaml
---
version: "3.7"
services:
  mealie-frontend:
    image: hkotel/mealie:frontend-nightly
    container_name: mealie-frontend
    depends_on:
      - mealie-api
    environment:
    # Set Frontend ENV Variables Here
      - ALLOW_SIGNUP=true
      - API_URL=http://mealie-api:9000
    restart: always
    ports:
      - "9925:3000"
  mealie-api:
    image: hkotel/mealie:api-nightly
    container_name: mealie-api
    depends_on:
      - postgres
    volumes:
      - ./data/:/app/data
    environment:
    # Set Backend ENV Variables Here
      - PUID=1000
      - PGID=1000
      - TZ=America/Anchorage
      - MAX_WORKERS=1
      - WEB_CONCURRENCY=1
      - BASE_URL=https://beta.mealie.io

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
    environment:
      POSTGRES_PASSWORD: mealie
      POSTGRES_USER: mealie
```

