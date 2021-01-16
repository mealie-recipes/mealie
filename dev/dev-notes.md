# Getting A Developer Instance Started
For the best experience developing I recommend using docker. I've used both WSL2 and Ubuntu to develop mealie and have had no issues with cross compatibility with docker. 2 Scripts are available along ith docker-compose files to make development instances easier. After cloning the repo you can set the scripts in /dev/scripts/ as executable and then use VSCode tasks to execute the scripts or execute them from the CLI. 

`docker-compose.dev.sh` Will spin up a development stack with hot-reloading enabled. 
`docker-compose.sh` Will spin up a production version of the stack.  

After the stack is running navigate to the [admin page localhost:9090/settings/site](http://localhost:9090/settings/site). On the Backups and Exports section import the backup labeled dev_sample_data_{DATE}.zip. This will give you some recipe data to work with. 

Once you're up and running you should be able to make changes and see them reflected on the frontend/backend. If you're not sure what to work on you can check:

- The Todo's below.
- The [Development Road Map](https://hay-kot.github.io/mealie/2.0%20-%20roadmap/)
- The [Current Open Issues](https://github.com/hay-kot/mealie/issues)

Don't forget to [join the Discord](https://discord.gg/R6QDyJgbD2)! 

# Todo's

Documentation
- [ ] V0.1.0 Release Notes
- [ ] Nextcloud Migration How To
- [ ] New Docker Setup with Sqlite
- [ ] Update Env Variables
- [ ] New Roadmap / Milestones

Frontend
- [ ] Prep / Cook / Total Time Indicator + Editor
- [ ] No Meal Today Page instead of Null 
- [ ] Recipe Print Page 
- [ ] Recipe Editor Data Validation Client Side
- [ ] Organize Home Page my Category, ideally user selectable.
- [ ] Advanced Search Page, draft started
- [ ] Search Bar Re-design
- [ ] Replace Backups card with something like Home Assistant
- [ ] Replace import card with something like Home Assistant
  - [ ] Select which imports to do

Backend
- [ ] Database Import
  - [x] Recipes
  - [x] Images
  - [ ] Meal Plans
  - [x] Settings
  - [x] Themes
- [ ] Remove Print / Debug Code
- [ ] Support how to Sections and how to steps
- [ ] Recipe request by category/tags


SQL
- [ ] Setup Database Migrations

# Draft Changelog
## v0.0.2

Bug Fixes
- Fixed opacity issues with marked steps - [mtoohey31](https://github.com/mtoohey31)
- Fixed hot-reloading development environment - [grssmnn](https://github.com/grssmnn)
- Fixed recipe not saving without image
- Fixed parsing error on image property null

General Improvements
- Added Confirmation component to deleting recipes - [zackbcom](https://github.com/zackbcom)
- Updated Theme backend - [zackbcom](https://github.com/zackbcom)
- Added Persistent storage to vuex - [zackbcom](https://github.com/zackbcom)
- General Color/Theme Improvements
  - More consistent UI
  - More minimalist coloring
- Added API Key Extras to Recipe Data
  - Users can now add custom json key/value pairs to all recipes via the editor for access in 3rd part applications. For example users can add a "message" field in the extras that can be accessed on API calls to play a message over google home. 
- Improved image rendering (nearly x2 speed)
- Improved documentation + API Documentation
- Improved recipe parsing
