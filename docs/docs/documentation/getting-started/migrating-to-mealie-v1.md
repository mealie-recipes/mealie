# Migrating to Mealie v1 Release

The version 1 release of Mealie should be seen as an entirely different application. A whole host of changes have been made to improve the application, performance, and developer experience. Most of these improvements required significant breaking changes in the application that made a clean and easy migration impossible. However, if you've used Mealie prior to v1 there is a migration path to get most of your data from the old version to the new v1 version.

!!! info "Currently Supported Migration Data"
    Supporting more data is a work in progress, but not a current priority. I'm open to PR's to add support for additional data.

    - [x] Recipes
    - [x] Categories
    - [x] Tags
    - [ ] Users
    - [ ] Groups
    - [ ] Meal Plans
    - [ ] Cookbooks / Pages

## Step 1: Setting Up The New Application

Given the nature of the upgrade, it is highly recommended that you standup a new instance of mealie along side your current instance. This will allow you to migrate your data safely and quickly without any issues. Follow the instructions in the [Installation Checklist](../getting-started/installation/installation-checklist.md) to get started. Once that's complete and you can login, continue here with step 2.

## Step 2: Exporting Your Data from Pre-v1

In your instance of Mealie prior to v1, perform an export of your data in the Admin section. Be sure to include the recipes when performing the export. Checking additional items won't impact the migration, but they will be ignored if they are included.


## Step 3: Using the Migration Tool

In your new v1 instance, navigate to `/group/data/migrations` and select "Mealie" from the dropdown selector. Upload the exported data from your pre-v1 instance. Optionally, you can tag all the recipes you've imported with the `mealie_alpha` tag to help you identify them. Once the upload has finished, submit the form and your migration will begin. This may take some time, but when it's complete you'll be provided a new entry in hte "Previous Migrations" table below. Be sure to review the migration report to make sure everything was successful. There may be instances where some of the recipes were not imported, but the migration will still import all the successful recipes.

In most cases, it's faster to manually migrate the recipes that didn't take instead of trying to identify why the recipes failed to import. If you're experiencing issues with the migration tool, please open an issue on GitHub.

!!! note "Recipe Owners"
    When perform any migration, it will automatically assign the owner of the recipe to the user that performed the migration. All group members will still be able to access the recipe, however the owner has special permissions to lock the recipe from edits from other users.


## Step 4: Reviewing New Features

v1 Comes with a whole host of new features and improvements. Checkout the changelog to get a sense for what's new.

- [v1 Changelog](../../changelog/v1.0.0.md)
