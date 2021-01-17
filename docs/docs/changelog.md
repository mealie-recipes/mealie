# Release Notes

## v0.1.0 - Initial Beta
### Bug Fixes
  - Fixed Can't delete recipe after changing name - Closes Issue #67
  - Fixed No image when added by URL, and can;t add an image - Closes Issue #66
  - Fixed Images saved with no way to delete when add recipe via URL fails - Closes Issue #43

### Features
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

### Break Changes

!!! error "Breaking Changes"
    As I've adopted the SQL database model I find that using 2 different types of databases will inevitably hinder development. As such after release v0.1.0 support for mongoDB will no longer be available. Prior to upgrading to v0.2.0 you will need to export your site and import after updating. This should be a painless process and require minimal intervention on the users part. Moving forward we will do our best to minimize changes that require user intervention like this and make updates a smooth process. 


## v0.0.2 - Pre-release Second Patch
A quality update with major props to [zackbcom](https://github.com/zackbcom) for working hard on making the theming just that much better!

### Bug Fixes
  - Fixed empty backup failure without markdown template
  - Fixed opacity issues with marked steps - [mtoohey31](https://github.com/mtoohey31)
  - Fixed hot-reloading development environment - [grssmnn](https://github.com/grssmnn)
  - Fixed recipe not saving without image - Issue #7 + Issue #54
  - Fixed parsing error on image property null - Issue #43

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
  - Improved recipe parsing - Issue #51
  - User feedback on backup importing

## v0.0.1 - Pre-release Patch
### General
  - Updated Favicon
  - Renamed Frontend Window
  - Added Debug folder to dump scraper data prior to processing. 

### Recipes
  - Added user feedback on bad URL
  - Better backend data validation for updating recipes, avoid small syntax errors corrupting database entry. [Issue #8](https://github.com/hay-kot/mealie/issues/8)
  - Fixed spacing issue while editing new recipes in JSON

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