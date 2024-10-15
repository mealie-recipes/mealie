# Updating Mealie

!!! warning "Read The Release Notes"
    You MUST read the release notes prior to upgrading your container. Mealie has a robust backup and restore system for managing your data. Pre-v1.0.0 versions of Mealie use a different database structure, so if you are upgrading from pre-v1.0.0 to v1.0.0, you MUST backup your data and then re-import it. Even if you are already on v1.0.0, it is strongly recommended to backup all data before updating.

    ### Before Upgrading
     - Read The Release Notes
     - Identify Breaking Changes
     - Create a Backup and Download from the UI
     - Upgrade

## Upgrading to Mealie v1 or later
If you are upgrading from pre-v1.0.0 to v1.0.0 or later (v2.0.0, etc.), make sure you read [Migrating to Mealie v1](./migrating-to-mealie-v1.md)!

## Backing Up Your Data

[See Backups and Restore Section](../getting-started/usage/backups-and-restoring.md) for details on backing up your data

## Docker
For all setups using Docker, the updating process looks something like this:

- Stop the container using `docker compose down`
- If you are not using the latest tag, change the version (image tag) in your docker-compose file
- Pull the latest image using `docker compose pull`
- Start the container again using `docker compose up -d`
