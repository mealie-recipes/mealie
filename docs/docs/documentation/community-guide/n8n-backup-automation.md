# Automating Backups with n8n

!!! info
This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

> [n8n](https://github.com/n8n-io/n8n) is a free and source-available fair-code licensed workflow automation tool. Alternative to Zapier or Make, allowing you to use a UI to create automated workflows.

This example workflow:

1. Backups Mealie every morning via an API call
2. Deletes all but the last 7 backups

> [!CAUTION]
> This only automates the backup function, this does not backup your data to anywhere except your local instance. Please make sure you are backing up your data to an external source.

---

![screenshot](../../assets/img/n8n/n8n-mealie-backup.png)

# Setup

## Deploying n8n

Follow the relevent guide in the [n8n Documentation](https://docs.n8n.io/)

## Importing n8n workflow

1. In n8n, add a new workflow
2. In the top right hit the 3 dot menu and select 'Import from URL...'

![screenshot](../../assets/img/n8n/n8n-workflow-import.png)

4. Paste `https://github.com/mealie-recipes/mealie/blob/mealie-next/docs/docs/assets/other/n8n/n8n-mealie-backup.json` and click Import
5. Click through the nodes and update the URLs for your environment

## API Credentials

#### Generate Mealie API Token

1. Head to https://mealie.example.com/user/profile/api-tokens
   > If you dont see this screen make sure that "Show advanced features" is checked under https://mealie.example.com/user/profile/edit
2. Under token name, enter the name of the token i.e. 'n8n' and hit Generate
3. Copy and keep this API Token somewhere safe, this is like your password!

#### Setup Credentials in n8n

> [n8n Docs](https://docs.n8n.io/credentials/add-edit-credentials/)

1. Create a new "Header Auth" Credential

![screenshot](../../assets/img/n8n/n8n-cred-app.png)

3. In the connection screen set - Name as `Authorization` - Value as `Bearer {INSERT MEALIE API KEY}`

![screenshot](../../assets/img/n8n/n8n-cred-connection.png)

4. In the workflow you created, for the "Run Backup", "Get All backups", and "Delete Oldies" nodes, update:
   - Authentication to `Generic Credential Type`
   - Generic Auth Type to `Header Auth`
   - Header Auth to `Mealie API` or whatever you named your credentials
