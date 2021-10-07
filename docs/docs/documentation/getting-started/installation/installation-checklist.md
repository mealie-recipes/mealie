# Installation Checklist

To install Mealie on your server there are a few steps for proper configuration. Let's go through them.

## Step 0: Pre-work

To deploy mealie on your local network it is highly recommended to use docker to deploy the image straight from dockerhub. Using the docker-compose templates provided, you should be able to get a stack up and running easily by changing a few default values and deploying. You can deploy with either SQLite (default) or Postgres. SQLite is sufficient for most use cases. Additionally, with Mealie's automated backup and restore functionality, you can easily move between SQLite and Postgres as you wish.

[Get Docker](https://docs.docker.com/get-docker/)

[Mealie on Dockerhub](https://hub.docker.com/r/hkotel/mealie)

- linux/amd64
- linux/arm64


## Step 1: Deciding on Deployment Type
SQLite is a popular, open source, self-contained, zero-configuration database that is the ideal choice for Mealie when you have 1-20 Users. If you need to support many concurrent users, you may want to consider a more robust database such as PostgreSQL. 

You can find the relevant ready to use docker-compose files for supported installations at the links below.

- [SQLite](/mealie/documentation/getting-started/installation/sqlite/)
- [PostgreSQL](/mealie/documentation/getting-started/installation/postgres/)

## Step 2: Customizing The `docker-compose.yaml` files.
After you've decided on a database it's important to set a few ENV variables to ensure that you can use all the features of Mealie. I recommend that you verify and check that:

- [x] You've configured the relevant ENV variables for your database selection in the `docker-compose.yaml` files.
- [x] You've configured the [SMTP server settings](/mealie/documentation/getting-started/installation/backend-config/#email) (used for invitations, password resets, etc)
- [x] Verified the port mapped on the `mealie-frontend` container is an open port on your server (Default: 9925)
- [x] You've set the [`BASE_URL`](/mealie/documentation/getting-started/installation/backend-config/#general) variable.
- [x] You've set the `DEFAULT_EMAIL` and `DEFAULT_GROUP` variable.
- [x] Make any theme changes on the frontend container. [See Frontend Config](/mealie/documentation/getting-started/installation/frontend-config/#themeing)

## Step 3: Startup 
After you've configured your database, and updated the `docker-compose.yaml` files, you can start Mealie by running the following command in the directory where you've added your `docker-compose.yaml`. 

```bash
$ docker-compose up -d
```

You should see the containers start up without error. You should now be able to access the Mealie frontend at [http://localhost:9925](http://locahost:9925).

!!! tip "Default Credentials"

    **Username:** changeme@email.com

    **Password:** MyPassword

## Step 4: Backup
While v1.0.0 is a great step to data-stability and security, it's not a backup. As a core feature, Mealie will run a backup of the entire database every 24 hours. Optionally, you can also run backups whenever you'd like through the UI or the API. 

These backups are just plain .zip files that you can download from the UI or access via the mounted volume on your system. For complete data protection you MUST store these backups somewhere safe, and outside of the server where they are deployed. A favorite solution of mine is [autorestic](https://autorestic.vercel.app/) which can be configured via yaml to run an off-site backup on a regular basis. 