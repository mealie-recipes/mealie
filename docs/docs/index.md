# About The Project

<p align="center">
  <a href="https://github.com/hay-kot/mealie">
  </a>
  <p align="center">
    <a href="https://github.com/hay-kot/mealie/issues">Report Bug</a>
    ·
    <a href="https://github.com/hay-kot/mealie/issues">Request Feature</a>
  </p>
</p>

<!-- ABOUT THE PROJECT -->

![Product Name Screen Shot][product-screenshot]

**Mealie** is a self hosted recipe manager and meal planner with a RestAPI backend and a reactive frontend application built in Vue for a pleasant user experience for the whole family. Easily add recipes into your database by providing the url and mealie will automatically import the relevant data or add a family recipe with the UI editor.  

Mealie also provides an API for interactions from 3rd party applications. **Why does my recipe manager need an API?** An API allows integration into applications like [Home Assistant](https://www.home-assistant.io/) that can act as notification engines to provide custom notifications based of Meal Plan data to remind you to defrost the chicken, marinade the steak, or start the CrockPot. Additionally, you can access any available API from the backend server. To explore the API spin up your server and navigate to http://yourserver.com/docs for interactive API documentation. 

[Remember to join the Discord](https://discord.gg/R6QDyJgbD2)! 

!!! note
    In some of the demo gifs the styling may be different than the finale application. demos were done during development prior to finale styling.

!!! warning
    Note that this is a **ALPHA** release and that means things may break and or change down the line. I'll do my best to make sure that any API changes are thoughtful and necessary in order not to break things. Additionally, I'll do my best to provide a migration path if the database schema ever changes. That said, one of the nice things about MongoDB is that it's flexible!



### Main Features
#### Recipes
  - Automatic web scrapping for common recipe platforms
  - Interactive API Documentation thanks to [FastAPI](https://fastapi.tiangolo.com/) and [Swagger](https://petstore.swagger.io/)
  - UI Recipe Editor
  - JSON Recipe Editor in browser
  - Custom tags and categories
  - Rate recipes
  - Add notes to recipes
  - Migration From Other Platforms
    - Chowdown
    - Open Eats - **Coming Soon**
#### Meal Planner
  - Random Meal plan generation based off categories
  - Expose notes in the API to allow external applications to access relevant information for meal plans
  
#### Database Import / Export
  - Easily Import / Export your recipes from the UI
  - Export recipes in markdown format for universal access
    - Use the default or a custom jinja2 template

### Built With

* [Vue.js](https://vuejs.org/)
* [Vuetify](https://vuetifyjs.com/en/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [MongoDB](https://www.mongodb.com/)
* [Docker](https://www.docker.com/)



<!-- ROADMAP -->
## Road Map

[See Roadmap](2.0 - roadmap)



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**. Especially test. Literally any tests.

If you are not a coder, you can still contribute financially. financial contributions help me prioritize working on this project over others and helps me know that there is a real demand for the project. 

<a href="https://www.buymeacoffee.com/haykot" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact
Project Link: [https://github.com/hay-kot/mealie](https://github.com/hay-kot/mealie)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Talk Python Training for helping me learn python](https://training.talkpython.fm/)
* [Academind for helping me learn Javascript and Vue.js](https://academind.com/)


<!-- MARKDOWN LINKS & IMAGES -->
[product-screenshot]: img/home_screenshot.png
