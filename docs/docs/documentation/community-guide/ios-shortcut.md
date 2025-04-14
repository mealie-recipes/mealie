!!! info
  This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

An easy way to add recipes to Mealie from an Apple device is via an Apple Shortcut. This is a short guide to install an configure a shortcut able to add recipes via a link or image(s). 

*Note: if adding via images make sure to enable [Mealie's openai integration](https://docs.mealie.io/documentation/getting-started/installation/open-ai/)*

## Javascript can only be run via Shortcuts on the Safari browser on MacOS and iOS. If you do not use Safari you may skip this section
Some sites have begun blocking AI scraping bots, inadvertently blocking the recipe scraping library Mealie uses as well. To circumvent this, the shortcut uses javascript to capture the raw html loaded in the browser and sends that to mealie when possible.

**iOS**

Settings app -> apps -> Shortcuts -> Advanced -> Allow Running Scripts

**MacOS**

Shortcuts app -> Settings (CMD ,) -> Advanced -> Allow Running Scripts

## Initial setup
An API key is needed to authenticate with mealie. To create an api key for a user, navigate to http://YOUR_MEALIE_URL/user/profile/api-tokens. Alternatively you can create a key via the mealie home page by clicking the user's profile pic in the top left -> Api Tokens

The shortcut can be installed via **[This link](https://www.icloud.com/shortcuts/52834724050b42aebe0f2efd8d067360)**. Upon install, replace "MEALIE_API_KEY" with the API key generated previously and "MEALIE_URI" with the full URL used to access your mealie instance e.g. "http://10.0.0.5:9000" or "https://mealie.domain.com".

## Using the shortcut
Once installed, the shortcut will automatically appear as an option when sharing an image or webpage. It can also be useful to add the shortcut to the home screen of your device. If selected from the home screen or shortcuts app, a menu will appear with prompts to import via **taking photo(s)**, **selecting photo(s)**, **scanning a URL**, or **pasting a URL**. 

*Note: despite the mealie API being able to accept multiple recipe images for import it is currently impossible to send multiple files in 1 web request via Shortcuts. Instead, the shortcut combines the images into a singular, vertically-concatenated image to send to mealie. This can result in slightly less-accurate text recognition.*