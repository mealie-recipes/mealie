# Using the Omni Image

Since [#1948](https://github.com/hay-kot/mealie/pull/1948) we've started publishing an experimental image that merges both the frontend and backend services into a single container image. This image is currently in an experimental state, and should be used with caution. Continued support for this image will be based on user feedback and demand, if you're using this image please let us know how it's working for you. The single container comes with SQLite, and can be used with PostgreSQL by adding a postgres container to the docker-compose file (see the [PostgreSQL install](./postgres.md) for a snippet).

- [Feedback Discussion](https://github.com/hay-kot/mealie/discussions/1949)

**For Environmental Variable Configuration See:**

Note that frontend and backend configurations are both applied to the same container. The container exposes the port 9000 for the API and port 3000 for the frontend.

- [Frontend Configuration](./frontend-config.md)
- [Backend Configuration](./backend-config.md)

```yaml
---
version: "3.7"
services:
  mealie-omni:
    image: hkotel/mealie:omni-nightly
    container_name: mealie
    ports:
      - "3000:3000"
      - "9000:9000"
    volumes:
      - mealie-data:/app/data/
    environment:
      - ALLOW_SIGNUP=true
      - PUID=1000
      - PGID=1000
      - TZ=America/Anchorage
      - BASE_URL=https://mealie.yourdomain.com
    restart: always

volumes:
  mealie-data:
    driver: local
```
