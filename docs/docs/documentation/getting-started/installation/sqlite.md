# Installing with SQLite

SQLite is a popular, open source, self-contained, zero-configuration database that is the ideal choice for Mealie when you have 1-20 Users. Below is a ready to use docker-compose.yaml file for deploying Mealie on your server. 

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
    restart: always
```