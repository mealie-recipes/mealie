# Release Notes

## v0.0.1 - Pre-release Patch
General
- Updated Favicon
- Renamed Frontend Window
- Added Debug folder to dump scraper data prior to processing. 

Recipes
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