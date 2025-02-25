# Backups and Restores

Mealie provides an integrated mechanic for doing full installation backups of the database. 

Navigate to Settings > Backups or manually by adding `/admin/backups` to your instance URL.

From this page, you will be able to: 

- See a list of available backups
- Create a backup
- Upload a backup
- Delete a backup (Confirmation Required)
- Download a backup
- Perform a restore

!!! tip
    If you're using Mealie with SQLite all your data is stored in the /app/data/ folder in the container. You can easily perform entire site backups by stopping the container, and backing up this folder with your chosen tool. This is the **best** way to backup your data.

## Restoring from a Backup

To restore from a backup it needs to be uploaded to your instance which can be done through the web portal. On the top left of the page you'll see an upload button. Click this button and select the backup file you want to upload and it will be available to import shortly. You can alternatively use one of the backups you see on the screen, if one exists.

Before importing it's critical that you understand the following:

- This is a destructive action and will delete all data in the database
- This action cannot be undone
- If this action is successful you will be logged out and you will need to log back in to complete the restore

!!! tip
    If for some reason the restore does not succeed, you can review the logs of what the issue may be, download the backup .ZIP and edit the contents of database.json to potentially resolve the issue. For example, if you receive an error restoring 'shopping-list' you can edit out the contents of that list while allowing other sections to restore. If you would like any assistance on this, reach out over Discord.

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
