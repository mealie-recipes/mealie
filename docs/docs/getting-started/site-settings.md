# Site Settings Panel
!!! danger
    As this is still a **BETA** It is recommended that you backup your data often and store in more than one place. Ad-hear to backup best practices with the [3-2-1 Backup Rule](https://en.wikipedia.org/wiki/Backup)


## Theme Settings
Color themes can be created and set from the UI in the settings page. You can select an existing color theme or create a new one. On creation of a new color theme, the default colors will be used, then you can select and save as you'd like. By default the "default" theme will be loaded for all new users visiting the site. All created color themes are available to all users of the site. Theme Colors will be set for both light and dark modes.

![](../gifs/theme-demo.gif)

!!! note
    Theme data is stored in localstorage in the browser. Calling "Save colors and apply theme will refresh the localstorage with the selected theme as well save the theme to the database. 





## Meal Planner Webhooks
Meal planner webhooks are post requests sent from Mealie to an external endpoint. The body of the message is the Recipe JSON of the scheduled meal. If no meal is schedule, no request is sent. The webhook functionality can be enabled or disabled as well as scheduled. Note that you must "Save Webhooks" prior to any changes taking affect server side. 


