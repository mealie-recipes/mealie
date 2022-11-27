# Frequently Asked Questions

## Is it Safe to Upgrade Mealie?

Yes. If you are using the v1 branches (including beta), you can upgrade to the latest version of Mealie without performing a site Export/Restore. This process was required in previous versions of Mealie, however we've automated the database migration process to make it easier to upgrade. Not that if you were using the v0.5.x version, you CANNOT upgrade to the latest version automatically. You must follow the migration instructions in the documentation.

Links

- [Migration From v0.5.x](./migrating-to-mealie-v1.md)

## How can I change the theme?

You can change the theme by settings the environment variables on the frontend container.

Links:

- [Frontend Theme](./installation/frontend-config#themeing)

## How can I change the language?

Languages need to be set on the frontend and backend containers as ENV variables.

Links

- [Frontend Config](./installation/frontend-config/)
- [Backend Config](./installation/backend-config/)

## How can I change the Login Session Timeout?

Login session can be configured by setting the `TOKEN_TIME` variable on the backend container.

- [Backend Config](./installation/backend-config/)

## Can I serve Mealie on a subpath?

No. Due to limitations from the Javascript Framework, mealie doesn't support serving Mealie on a subpath.

## Can I install Mealie without docker?

Yes, you can install Mealie on your local machine. HOWEVER, it is recommended that you don't. Managing non-system versions of python, node, and npm is a pain. Moreover updating and upgrading your system with this configuration is unsupported and will likely require manual interventions. If you insist on installing Mealie on your local machine, you can use the links below to help guide your path.

- [Advanced Installation](./installation/advanced/)

## How i can attach an image or video to a Recipe?

Yes. Mealie's Recipe Steps and other fields support the markdown syntax and therefor supports images and videos. To attach an image to the recipe, you can upload it as an asset and use the provided copy button to generate the html image tag required to render the image. For videos, Mealie provides no way to host videos. You'll need to host your videos with another provider and embed them in your recipe. Generally, the video provider will provide a link to the video and the html tag required to render the video. For example, youtube provides the following link that works inside a step. You can adjust the width and height attributes as necessary to ensure a fit.

```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/nAUwKeO93bY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
```

## How can I unlock my account?

If your account has been locked by bad password attempts, you can use an administrator account to unlock another account. Alternatively you can unlock all account via a scripts within the container.

```shell
docker exec -it mealie-next bash

python /app/mealie/scripts/reset_locked_users.py
```

## How can I change my password

You can change your password by going to the user profile page and clicking the "Change Password" button. Alternatively you can use the following script to change your password via the CLI if you are locked out of your account.

```shell
docker exec -it mealie-next bash

python /app/mealie/scripts/change_password.py
```
