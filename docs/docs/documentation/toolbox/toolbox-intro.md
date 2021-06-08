#Toolbox
The toolbox gives you multiple options to clean-up and organize your recipes. You can get notified through different channels.
You can access it through the 'Settings' menu or through the [dashboard](../admin/dashboard.md).


## Category and Tag Editor
The 'Categories' and 'Tags' tab give you the option to bulk assign categories and tags to multiple recipes. You could also remove the unused ones or title case them all.

![Toolbox-Categories](../../assets/img/Toolbox-Categories.webp)

## Bulk Organize
The 'Organize' tab can be used to show all of the items that do not have any category or tag assigned.

![Toolbox-Organize](../../assets/img/Toolbox-Organize.webp)

## External Notifications

### Apprise

Using the [Apprise](https://github.com/caronc/apprise/) library Mealie is able to provided notification services for nearly every popular service. Some of our favorites are...

- [Gotify](https://github.com/caronc/apprise/wiki/Notify_gotify)
- [Discord](https://github.com/caronc/apprise/wiki/Notify_discord)
- [Home Assistant](https://github.com/caronc/apprise/wiki/Notify_homeassistant)
- [Matrix](https://github.com/caronc/apprise/wiki/Notify_matrix)
- [Pushover](https://github.com/caronc/apprise/wiki/Notify_pushover)

But there are some many to choose from! Take a look at their wiki for information on how to create their URL formats and that you can use to create a notification integration in Mealie.


### Subscribe Events
There are several categories of events that mealie logs that can be broadcast with the notifications feature. You can also see a feed of your events in the Admin Dashboard

- General Events
    - Application Startup
- Recipe Events
    - Create Recipe
    - Delete Recipe
- Database Events
    - Export/Import
    - Database Initialization
- Scheduled Events
    - MealPlan Webhooks Sent
- Group Events
    - Create/Delete Groups
- User Events
    - User Creation
    - User Sign-up
    - Sign-up Token Creation
    - Invalid login attempts

In most cases the events will also provide details on which user performed the action. Now you'll know when your grandma deletes your favorite recipe!

!!! info
This is a new feature and we are still working through all the possibilities of events. if you have an idea for an event let us know!


### Creating a New Notification

New events can be created and viewed in admin Toolbox `/admin/toolbox?tab=event-notifications`. Select the "+ Notification" button and you'll be provided with a dialog. Complete the form using the URL for the service you'd like to connect to. Before saving be sure to use the test feature.

!!! tip
The feedback provided from the test feature is only an indicated of if the URL you provided is valid, not if the message was successfully sent. Be sure to check the notification feed for the test message.

![Add Notification Image](../../assets/img/add-notification.webp)


### Examples

#### Discord
![Discord](../../assets/img/discord-notification-example.webp)

#### Gotify
![Gotify](../../assets/img/gotify-notification-example.webp)