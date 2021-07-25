# Updating Mealie

!!! warning "Read The Release Notes"
    You MUST read the release notes prior to upgrading your container. Currently Mealie provides no database migrations as doing so would slow down development and hinder major changes that may need to happen prior to v1.0.0. Mealie has a robust backup and restore system for managing your data.

    ### Before Upgrading
     - Read The Release Notes
     - Identify Breaking Changes
     - Create a Backup and Download from the UI
     - Upgrade

## Backing Up Your Data

[See Backups and Restore Section](../admin/backups-and-exports.md) for details on backing up your data

## Docker
For all setups using Docker the updating process looks something like this

- Stop the container using docker-compose down
- Pull the latest image using docker-compose pull
- Start the container again using docker-compose up -d
