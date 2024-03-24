---
tags:
  - Security
---

# Security Considerations

This page is a collection on security considerations for Mealie. It mostly deals with reported issues and how it's possible to mitigate them, (if possible). Note that this page is for you to use as a guide for how secure you want to make this application. It's important to note that if you

1. Disable Sign-Ups
2. Run behind a VPN
3. Use a strong password
4. Don't host for malicious users

Most of these will not apply to you. Use your best judgement when deciding what to do.

## Denial of Service

By default, the API is **not** rate limited. This leaves Mealie open to a potential **Denial of Service Attack**. While it's possible to perform a **Denial of Service Attack** on any endpoint, there are a few key endpoints that are more vulnerable than others.

- `/api/recipes/create-url`
- `/api/recipes/{id}/image`

These endpoints are used to scrape data based off a user provided Url. It is possible for a malicious user issue multiple requests to download an arbitrarily large external file (e.g a Debian ISO) and sufficiently saturate a CPU assigned to the container. While we do implement some protections against this by chunking the response, and using a timeout strategy, it's still possible to overload the CPU if an attacker issues multiple requests concurrently.

### Mitigation

If you'd like to mitigate this risk, we suggest that you rate limit the API in general, and these endpoints with strick rate limits. You can do this by utilizing a reverse proxy. See the following links to get started

- [Traefik](https://doc.traefik.io/traefik/middlewares/http/ratelimit/)
- [Nginx](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
- [Caddy](https://caddyserver.com/docs/modules/http.handlers.rate_limit)

## Server Side Request Forgery

- `/api/recipes/create-url`
- `/api/recipes/{id}/image`

Given these nature of these APIs it's possible to perform a **Server Side Request Forgery** attack. This is where a malicious user can issue a request to an internal network resource, and potentially exfiltrate data. We _do_ perform some checks to mitigate access to resources within your network but at the end of the day, users of Mealie are allowed to trigger Http requests on **your server**.

### Mitigation

If you'd like to mitigate this risk, we suggest that you isolate the container that Mealie is running in to ensure that it's access to internal resources is limited only to what is required. _Note that Mealie does require access to the internet for recipes imports._ You might consider isolating Mealie from your home network entirely and only allowing access to the external internet.
