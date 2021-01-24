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

Test
- [ ] Image Upload Test
- [ ] Rename and Upload Image Test

Frontend
- [ ] No Meal Today Page instead of Null 
- [ ] Recipe Print Page 
- [ ] Recipe Editor Data Validation Client Side
- [ ] Organize Home Page my Category, ideally user selectable.
- [ ] Advanced Search Page, draft started
  - [ ] Filter by Category
  - [ ] Filter by Tags
- [ ] Search Bar Results Redesign

Backend
- [ ] Database Import
  - [x] Recipes
  - [x] Images
  - [ ] Meal Plans
  - [x] Settings
  - [x] Themes
- [ ] Remove Print / Debug Code
- [ ] Support how to sections and how to steps
- [ ] Recipe request by category/tags

SQL
- [ ] Setup Database Migrations

# Draft Changelog
