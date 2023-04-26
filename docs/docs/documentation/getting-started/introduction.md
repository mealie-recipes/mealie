# About The Project

!!! warning "Mealie v1 Beta Release"
    This documentation is for the Mealie v1 Beta release and is not final. As such, it may contain incomplete or incorrect information. You should understand that installing Mealie v1 Beta is a work in progress and while we've committed to maintaining the database schema and provided migrations, we are still in the process of adding new features, and robust testing to ensure the application works as expected.

    You should likely find bugs, errors, and unfinished pages within the application. To find the current status of the release you can checkout the [project on github](https://github.com/hay-kot/mealie/projects/7) or reach out on discord.


Mealie is a self hosted recipe manager and meal planner with a RestAPI backend and a reactive frontend application built in Vue for a pleasant user experience for the whole family. Easily add recipes into your database by providing the url and Mealie will automatically import the relevant data or add a family recipe with the UI editor. Mealie also provides an API for interactions from 3rd party applications.

[Remember to join the Discord](https://discord.gg/QuStdQGSGK)


## Key Features
- 🔍 Smart search, mix & match of "quoted literal searches" and keyword search. Fuzzy search ("is it brocolli or broccoli?") is also available when using a Postgres database.
- 🏷️ Tag recipes with categories or tags for flexible sorting
- 🕸 Import recipes from around the web by URL
- 📱 Progressive Web App
- 📆 Create Meal Plans
- 🛒 Generate shopping lists
- 🐳 Easy setup with Docker
- 🎨 Customize your interface with color themed layouts
- 💾 Export all your data in any format with Jinja2 Templates, with easy data restoration from the user interface.
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
See the [Frequently Asked Questions page](./faq.md)


## Built With

* [Vue.js](https://vuejs.org/)
* [Vuetify](https://vuetifyjs.com/en/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Docker](https://www.docker.com/)


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, develop, and create. Any contributions you make are **greatly appreciated**. See the [Contributors Guide](../../contributors/non-coders.md) for help getting started.

If you are not a coder, you can still contribute financially. Financial contributions help me prioritize working on this project over others and help me to know that there is a real demand for project development.

<a href="https://www.buymeacoffee.com/haykot" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
