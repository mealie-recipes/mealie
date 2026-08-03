# Trusted Proxy Header Authentication (SSO)

:octicons-tag-24: (not yet released)

Trusted proxy header authentication lets Mealie authenticate a user using a header supplied by a trusted reverse proxy.

When enabled, Mealie will automatically login an existing user from a configured request header (for example, `Remote-User`).

## Security Model

This feature assumes your reverse proxy is the trust boundary.

- Clients should not be able to reach Mealie directly.
- Your proxy **must** strip client-supplied identity headers and set its own trusted headers.
- `TRUSTED_PROXY` must be configured correctly.

If your proxy is misconfigured, identity header spoofing may be possible.

## Required Settings

Configure these variables in backend configuration:

- `PROXY_AUTH_ENABLED=true`
- `PROXY_AUTH_HEADER=Remote-User` (or your chosen header name)
- `TRUSTED_PROXY=<single IP>`

Notes:

- `TRUSTED_PROXY` must be a single IP address
- CIDRs, comma-separated lists and `*` are not supported when trusted proxy header authentication is enabled

Any value other than a single IP address will disable trusted proxy header auth for safety reasons.

## Request Flow and Auth Precedence

For authenticated API routes:

1. Mealie first checks for a valid Mealie session token (bearer or cookie).
2. If no valid token is present, Mealie will attempt to match the user supplied in `PROXY_AUTH_HEADER`.
3. If neither path authenticates, Mealie returns `401`.

Notes:

- If an invalid token is supplied, Mealie returns `401` and does not fall back to proxy header auth.
- Mealie will not automatically create a user that does not exist. The header value must match an existing user.

## User Matching

When proxy-header auth is attempted:

1. Mealie reads the configured header (`PROXY_AUTH_HEADER`).
2. Mealie matches the header value to an existing user:
   - first by `username` (case-insensitive)
   - then by `email` (case-insensitive)

If no user matches, authentication fails.

## Header Behavior

- `PROXY_AUTH_HEADER` is used as configured (no whitespace trimming).
- HTTP header names are case-insensitive in request lookup.

## Authelia Example

Example deployment with Authelia in front of Mealie, with the proxy forwarding identity to Mealie as `Remote-User`.

High-level setup:

1. User authenticates with Authelia
2. Proxy (e.g. haproxy) at 10.0.0.5 forwards request to Mealie and sets `Remote-User`
3. Uvicorn trusts forwarded headers only from `TRUSTED_PROXY`
4. Mealie maps `Remote-User` to an existing Mealie user

Example Mealie env:

```env
PROXY_AUTH_ENABLED=true
PROXY_AUTH_HEADER=Remote-User
TRUSTED_PROXY=10.0.0.5
```

For exact Authelia/proxy configuration syntax, follow your proxy and Authelia docs.

## Troubleshooting

- Proxy auth never activates:
  - Confirm `PROXY_AUTH_ENABLED=true`
  - Confirm `TRUSTED_PROXY` is a single IP and not `*`
  - Confirm Mealie receives traffic through your trusted reverse proxy
- Always getting `401`:
  - Confirm proxy sets `PROXY_AUTH_HEADER`
  - Confirm mapped user already exists in Mealie
  - Confirm invalid/stale bearer token is not being sent
- Header mismatch:
  - Verify `PROXY_AUTH_HEADER` name and whitespace in config
