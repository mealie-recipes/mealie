# User Managemenet

## Overview
The basic relationship and ownership of recipes and meal plans is based on a user and group model where users are owners of recipes and groups are owners of meal plans. By default all users will be added to the default group. If a recipe is added through a migration or through a backup where no user exists ownership will be set to the default Admin, the original user provided by Mealie. To fully understand how to structure your users and groups, you'll need to know how each role is used in the website.

!!! info ":fontawesome-solid-user-cog: Admins"
    Mealie admins are super users that have access to all user data (excluding passwords). All admins can perform administrative tasks like adding users, resetting user passwords, backing up the database, migrating data, and managing site settings. Administrators can also access restricted recipes that are marked hidden or with editing disabled by the owner. 

!!! info ":fontawesome-solid-users: User Groups"
    User groups, or "family" groups are a collection of users that are associated together. Users belonging to groups will have access to their associated meal plans and associated pages. This is currently the only feature of groups. 

!!! info ":fontawesome-solid-user: User" 
    A single user created by an Admin that has basic privileges to edit their profile, create and edit recipes they own. Edit recipes that are not hidden and are marked editable.  

## Startup
On the first startup you'll need to login to Mealie using the default username and password `changeme@email.com` and `MyPassword` or the default set through the env variable. On first login you'll be required to reset your password. After resetting your password you should also change your email address as appropriate. This will be used for logins on all future requests. 

!!! tip 
    Your default password environmental variable will be the default password for all new users that are created. This is stored in plain text and should not be used **any where** else.
    

## Creating and Editing Users
// TODO

## Creating Groups
// TODO

## Password Reset
// TODO

## Examples Use Cases
// TODO