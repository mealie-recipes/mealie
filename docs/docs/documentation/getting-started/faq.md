# Frequently Asked Questions

## How can I change the theme?

You can change the theme by settings the environment variables on the frontend container. 

Links:

- [Frontend Theme](/mealie/documentation/getting-started/installation/frontend-config#themeing)

## How can I change the language?

Languages need to be set on the frontend and backend containers as ENV variables.

Links

- [Frontend Config](/mealie/documentation/getting-started/installation/frontend-config/)
- [Backend Config](/mealie/documentation/getting-started/installation/backend-config/)

## How can I change the Login Session Timeout?

Login session can be configured by setting the `TOKEN_TIME` variable on the backend container.

- [Backend Config](/mealie/documentation/getting-started/installation/backend-config/)

## Can I serve Mealie on a subpath?

No. Due to limitations from the Javascript Framework, mealie doesn't support serving Mealie on a subpath.

## Can I install Mealie without docker? 

Yes, you can install Mealie on your local machine. HOWEVER, it is recommended that you don't. Managing non-system versions of python, node, and npm is a pain. Moreover updating and upgrading your system with this configuration is unsupported and will likely require manual interventions. If you insist on installing Mealie on your local machine, you can use the links below to help guide your path.

- [Advanced Installation](/mealie/documentation/getting-started/installation/advanced/)

## How I can attach an Image or Video to a Recipe? 

Yes. Mealie's Recipe Steps and other fields support the markdown syntax and therefor supports images and videos. To attach an image to the recipe, you can upload it as an asset and use the provided copy button to generate the html image tag required to render the image. For videos, Mealie provides no way to host videos. You'll need to host your videos with another provider and embed them in your recipe. Generally, the video provider will provide a link to the video and the html tag required to render the video. For example, youtube provides the following link that works inside a step. You can adjust the width and height attributes as necessary to ensure a fit.

```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/nAUwKeO93bY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
```