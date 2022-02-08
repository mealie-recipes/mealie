[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Docker Pulls][docker-pull]][docker-pull]
[![CodeFactor](https://www.codefactor.io/repository/github/hay-kot/mealie/badge)](https://www.codefactor.io/repository/github/hay-kot/mealie)
[![Docker Build Production](https://github.com/hay-kot/mealie/actions/workflows/dockerbuild.release.yml/badge.svg)](https://github.com/hay-kot/mealie/actions/workflows/dockerbuild.release.yml)
[![Project Tests Production](https://github.com/hay-kot/mealie/actions/workflows/test-all.yml/badge.svg)](https://github.com/hay-kot/mealie/actions/workflows/test-all.yml)
[![Docker Build Dev](https://github.com/hay-kot/mealie/actions/workflows/dockerbuild.dev.yml/badge.svg?branch=dev)](https://github.com/hay-kot/mealie/actions/workflows/dockerbuild.dev.yml)
[![Project Tests Dev](https://github.com/hay-kot/mealie/actions/workflows/test-all.yml/badge.svg?branch=dev)](https://github.com/hay-kot/mealie/actions/workflows/test-all.yml)
  

  
<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/hay-kot/mealie">
<svg style="width:100px;height:100px" viewBox="0 0 24 24">
    <path fill="currentColor" d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z" />
</svg>
  </a>

  <h3 align="center">Mealie</h3>

  <p align="center">
    A Place for All Your Recipes
    <br />
    <a href="https://hay-kot.github.io/mealie/"><strong>Explore the docs »</strong></a>
  <a href="https://github.com/hay-kot/mealie">
  </a>
    <br />
    <a href="https://mealie-demo.hay-kot.dev/">View Demo</a>
    ·
    <a href="https://github.com/hay-kot/mealie/issues">Report Bug</a>    
    ·
    <a href="https://hay-kot.github.io/mealie/api/redoc/">API</a>
    ·
    <a href="https://github.com/hay-kot/mealie/issues">
    Request Feature
    </a>    
    ·
    <a href="https://hub.docker.com/r/hkotel/mealie"> Docker Hub
    </a>
</p>




[![Product Name Screen Shot][product-screenshot]](https://example.com)

# About The Project

Mealie is a self hosted recipe manager and meal planner with a RestAPI backend and a reactive frontend application built in Vue for a pleasant user experience for the whole family. Easily add recipes into your database by providing the url and Mealie will automatically import the relevant data or add a family recipe with the UI editor. Mealie also provides an API for interactions from 3rd party applications. 

[Remember to join the Discord](https://discord.gg/QuStdQGSGK)! 



## Key Features
- 🔍 Fuzzy search
- 🏷️ Tag recipes with categories or tags for flexible sorting
- 🕸 Import recipes from around the web by URL
- 💪 Powerful bulk Category/Tag assignment
- 📱 Beautiful Mobile Views
- 📆 Create Meal Plans
- 🛒 Generate shopping lists
- 🐳 Easy setup with Docker
- 🎨 Customize your interface with color themes 
- 💾 Export all your data in any format with Jinja2 Templates
- 🔒 Keep your data safe with automated backup and easy restore options
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
Some users of static-site generator applications like ChowDown have expressed concerns about their data being stuck in a database. Considering this is a new project it is a valid concern to be worried about your data. Mealie specifically addresses this concern by provided automatic daily backups that export your data in json, plain-text markdown files, and/or custom Jinja2 templates. **This puts you in controls of how your data is represented** when exported from Mealie, which means you can easily migrate to any other service provided Mealie doesn't work for you. 

As to why we need a database?

- **Developer Experience:** Without a database a lot of the work to maintain your data is taken on by the developer instead of a battle tested platform for storing data. 
- **Multi User Support:** With a solid database as backend storage for your data Mealie can better support multi-user sites and avoid read/write access errors when multiple actions are taken at the same time. 


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**. Especially test. Literally any tests. See the [Contributors Guide](https://hay-kot.github.io/mealie/contributors/non-coders/) for help getting started.

If you are not a coder, you can still contribute financially. financial contributions help me prioritize working on this project over others and helps me know that there is a real demand for project development. 

<a href="https://www.buymeacoffee.com/haykot" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 107px !important;" ></a>

<!-- LICENSE -->
## License
Distributed under the MIT License. See `LICENSE` for more information.


## Sponsors

Huge thanks to all the sponsors of this project on [Github Sponsors](https://github.com/sponsors/hay-kot) and Buy Me a Coffee. Without you this project would surely not be possible.

Thanks to Linode for providing Hosting for the Demo, Beta, and Documentation sites! Another big thanks to JetBrains for providing their IDEs for development.

<div align='center'>
  <img height="200" src="docs/docs/assets/img/sponsors-linode.svg" />
  <img height="200" src="docs/docs/assets/img/sponsors-jetbrains.png" />
</div>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/hay-kot/mealie.svg?style=flat-square
[docker-pull]: https://img.shields.io/docker/pulls/hkotel/mealie
[contributors-url]: https://github.com/hay-kot/mealie/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/hay-kot/mealie.svg?style=flat-square
[forks-url]: https://github.com/hay-kot/mealie/network/members
[stars-shield]: https://img.shields.io/github/stars/hay-kot/mealie.svg?style=flat-square
[stars-url]: https://github.com/hay-kot/mealie/stargazers
[issues-shield]: https://img.shields.io/github/issues/hay-kot/mealie.svg?style=flat-square
[issues-url]: https://github.com/hay-kot/mealie/issues
[license-shield]: https://img.shields.io/github/license/hay-kot/mealie.svg?style=flat-square
[license-url]: https://github.com/hay-kot/mealie/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/hay-kot
[product-screenshot]: docs/docs/assets/img/home_screenshot.png
