# Release Notes

## v0.0.2 - Pre-release Second Patch
A quality update with major props to [zackbcom](https://github.com/zackbcom) for working hard on making the theming just that much better!
### Bug Fixes
  - Fixed opacity issues with marked steps - [mtoohey31](https://github.com/mtoohey31)
  - Fixed hot-reloading development environment - [grssmnn](https://github.com/grssmnn)
  - Fixed recipe not saving without image
  - Fixed parsing error on image property null

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
  - Improved recipe parsing

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