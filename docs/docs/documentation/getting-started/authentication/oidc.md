# OpenID Connect (OIDC) Authentication

Mealie supports 3rd party authentication via [OpenID Connect (OIDC)](https://openid.net/connect/), an identity layer built on top of OAuth2. OIDC is supported by many identity providers, including:

- [Authentik](https://goauthentik.io/integrations/sources/oauth/#openid-connect)
- [Authelia](https://www.authelia.com/configuration/identity-providers/open-id-connect/)
- [Keycloak](https://www.keycloak.org/docs/latest/securing_apps/#_oidc)
- [Okta](https://www.okta.com/openid-connect/)

## Account Linking

Signing in with OAuth will automatically find your account in Mealie and link to it. If a user does not exist in Mealie, then one will be created (if enabled), but will be unable to log in with any other authentication method. An admin can configure another authentication method for such a user.

## Provider Setup

Before you can start using OIDC Authentication, you must first configure a new client application in your identity provider. Your identity provider must support the OAuth **Authorization Code** flow (with PKCE). The steps will vary by provider, but generally, the steps are as follows.

1. Create a new client application
    - The Provider type should be OIDC or OAuth2
    - The Grant type should be `Authorization Code`
    - The Application type should be `Web`
    - The Client type should be `public`

2. Configure redirect URI

    The only redirect URI that is needed is `http(s)://DOMAIN:PORT/login`

    The redirect URI should include any URL that Mealie is accessible from. Some examples include

        http://localhost:9091/login
        https://mealie.example.com/login

3. Configure origins

    If your identity provider enforces CORS on any endpoints, you will need to specify your Mealie URL as an Allowed Origin.

4. Configure allowed scopes

    The scopes required are `openid profile email groups`

## Mealie Setup

Take the client id and your discovery URL and update your environment variables to include the required OIDC variables described in [Installation - Backend Configuration](../installation/backend-config.md#openid-connect-oidc)

## Examples

### Authelia

Follow the instructions in [Authelia's documentation](https://www.authelia.com/configuration/identity-providers/open-id-connect/). Below is an example config

!!! warning

    This is only an example and not meant to be an exhaustive configuration. You should read read through the documentation and adjust your configuration as needed.

```yaml
identity_providers:
  oidc:
    access_token_lifespan: 1h
    authorize_code_lifespan: 1m
    id_token_lifespan: 1h
    refresh_token_lifespan: 90m
    enable_client_debug_messages: false
    enforce_pkce: public_clients_only
    cors:
      endpoints:
        - authorization
        - token
        - revocation
        - introspection
      allowed_origins:
        - https://mealie.example.com
      allowed_origins_from_client_redirect_uris: false
    clients:
      - id: mealie
        description: Mealie
        authorization_policy: one_factor
        redirect_uris:
          - https://mealie.example.com/login
        public: true
        grant_types:
          - authorization_code
        scopes:
          - openid
          - profile
          - groups
          - email
          - offline_access
```
