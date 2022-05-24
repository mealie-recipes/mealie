!!! info "Feature Set"
    This isn't an exhaustive list of features within Mealie, but it does capture the most important, overarching features that Mealie offers.


## Recipes

### Creating Recipes

Mealie offers two main ways to create recipes. You can use the integrated recipe-scraper to create recipes from hundreds of websites, or you can create recipes manually using the recipe editor.

[Demo](https://beta.mealie.io/recipe/create?tab=url){ .md-button .md-button--primary .align-right }

### Importing Recipes

Mealie supports importing recipes from a few other sources besides websites. Currently the following sources are supported:

- Mealie Pre v1
- Nextcloud Cookbooks
- Paprika
- Chowdown

You can access these options on your installation at the `/group/migrations` page on your installation. If you'd like to see another source added, feel free to request so on Github.


[Demo](https://beta.mealie.io/group/data/foods){ .md-button .md-button--primary }


### Organizing Recipes

Mealie has a robust and flexible recipe organization system with a few different ways to organize your recipes in a way that fits your household.

#### Categories


Categories are the overarching organizer for recipes. You can assign as many categories as you'd like to a recipe, but we recommend that you try to limit the categories you assign to a recipe to one or two. This helps keep categories as focused as possible while still allowing you to find recipes that are related to each other. For example, you might assign a recipe to the category **Breakfast**, **Lunch**, **Dinner**, or **Side**.

[Demo](https://beta.mealie.io/recipes/categories){ .md-button .md-button--primary }

#### Tags

Tags, are nearly identical to categories in function but play a secondary role in some cases. As such, we recommend that you use tags freely to help you organize your recipes by more specific topics. For example, if a recipe can be frozen or is a great left-over meal, you could assign the tags **frozen** and **left-over** and easily filter for those at a later time.

[Demo](https://beta.mealie.io/recipes/tags){ .md-button .md-button--primary }

#### Tools

Tools, are another way that some users like to organize their recipes. If a recipe requires some specific equipment if can be helpful to assign the tools to the recipes. This is particularly useful for things that are less common, like a pressure cooker, or a sous vide.

Each of the above organizers can be filtered in searches, and have their own pages where you can view all the recipes that are associated with those organizers.

[Demo](https://beta.mealie.io/recipes/tools){ .md-button .md-button--primary }

#### Cookbooks

Mealie also has the concept of cookbooks. These can be created inside of a group and can use a cross section of Categories, Tags, and Tools to filter recipes and view them in one specific page. Cookbooks are a great way to keep a supset of recipes easily accessible to you. You can think of them as a saved search results page. While most examples are simple, you can use as many organizers to filter a cookbook as you'd like.

#### Examples:

- Main Courses: This cookbooks has all the recipes that have the **Dinner** category
- Pasta Sides: Recipes that have both the **Side** category and the **Pasta** tag
- Dessert Breads: Recipes that have both the **Bread** category and the **Dessert** tag

[Demo](https://beta.mealie.io/group/cookbooks){ .md-button .md-button--primary }

## Meal Planning

Mealie uses a calendar like view to help you plan your meals. It shows you the previous day, and the next 6 days by default. You can toggle through the calendar by clicking the arrows on the top of the page. In editor mode, you can use the random recipe buttons, or manually add an entry.

!!! tip
    You can also add a "Note" type entry to your meal-plan when you want to include something that might not have a specific recipes. This is great for leftovers, or for ordering out.

[Demo](https://beta.mealie.io/group/mealplan/planner){ .md-button .md-button--primary }

### Planner Rules

The meal planner has the concept of plan rules. These offer a flexible way to use your organizers to customize how a random recipe is inserted into your meal plan. You can set rules to restrict the pool of recipes based on the Tags and/or Categories of a recipe. Additionally, since meal plans have a Breakfast, Lunch, Dinner, and Snack labels you can specifically set a rule to be active for a **specific meal type** or even a **specific day of the week.**

[Demo](https://beta.mealie.io/group/mealplan/settings){ .md-button .md-button--primary }

## Shopping Lists

The shopping lists feature is a great way to keep track of what you need to buy for your next meal. You can add items directly to the shopping list, or link a recipe and all of it's ingredients to track meals during the week.

!!! warning
    At this time there isn't a tight integration between meal-plans and shopping lists, however it's something we have planned for the future.


[Demo](https://beta.mealie.io/shopping-lists){ .md-button .md-button--primary }


## Data Management

Managing a robust collection of recipes inevitable requires a lot of data. Mealie has a robust data management system that allows you to easily some of the more important data sets in your collection. Here's some of the features that are available in the `group/data/<type>` pages:

- Recipes
    - Bulk Actions
        - Export
        - Tag
        - Categorize
        - Delete
- Foods
    - Import/Seed your database with a collection of over 200 foods!
    - Merge Foods into a single food entry
    - Export as JSON
- Units
    - Import/Seed your database with a collection of the most common units of measurement
    - Merge Units into a single unit entry
    - Export as JSON

[Demo](https://beta.mealie.io/group/data/foods){ .md-button .md-button--primary }

## Server Administration

### Site Settings

The site settings page contains general information about your installtion like the application version, some configuration details, and some utilities to help you confirm your installation is working as expected. For example, you can use the Email Configuration section to validate that your email credentials are setup correctly and that the email service is working as expected. Additionally, there is a docker-volume utility that will confirm your volumes are configured and shared correctly between the front and backend of the application.

[Demo](https://beta.mealie.io/admin/site-settings){ .md-button .md-button--primary }

### Users and Group

There is a small management area for users and groups that allows you to create, edit, and delete users and groups.

[Demo](https://beta.mealie.io/admin/manage/users){ .md-button .md-button--primary }

### Backups

The backups page provides a full system backup of your installation including all assets and images related to recipes. These are archived into a zip file and stored on the server but can also be downloaded through the UI. Due to some issues in the past Mealie no longer performs automatic backups, **it is advised that during setup you also setup a backup strategy to ensure your data is not lost.**


[Demo](https://beta.mealie.io/admin/backups){ .md-button .md-button--primary }


!!! note
    This is **NOT** the same as backups in v0.5.4. We've greatly simplified how backups are managed at the database level and we are now taking a full snapshot of the database and restoring it. If you're looking to export your recipes to move to an alternative service, this is likely not the way you'll want to export that data. You'll likely want to handle that through the group data exports page or through the API itself.

    [Group Data Exports](https://beta.mealie.io/group/data/recipes){ .md-button .md-button--primary }
