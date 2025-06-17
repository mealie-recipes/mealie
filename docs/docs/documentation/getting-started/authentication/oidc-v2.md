# OpenID Connect (OIDC) Authentication

:octicons-tag-24: v2.0.0

!!! note
    Breaking changes to OIDC Authentication were introduced with Mealie v2. Please see the below for [migration steps](#migration-from-mealie-v1x).

    Looking instead for the docs for Mealie :octicons-tag-24: v1.x? [Click here](./oidc.md)

Mealie supports 3rd party authentication via [OpenID Connect (OIDC)](https://openid.net/connect/), an identity layer built on top of OAuth2. OIDC is supported by many Identity Providers (IdP), including:

- [Authentik](https://goauthentik.io/integrations/sources/oauth/#openid-connect)
- [Authelia](https://www.authelia.com/integration/openid-connect/mealie/)
- [Keycloak](https://www.keycloak.org/docs/latest/securing_apps/#_oidc)
- [Okta](https://www.okta.com/openid-connect/)

## Account Linking

Signing in with OAuth will automatically find your account in Mealie and link to it. If a user does not exist in Mealie, then one will be created (if enabled), but will be unable to log in with any other authentication method. An admin can configure another authentication method for such a user.

If a user previously accessed Mealie via credentials and you want to no longer allow users to log in with `LDAP` or `Mealie` credentials, then you can set the user's *Authentication Method* to `OIDC`. Conversely, if a user's auth method is not `OIDC`, then they can still log in with whatever their auth method is as well as OIDC.

## Provider Setup

Before you can start using OIDC Authentication, you must first configure a new client application in your identity provider. Your identity provider must support the OAuth **Authorization Code flow with PKCE**. The steps will vary by provider, but generally, the steps are as follows.

1. Create a new client application
    - The Provider type should be OIDC or OAuth2
    - The Grant type should be `Authorization Code`
    - The Client type should be `confidential` (you should have a **Client Secret**)

2. Configure redirect URI

    The redirect URI(s) that are needed:

    1. `http(s)://DOMAIN:PORT/login`
    2. `http(s)://DOMAIN:PORT/login?direct=1`
        1. This URI is only required if your IdP supports [RP-Initiated Logout](https://openid.net/specs/openid-connect-rpinitiated-1_0.html) such as Keycloak. You may also be able to combine this into the previous URI by using a wildcard: `http(s)://DOMAIN:PORT/login*`

    The redirect URI(s) should include any URL that Mealie is accessible from. Some examples include

        http://localhost:9091/login
        https://mealie.example.com/login

3. Configure allowed scopes

    The scopes required are `openid profile email`

    If you plan to use the [groups](#groups) to configure access within Mealie, you will need to also add the scope defined by the `OIDC_GROUPS_CLAIM` environment variable. The default claim is `groups`

## Mealie Setup

Take the client id and your discovery URL and update your environment variables to include the required OIDC variables described in [Installation - Backend Configuration](../installation/backend-config.md#openid-connect-oidc).

You might also want to set ALLOW_PASSWORD_LOGIN to false, to hide the username+password inputs, if you want to allow logins only via OIDC.

### Groups

There are two (optional) [environment variables](../installation/backend-config.md#openid-connect-oidc) that can control which of the users in your IdP can log in to Mealie and what permissions they will have. Keep in mind that these groups **do not necessarily correspond to groups in Mealie**. The groups claim is configurable via the `OIDC_GROUPS_CLAIM` environment variable. The groups should be **defined in your IdP** and be returned in the configured claim value.

`OIDC_USER_GROUP`: Users must be a part of this group (within your IdP) to be able to log in.

`OIDC_ADMIN_GROUP`: Users that are in this group (within your IdP) will be made an **admin** in Mealie. Users in this group do not need to be in the `OIDC_USER_GROUP`

## Examples

Example configurations for several Identity Providers have been provided by the Community in the [GitHub Discussions](https://github.com/mealie-recipes/mealie/discussions/categories/oauth-provider-example).

If you don't see your provider and have successfully set it up, please consider [creating your own example](https://github.com/mealie-recipes/mealie/discussions/new?category=oauth-provider-example) so that others can have a smoother setup.


## Migration from Mealie v1.x

**High level changes**

- A Client Secret is now required
- CORS is no longer a requirement since all authentication happens server-side
- A user will be successfully authenticated if they are part of *either* `OIDC_USER_GROUP` or `OIDC_ADMIN_GROUP`. Admins no longer need to be part of both groups
- ID Token signing algorithm is now inferred using the `id_token_signing_alg_values_supported` metadata from the discovery URL

### Changes in your IdP

**Required**

- You must change the Mealie client in your IdP to be **confidential**. The option is different for every provider, but you need to obtain a **client secret**.

**Optional**

- You may now also remove the `OIDC_USER_GROUP` from your admin users if you so desire. Users within the `OIDC_ADMIN_GROUP` will now be able to successfully authenticate with only that group.
- You may remove any CORS configuration. i.e. configured origins

### Changes in Mealie

**Required**

- After obtaining the **client secret** from your IdP, you must add it to Mealie using the `OIDC_CLIENT_SECRET` environment variable or via [docker secrets](../installation/backend-config.md#docker-secrets). This secret will not be logged on startup.

**Optional**

- Remove `OIDC_SIGNING_ALGORITHM` from your environment. It will no longer have any effect.
