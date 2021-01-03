# Working Todos

Frontend
- [ ] .Vue file reorganized into something that makes sense
- [ ] Recipe Print Page 
- [x] Catch 400 / bad response on create from URL
- [ ] Recipe Editor Data Validation CLient Side
- [x] Favicon
- [x] Rename Window
- [ ] Add version indicator and notification for new version available
- [ ] Enhanced Search Functionality
- [ ] Organize Home Page my Category, ideally user selectable.

Backend
- [x] Add Debug folder for writing the last pulled recipe data to. 
- [x] Recipe Editor Data Validation Server Side
- [ ] Normalize Recipe data on scrape
- [ ] Support how to Sections
- [ ] Export Markdown on Auto backups
- [ ] Recipe request by category/tags
- [ ] Add Additional Migrations, See mealie/services/migrations/chowdown.py for examples of how to do this.
  - [ ] Open Eats [See Issue #4](https://github.com/hay-kot/mealie/issues/4)
  - [ ] NextCloud [See Issue #14](https://github.com/hay-kot/mealie/issues/14)

# Draft Changelog
## v0.0.1

General
- Fixed opacity issues with marked steps - [mtoohey31](https://github.com/mtoohey31)
- Updated Favicon
- Renamed Frontend Window
- Added Debug folder to dump scraper data prior to processing. 

Recipes
- Added user feedback on bad URL. Now when
- Better backend data validation for updating recipes, avoid small syntax errors corrupting database entry. [Issue #8](https://github.com/hay-kot/mealie/issues/8)
- Fixed spacing issue while editing new recipes in JSON
