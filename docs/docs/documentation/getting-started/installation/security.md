---
tags:
  - Security
---

# Security Considerations

This page is a collection of security considerations for Mealie. It mostly deals with reported issues and how it's possible to mitigate them. Note that this page is for you to use as a guide for how secure you want to make your deployment. It's important to note that most of these will not apply to you, if you:

1. Run behind a VPN
2. Use a strong password
3. Disable Sign-Ups
4. Don't host for malicious users

Use your best judgement when deciding what to do.

## Denial of Service

By default, the API is **not** rate limited. This leaves Mealie open to a potential **Denial of Service Attack**. While it's possible to perform a **Denial of Service Attack** on any endpoint, there are a few key endpoints that are more vulnerable than others.

- `/api/recipes/create/url`
- `/api/recipes/create/ai`
- `/api/recipes/{id}/image`

These endpoints are used to scrape data based off a user provided URL. It is possible for a malicious user to issue multiple requests to download an arbitrarily large external file (e.g a Debian ISO) and sufficiently saturate a CPU assigned to the container. While we do implement some protections against this by chunking the response, and using a timeout strategy, it's still possible to overload the CPU if an attacker issues multiple requests concurrently.

### Mitigation

If you'd like to mitigate this risk, we suggest that you rate limit the API in general, and apply strict rate limits to these endpoints. You can do this by utilizing a reverse proxy. See the following links to get started:

- [Traefik](https://doc.traefik.io/traefik/middlewares/http/ratelimit/)
- [Nginx](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
- [Caddy](https://caddyserver.com/docs/modules/http.handlers.rate_limit)

## Server Side Request Forgery

Several features make your Mealie server send requests to URLs that users provide. A **Server Side Request Forgery** (SSRF) attack abuses this to make the server reach resources on your internal network that the user can't reach directly.

### Recipe imports, images, webhooks, and recipe actions

These requests can only reach public addresses by default:

- Recipe imports from a URL (`/api/recipes/create/url`, `/api/recipes/create/ai`)
- Recipe image and asset downloads (`/api/recipes/{id}/image`)
- Webhooks
- Recipe actions
- OIDC profile images

Mealie refuses a target that resolves to a private, loopback, link-local, or carrier-grade NAT (`100.64.0.0/10`, used by Tailscale) address, and checks every redirect. To let these features reach a trusted internal host, add it to `HTTP_ALLOW_LIST`. To block a target, including a public one, add it to `HTTP_DISALLOW_LIST`. See [Backend Configuration](./backend-config.md#application-security).

### Notifiers and webhooks

Notifiers send through the [Apprise](https://github.com/caronc/apprise/wiki) library and **can reach internal hosts by design**. Many self-hosted instances send notifications to services on the same network, such as ntfy, Gotify, Home Assistant, or a local mail server. `HTTP_ALLOW_LIST` and `HTTP_DISALLOW_LIST` do not apply to notifiers.

Only users with the **Manage household** permission can view, create, change, or test notifiers and webhooks. Give this permission only to users you trust to make your server send requests. See [Permissions and Public Access](../usage/permissions-and-public-access.md).

To limit which notification services can be used, set `APPRISE_ALLOWED_SCHEMAS` to the Apprise schemas you want to allow, for example `APPRISE_ALLOWED_SCHEMAS=ntfys,discord`. Mealie refuses to save a notifier with any other schema, and skips existing notifiers that no longer match. Leaving out the generic `json`, `form`, and `xml` schemas (and their secure variants) removes the most direct way to send arbitrary HTTP requests, but services you allow that take a custom host, such as `ntfy` or `mailto`, can still reach internal addresses.

### Mitigation

If you'd like to limit this risk further, isolate the container that Mealie runs in so that it can reach only the internal resources it needs. _Note that Mealie does require access to the internet for recipe imports._ You might consider isolating Mealie from your home network entirely and only allowing access to the external internet.

## Reporting a Vulnerability

Please report security issues privately through [GitHub's private vulnerability reporting](https://github.com/mealie-recipes/mealie/security/advisories/new), not as public issues. See the [security policy](https://github.com/mealie-recipes/mealie/security/policy) for details.
