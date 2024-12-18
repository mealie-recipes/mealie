# Installation Checklist

To install Mealie on your server, there are a few steps for proper configuration. Let's go through them.

!!! tip TLDR

    Don't need step-by-step? Check out:

    - [SQLite docker-compose](./sqlite.md)
    - [Postgres docker-compose](./postgres.md)

## Pre-work

To deploy mealie on your local network, it is highly recommended to use Docker to deploy the image straight from the GitHub registry. Using the docker-compose templates provided, you should be able to get a stack up and running easily by changing a few default values and deploying. You can deploy with either SQLite (default) or Postgres. SQLite is sufficient for most use cases. Additionally, with Mealie's automated backup and restore functionality, you can easily move between SQLite and Postgres as you wish.

[Get Docker](https://docs.docker.com/get-docker/)

[Get Docker Compose](https://docs.docker.com/compose/install/)

[Mealie on GitHub registry](https://github.com/mealie-recipes/mealie/pkgs/container/mealie)

- linux/amd64
- linux/arm64

!!! warning "32bit Support"

    Due to a build dependency limitation, Mealie is not supported on 32bit ARM systems. If you're running into this limitation on a newer Raspberry Pi, please consider upgrading to a 64bit operating system on the Raspberry Pi.

## Migrating From Other V1 Versions

We've gone through a few versions of Mealie v1 deployment targets. We have settled on a single container deployment, and we've begun publishing the nightly container on github containers. If you're looking to move from the old nightly (split containers _or_ the omni image) to the new nightly, there are a few things you need to do:

1. Take a backup just in case!
2. Replace the image for the API container with `ghcr.io/mealie-recipes/mealie:v2.4.1`
3. Take the external port from the frontend container and set that as the port mapped to port `9000` on the new container. The frontend is now served on port 9000 from the new container, so it will need to be mapped for you to have access.
4. Restart the container

For an example of what these changes look like, see the new [SQLite](./sqlite.md) or [PostgreSQL](./postgres.md) docker-compose examples. The container swap should be seemless, at least that's our hope!

## Step 1: Deployment Type

SQLite is a popular, open source, self-contained, zero-configuration database that is the ideal choice for Mealie when you have 1-20 Users and your concurrent write operations will be some-what limited.

PostgreSQL might be considered if you need to support many concurrent users. In addition, some features are only enabled on PostgreSQL, such as fuzzy search.

You can find the relevant ready to use docker-compose files for supported installations at the links below.

- [SQLite](./sqlite.md)
- [PostgreSQL](./postgres.md)

## Step 2: Setting up your files.

The following steps were tested on a Ubuntu 20.04 server, but should work for most other Linux distributions. These steps are not required, but this is how I generally will setup services on my server.

1. SSH into your server and navigate to the home directory of the user you want to run Mealie as. If that is your current user, you can use `cd ~` to ensure you're in the right directory.
2. Create a directory called `docker` and navigate into it: `mkdir docker && cd docker` (this is optional, if you organize your docker installs separate from everything else)
3. Do the same for mealie: `mkdir mealie && cd mealie`
4. Create a docker-compose.yaml file in the mealie directory: `touch docker-compose.yaml`
5. Use the text editor of your choice to edit the file and copy the contents of the docker-compose template for the deployment type you want to use: `nano docker-compose.yaml` or `vi docker-compose.yaml`

## Step 3: Customizing The `docker-compose.yaml` files.

After you've decided setup the files it's important to set a few ENV variables to ensure that you can use all the features of Mealie. I recommend that you verify and check that:

- [x] You've configured the relevant ENV variables for your database selection in the `docker-compose.yaml` files.
- [x] You've configured the [SMTP server settings](./backend-config.md#email) (used for invitations, password resets, etc). You can setup a [google app password](https://support.google.com/accounts/answer/185833?hl=en) if you want to send email via gmail.
- [x] You've set the [`BASE_URL`](./backend-config.md#general) variable.
- [x] You've set the `DEFAULT_EMAIL`, `DEFAULT_GROUP`, and `DEFAULT_HOUSEHOLD` variables.

## Step 4: Startup

After you've configured your database and updated the `docker-compose.yaml` files, you can start Mealie by running the following command in the directory where you've added your `docker-compose.yaml`.

```bash
$ docker compose up -d
```

You should see the containers start up without error. You should now be able to access the Mealie frontend at [http://localhost:9925](http://localhost:9925).

!!! warning "Default Username"

    Note that the default username (below) has been changed from previous versions

!!! tip "Default Credentials"

    **Username:** changeme@example.com

    **Password:** MyPassword

## Step 5: Validate Installation

After the startup is complete, you should see a login screen. Use the default credentials above to log in and navigate to `/admin/site-settings`. Here, you'll find a summary of your configuration details and their respective status. Before proceeding, you should validate that the configuration is correct. For any warnings or errors the page will display an error and notify you of what you need to verify.

## Step 6: Backup

While v1.0.0 is a great step to data-stability and security, it's not a backup. Mealie provides a full site data backup mechanism through the UI.

These backups are just plain .zip files that you can download from the UI or access via the mounted volume on your system. For complete data protection you MUST store these backups somewhere safe, outside of the server where they are deployed.

## Appendix

### Docker Tags

See all available tags on [GitHub](https://github.com/mealie-recipes/mealie/pkgs/container/mealie).

`ghcr.io/mealie-recipes/mealie:nightly`

The nightly build are the latest and greatest builds that are built directly off of every commit to the `mealie-next` branch and as such may contain bugs. These are great to help the community catch bugs before they hit the stable release or if you like living on the edge.

`ghcr.io/mealie-recipes/mealie:<version>`

We also provide versioned containers that allow to pin to a specific release. Each time a new release is built a new tag will be pushed with the version. These are great to pin to a specific version and allows you to have absolute control on when you upgrade your container.

`ghcr.io/mealie-recipes/mealie:latest`

The latest tag provides the latest released image of Mealie.

---

**These tags no are long updated**

`mealie:frontend-v1.0.0beta-x` **and** `mealie:api-v1.0.0beta-x`

These are the tags for the latest beta release of the frontend docker-container. These are currently considered the latest and most stable releases and the recommended way of using Mealie.

`mealie:frontend-nightly`**and** `mealie:api-nightly`

The nightly build are the latest and greatest builds that are built directly off of every commit to the `mealie-next` branch and as such may contain bugs. These are great to help the community catch bugs before they hit the stable release or if you like living on the edge.
