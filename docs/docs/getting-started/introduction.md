# About The Project

Mealie is a self hosted recipe manager and meal planner with a RestAPI backend and a reactive frontend application built in Vue for a pleasant user experience for the whole family. Easily add recipes into your database by providing the url and Mealie will automatically import the relevant data or add a family recipe with the UI editor. Mealie also provides an API for interactions from 3rd party applications. 

[Remember to join the Discord](https://discord.gg/R6QDyJgbD2)! 

!!! note
    In some of the demo gifs the styling may be different than the finale application. demos were done during development prior to finale styling.

!!! warning
    This is a **BETA** release and that means things may break and or change down the line. I'll do my best to make sure that any API changes are thoughtful and necessary in order not to break things. Additionally, I'll do my best to provide a migration path if the database schema ever changes. Do not use programs like watchtower to auto update your container. You **WILL** run into issues if you do this,


## Key Features
- 🔍 Powerful fuzzy search
- 🏷️ Tag recipes with categories or tags to flexible sorting
- ⬇️ Import recipes from around the web by URL
- 📱 Beautiful Mobile Views
- 📆 Create meal plans 
- 🛒 Generate shopping lists from meal plans
- 🐳 Easy setup with Docker
- 🎨 Customize your interface with color themes layouts
- ✉️ Export and import all your data in any formating with Jinja Tempaltes
- 🌍 localized in many languages
- ➕ Plus tons more!
    - Flexible API
        - Custom key/value pairs for recipes
        - Webhook support
        - Interactive API Documentation thanks to [FastAPI](https://fastapi.tiangolo.com/) and [Swagger](https://petstore.swagger.io/)
    - Raw JSON Recipe Editor
    - Migration from other platforms
        - Chowdown
        - Nextcloud Cookbook
    - Random meal plan generation

## FAQ

### Why An API?
An API allows integration into applications like [Home Assistant](https://www.home-assistant.io/) that can act as notification engines to provide custom notifications based of Meal Plan data to remind you to defrost the chicken, marinade the steak, or start the CrockPot. Additionally, you can access nearly any backend service via the API giving you total control to extend the application. To explore the API spin up your server and navigate to http://yourserver.com/docs for interactive API documentation. 

### Why a Database?
Some users of static-site generator applications have expressed concerns about their data being stuck in a database. Considering this is a new project it is a valid concern to be worried about your data. Mealie specifically addresses this concern by provided automatic daily backups that export your data in json, plain-text markdown files, and/or custom Jinja2 templates. This puts you in controls of how your data is represented when exported from Mealie, which means you can easily migrate to any other service provided Mealie doesn't work for you.

## Built With

* [Vue.js](https://vuejs.org/)
* [Vuetify](https://vuetifyjs.com/en/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Docker](https://www.docker.com/)

<!-- ROADMAP -->
## Road Map

[See Roadmap](/roadmap)


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, develop, and create. Any contributions you make are **greatly appreciated**. See the [Contributors Guide](https://hay-kot.github.io/mealie/contributors/developers-guide/code-contributions/) for help getting started.

If you are not a coder, you can still contribute financially. financial contributions help me prioritize working on this project over others and helps me know that there is a real demand for project development. 

<a href="https://www.buymeacoffee.com/haykot" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>


