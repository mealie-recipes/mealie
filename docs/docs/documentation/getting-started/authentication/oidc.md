# OpenID Connect (OIDC) Authentication

:octicons-tag-24: v1.4.0

Mealie supports 3rd party authentication via [OpenID Connect (OIDC)](https://openid.net/connect/), an identity layer built on top of OAuth2. OIDC is supported by many Identity Providers (IdP), including:

- [Authentik](https://goauthentik.io/integrations/sources/oauth/#openid-connect)
- [Authelia](https://www.authelia.com/integration/openid-connect/mealie/)
- [Keycloak](https://www.keycloak.org/docs/latest/securing_apps/#_oidc)
- [Okta](https://www.okta.com/openid-connect/)

## Account Linking

Signing in with OAuth will automatically find your account in Mealie and link to it. If a user does not exist in Mealie, then one will be created (if enabled), but will be unable to log in with any other authentication method. An admin can configure another authentication method for such a user.

## Provider Setup

Before you can start using OIDC Authentication, you must first configure a new client application in your identity provider. Your identity provider must support the OAuth **Authorization Code flow with PKCE**. The steps will vary by provider, but generally, the steps are as follows.

1. Create a new client application
    - The Provider type should be OIDC or OAuth2
    - The Grant type should be `Authorization Code`
    - The Application type should be `Web` or `SPA`
    - The Client type should be `public`

2. Configure redirect URI

    The redirect URI(s) that are needed:

    1. `http(s)://DOMAIN:PORT/login`
    2. `http(s)://DOMAIN:PORT/login?direct=1`
        1. This URI is only required if your IdP supports [RP-Initiated Logout](https://openid.net/specs/openid-connect-rpinitiated-1_0.html) such as Keycloak. You may also be able to combine this into the previous URI by using a wildcard: `http(s)://DOMAIN:PORT/login*`

    The redirect URI(s) should include any URL that Mealie is accessible from. Some examples include

        http://localhost:9091/login
        https://mealie.example.com/login

3. Configure origins

    If your identity provider enforces CORS on any endpoints, you will need to specify your Mealie URL as an Allowed Origin.

4. Configure allowed scopes

    The scopes required are `openid profile email`

    If you plan to use the [groups](#groups) to configure access within Mealie, you will need to also add the scope defined by the `OIDC_GROUPS_CLAIM` environment variable. The default claim is `groups`

## Mealie Setup

Take the client id and your discovery URL and update your environment variables to include the required OIDC variables described in [Installation - Backend Configuration](../installation/backend-config.md#openid-connect-oidc).

### Groups

There are two (optional) [environment variables](../installation/backend-config.md#openid-connect-oidc) that can control which of the users in your IdP can log in to Mealie and what permissions they will have. Keep in mind that these groups **do not necessarily correspond to groups in Mealie**. The groups claim is configurable via the `OIDC_GROUPS_CLAIM` environment variable. The groups should be **defined in your IdP** and be returned in the configured claim value.

`OIDC_USER_GROUP`: Users must be a part of this group (within your IdP) to be able to log in.

`OIDC_ADMIN_GROUP`: Users that are in this group (within your IdP) will be made an **admin** in Mealie.

## Examples

Example configurations for several Identity Providers have been provided by the Community in the [GitHub Discussions](https://github.com/mealie-recipes/mealie/discussions/categories/oauth-provider-example).

If you don't see your provider and have successfully set it up, please consider [creating your own example](https://github.com/mealie-recipes/mealie/discussions/new?category=oauth-provider-example) so that others can have a smoother setup.
