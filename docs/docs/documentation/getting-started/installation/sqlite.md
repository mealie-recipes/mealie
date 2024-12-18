# Installing with SQLite

!!! Warning
    If you're planning on deploying and using Network Attached Storage with Mealie, you should use [Postgres](./postgres.md) instead of SQLite. SQLite is not designed to be used with Network Attached Storage and can cause data corruption, or locked database errors


SQLite is a popular, open source, self-contained, zero-configuration database that is the ideal choice for Mealie when you have 1-20 Users. Below is a ready to use docker-compose.yaml file for deploying Mealie on your server.

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

volumes:
  mealie-data:
```

<!-- Updating This? Be Sure to also update the Postgres Annotations -->

1.  To access the mealie interface you only need to expose port 9000 on the container. Here we expose port 9925 on the host, but feel free to change this to any port you like.
2.  Setting an explicit memory limit is recommended. Python can pre-allocate larger amounts of memory than is necessary if you have a machine with a lot of RAM. This can cause the container to idle at a high memory usage. Setting a memory limit will improve idle performance.
3.  You should double check this value isn't out of date when setting up for the first time; check the README and use the value from the "latest release" badge at the top - the format should be `vX.Y.Z`. Whilst a 'latest' tag is available, the Mealie team advises specifying a specific version tag and consciously updating to newer versions when you have time to read the release notes and ensure you follow any manual actions required (which should be rare).
