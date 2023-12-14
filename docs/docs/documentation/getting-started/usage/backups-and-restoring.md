# Backups and Restoring

Mealie provides an integrated mechanics for doing full installation backups of the database. Navigate to `/admin/backups` to

- See a list of available backups
- Perform a backups
- Restore a backup

!!! tip
    If you're using Mealie with SQLite all your data is stored in the /app/data/ folder in the container. You can easily perform entire site backups by stopping the container, and backing up this folder with your chosen tool. This is the **best** way to backup your data.

## Restoring from a Backup

To restore from a backup it needs to be uploaded to your instance, this can be done through the web portal. On the lower left hand corner of the backups data table you'll see an upload button. Click this button and select the backup file you want to upload and it will be available to import shortly.

Before importing it's critical that you understand the following:

- This is a destructive action and will delete all data in the database
- This action cannot be undone
- If this action is successful you will be logged out and you will need to log back in to complete the restore

!!! warning
    Prior to beta-v5 using a mis-matched version of the database backup will result in an error that will prevent you from using the instance of Mealie requiring you to remove all data and reinstall. Post beta-v5 performing a mismatched restore will throw an error and alert the user of the issue.

### Postgres Note

Restoring the Database when using Postgres requires Mealie to be configured with a postgres **superuser** account. This is due to our usage of massive deleting of data in the database and temporarily setting roles to perform the restore. To perform a restoration on Postgres you will need to _temporarily_ set the Mealie user to a superuser account.

```sql
ALTER USER mealie WITH SUPERUSER;

# Run restore from Mealie

ALTER USER mealie WITH NOSUPERUSER;
```

For more information see [GitHub Issue #1500](https://github.com/mealie-recipes/mealie/issues/1500)
