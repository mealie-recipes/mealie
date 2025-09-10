!!! info
This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

Mealie supports adding the ingredients of a recipe to your [Bring](https://www.getbring.com/) shopping list, as you can
see [here](https://docs.mealie.io/documentation/getting-started/features/#recipe-actions).
However, for this to work, your Mealie instance needs to be exposed to the open Internet so that the Bring servers can access its information. If you don't want your server to be publicly accessible for security reasons, you can use the [Mealie-Bring-API](https://github.com/felixschndr/mealie-bring-api) written by a community member. This integration is entirely local and does not require any service to be exposed to the Internet.

This is a small web server that runs locally next to your Mealie instance, and instead of Bring pulling the data from you, it pushes the data to Bring. [Check out the project](https://github.com/felixschndr/mealie-bring-api) for more information and installation instructions.
