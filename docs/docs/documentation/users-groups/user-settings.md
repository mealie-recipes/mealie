# User Settings

A user will be able to access 3 sections in their admin panel. The user profile, themes, group/meal-plan settings section. 

## Profile Settings
In as users profile they are able to

- Change Display Name
- Change Email
- Update Password
- View Their Group
- Upgrade Profile Picture (Experimental)

## Themes
Color themes can be created and set from the UI in the users settings page. You can select an existing color theme or create a new one. On creation of a new color theme, the default colors will be used, then you can select and save as you'd like. By default the "default" theme will be loaded for all new users visiting the site. All created color themes are available to all users of the site. Theme Colors will be set for both light and dark modes.

![](../../assets/gifs/theme-demo-v2.gif)

!!! tip
    Theme data is stored in local storage in the browser. Calling "Save colors and apply theme will refresh the local storage with the selected theme as well save the theme to the database. 

## Group & Meal Plan
In the meal planner section a user can select categories to be used as apart of the random recipe selector in the meal plan creator. If no categories are selected, all recipes will be used

Meal planner webhooks are post requests sent from Mealie to an external endpoint. The body of the message is the Recipe JSON of the scheduled meal. If no meal is schedule, no request is sent. The webhook functionality can be enabled or disabled as well as scheduled. Note that you must "Save" prior to any changes taking affect server side. 
