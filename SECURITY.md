# Security Policy

## Supported Versions

Since this software is still considered beta/WIP support is always only given for the latest version. Security patches are only available for the latest version and not back-ported to older versions.

## Reporting a Vulnerability

This repository has [private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/privately-reporting-a-security-vulnerability) enabled. To confidentially report a security issue, click the **"Report a vulnerability"** button on the [Security tab](../../security/advisories/new) of this repository. This allows you to submit details directly to the maintainers without public disclosure.

For non-sensitive issues or general feedback, feel free to open a GitHub issue or contribute a fix via pull request.

Please do not open public issues for security reports.

## Intended Behavior

The following behavior is by design and is not treated as a vulnerability. See the [security documentation](https://docs.mealie.io/documentation/getting-started/installation/security/) for details and the settings that control it.

### Notifiers can reach internal hosts

Notifiers send through [Apprise](https://github.com/caronc/apprise) and can target any host, including private and loopback addresses, because self-hosted instances often notify services on the same network. Only users with the **Manage household** permission can create, change, or test notifiers. Admins can limit the usable services with `APPRISE_ALLOWED_SCHEMAS`.

### Webhooks and recipe actions can send requests to URLs a user chooses

Only users with the **Manage household** permission can manage webhooks, and only users with the **Organize group data** permission can manage recipe actions. Requests to private, loopback, link-local, and carrier-grade NAT addresses are blocked by default.

### Admin-allowed targets are reachable

Hosts or networks that an admin adds to `HTTP_ALLOW_LIST` can be reached by recipe imports, webhooks, recipe actions, and image downloads.

### Recipe imports from a URL make the server fetch that URL

Requests to non-public addresses are blocked, but the API is not rate limited. Use a reverse proxy to rate limit if you need to.

### Notifier requests are blind

Mealie does not return the response from a notification service to the user, so a notifier that reaches an internal host cannot read data from it. A report about notifiers must show impact beyond the server sending the request.

### Recipe media is served to anyone with its URL

Recipe images, timeline images, and assets under `/api/media/recipes/` do not require a login, so they load on public and shared recipe pages. These URLs contain the recipe's random UUID, which cannot be guessed or enumerated. Anyone who has seen a recipe, for example through a share link or while it was public, can keep using its media URLs after the share is revoked or the recipe becomes private.

## In Scope

Reports that show a way around these controls, for example reaching a blocked address without an admin allowing it, or managing notifiers without the required permission, are in scope.
