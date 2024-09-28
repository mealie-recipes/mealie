# Development: Database Changes

This document is open to improvement; please share any insights you have/develop.

## Overview

When modifying the database, you will most likely need to change the files under `/mealie/db/models/`.
How exactly you need to modify it is of course highly contextual to the change you're making.

## Using Alembic to generate upgrade script

In your dev container you can run something like (change the message) `task py:migrate -- "Add creation tag to group preferences"` to have Alembic generate an upgrade script for you.

Alembic's script migration isn't perfect, so you will need to review which changes are generated. You will also need to make sure any custom operations work on both SQLite and Postgres.
There are some known limitations with our migrations and Alembic's auto-generation, which is accounted for in `/alembic/env.py`. If any of your migrations overlap with the columns in `include_object`, you may need to manually adjust the migration.
