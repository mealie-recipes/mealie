# Updating Mealie

!!! warning "Read The Release Notes"
    You MUST read the release notes prior to upgrading your container. Mealie has a robust backup and restore system for managing your data. Pre-v1.0.0 versions of Mealie use a different database structure, so if you are upgrading from pre-v1.0.0 to v1.0.0, you MUST backup your data and then re-import it. Even if you are already on v1.0.0, it is strongly recommended to backup all data before updating.

    ### Before Upgrading
     - Read The Release Notes
     - Identify Breaking Changes
     - Create a Backup and Download from the UI
     - Upgrade

## Upgrading to Mealie v1
If you are upgrading from pre-v1.0.0 to v1.0.0, make sure you read [Migrating to Mealie v1](./migrating-to-mealie-v1.md)!

## Backing Up Your Data

[See Backups and Restore Section](../getting-started/usage/backups-and-restoring.md) for details on backing up your data

## Docker
For all setups using Docker the updating process looks something like this

- Stop the container using docker-compose down
- Pull the latest image using `docker-compose pull`
- Start the container again using `docker-compose up -d`
