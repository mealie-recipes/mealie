# Release Notes

## v0.2.0 - Now with Test!
This is, what I think, is a big release! Tons of new features and some great quality of life improvements with some additional features. You may find that I made promises to include some fixes/features in v0.2.0. The short of is I greatly underestimated the work needed to refactor the database to a usable state and integrate categories in a way that is useful for users. This shouldn't be taken as a sign that I'm dropping those feature requests or ignoring them. I felt it was better to push a release in the current state rather than drag on development to try and fulfil all of the promises I made. 

!!! warning "Upgrade Process"
    Database Breaks! I have not yet implemented a database migration service. As such, upgrades cannot be done by simply pulling the image. You must first export your recipes, update your deployment, and then import your recipes. This pattern is likely to be how upgrades take place prior to v1.0. After v1.0 migrations will be done automatically.

### Bug Fixes
  - Remove ability to save recipe with no name
  - Fixed data validation error on missing parameters
  - Fixed failed database initialization at startup - Closes #98
  - Fixed misaligned text on various cards
  - Fixed bug that blocked opening links in new tabs - Closes #122
  - Fixed router link bugs - Closes #122
  - Fixed navigation on keyboard selection - Closes #139

### Features and Improvements
  - 🐳 Dockerfile now 1/5 of the size!
  - 🌎 UI Language Selection + Additional Supported Language
  - **Home Page**
    - By default your homepage will display only the recently added recipes. You can configured sections to show on the home-screen based of categories on the settings page. 
    - A new sidebar is now shown on the main page that lists all the categories in the database. Clicking on them navigates into a page that shows only recipes. 
    - Basic Sort functionality has been added. More options are on the way! 
  - **Meal Planner**
    - Improved Search (Fuzzy Search)
    - New Scheduled card support 
  - **Recipe Editor**
    - Ingredients are now sortable via drag-and-drop
    - Known categories now show up in the dropdown - Closes 83
    - Initial code for data validation to prevent errors
  - **Migrations**
    - Card based redesign
    - Upload from the UI
    - Unified Chowdown / Nextcloud import process. (Removed Git as a dependency)
  - **API**
    - Category and Tag endpoints added
    - Major Endpoint refactor
    - Improved API documentation
    - Link to your Local API is now on your `/settings/site`. You can use it to explore your API. 

  - **Style**
    - Continued work on button/style unification
    - Adding icons to buttons
    - New Color Theme Picker UI

### Development
  - Fixed Vetur config file. Autocomplete in VSCode works!
  - File/Folder restructuring 
  - Added Prettier config
  - Fixed incorrect layout code
  - FastAPI Route tests for major operations - WIP (shallow testing)

### Breaking Changes 

!!! error "Breaking Changes"
    - API endpoints have been refactored to adhear to a more consistent standard. This is a WIP and more changes are likely to occur. 
    - Officially Dropped MongoDB Support
    - Database Breaks! We have not yet implemented a database migration service. As such, upgrades cannot be done by simply pulling the image. You must first export your recipes, update your deployment, and then import your recipes. This pattern is likely to be how upgrades take place prior to v1.0. After v1.0 migrations will be done automatically. 

## v0.1.0 - Initial Beta
### Bug Fixes
  - Fixed Can't delete recipe after changing name - Closes Closes #67
  - Fixed No image when added by URL, and can't add an image - Closes Closes #66
  - Fixed Images saved with no way to delete when add recipe via URL fails - Closes Closes #43

### Features
  - Additional Language Support
  - Improved deployment documentation
  - Additional database! SQlite is now supported! - Closes #48
  - All site data is now backed up.
  - Support for Prep Time, Total Time, and Cook Time field - Closes #63
  - New backup import process with support for themes and site settings
  - **BETA** ARM support! - Closes #69

### Code / Developer Improvements
  - Unified Database Access Layers
  - Poetry / pyproject.toml support over requirements.txt
  - Local development without database is now possible!
  - Local mkdocs server added to docker-compose.dev.yml
  - Major code refactoring to support new database layer
  - Global variable refactor

### Breaking Changes

- Internal docker port is now 80 instead of 9000. You MUST remap the internal port to connect to the UI. 

!!! error "Breaking Changes"
    As I've adopted the SQL database model I find that using 2 different types of databases will inevitably hinder development. As such after release v0.1.0 support for mongoDB will no longer be available. Prior to upgrading to v0.2.0 you will need to export your site and import after updating. This should be a painless process and require minimal intervention on the users part. Moving forward we will do our best to minimize changes that require user intervention like this and make updates a smooth process. 


## v0.0.2 - Pre-release Second Patch
A quality update with major props to [zackbcom](https://github.com/zackbcom) for working hard on making the theming just that much better!

### Bug Fixes
  - Fixed empty backup failure without markdown template
  - Fixed opacity issues with marked steps - [mtoohey31](https://github.com/mtoohey31)
  - Fixed hot-reloading development environment - [grssmnn](https://github.com/grssmnn)
  - Fixed recipe not saving without image - Closes #7 + Closes #54
  - Fixed parsing error on image property null - Closes #43

### General Improvements
  - Added Confirmation component to deleting recipes - [zackbcom](https://github.com/zackbcom)
  - Updated Theme backend - [zackbcom](https://github.com/zackbcom)
  - Added Persistent storage to vuex - [zackbcom](https://github.com/zackbcom)
  - General Color/Theme Improvements
      - More consistent UI
      - More minimalist coloring
  - Added API key extras to Recipe Data - [See Documentation](/api/api-usage/)
      - Users can now add custom json key/value pairs to all recipes via the editor for access in 3rd part applications. For example users can add a "message" field in the extras that can be accessed on API calls to play a message over google home. 
  - Improved image rendering (nearly x2 speed)
  - Improved documentation + API Documentation
  - Improved recipe parsing - Closes #51
  - User feedback on backup importing

## v0.0.1 - Pre-release Patch
### General
  - Updated Favicon
  - Renamed Frontend Window
  - Added Debug folder to dump scraper data prior to processing. 

### Recipes
  - Added user feedback on bad URL
  - Better backend data validation for updating recipes, avoid small syntax errors corrupting database entry. [Closes #8](https://github.com/hay-kot/mealie/issues/8)
  - Fixed spacing Closes while editing new recipes in JSON

## v0.0.0 - Initial Pre-release
The initial pre-release. It should be semi-functional but does not include a lot of user feedback You may notice errors that have no user feedback and have no idea what went wrong. 

### Recipes
  - Automatic web scrapping for common recipe platforms
  - Interactive API Documentation thanks to [FastAPI](https://fastapi.tiangolo.com/) and [Swagger](https://petstore.swagger.io/)
  - UI Recipe Editor
  - JSON Recipe Editor in browser
  - Custom tags and categories
  - Rate recipes
  - Add notes to recipes
  - Migration From Other Platforms
    - Chowdown
### Meal Planner
  - Random Meal plan generation based off categories
  - Expose notes in the API to allow external applications to access relevant information for meal plans
  
### Database Import / Export
  - Easily Import / Export your recipes from the UI
  - Export recipes in markdown format for universal access
    - Use the default or a custom jinja2 template