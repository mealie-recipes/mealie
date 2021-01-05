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

Frontend
- [ ] .Vue file reorganized into something that makes sense
- [ ] Recipe Print Page 
- [x] Catch 400 / bad response on create from URL
- [ ] Recipe Editor Data Validation Client Side
- [x] Favicon
- [x] Rename Window
- [ ] Add version indicator and notification for new version available
- [ ] Enhanced Search Functionality
- [ ] Organize Home Page my Category, ideally user selectable.

Backend
- [x] Add Debug folder for writing the last pulled recipe data to. 
- [x] Recipe Editor Data Validation Server Side
- [ ] Normalize Recipe data on scrape
- [ ] Support how to Sections and how to steps
- [ ] Export Markdown on Auto backups
- [ ] Recipe request by category/tags
- [ ] Add Additional Migrations, See mealie/services/migrations/chowdown.py for examples of how to do this.
  - [ ] Open Eats [See Issue #4](https://github.com/hay-kot/mealie/issues/4)
  - [ ] NextCloud [See Issue #14](https://github.com/hay-kot/mealie/issues/14)

# Draft Changelog
## v0.0.2

General
- Fixed opacity issues with marked steps - [mtoohey31](https://github.com/mtoohey31)
- Improved documentation
- Fixed hot-reloading development environment - [grssmnn](https://github.com/grssmnn)
