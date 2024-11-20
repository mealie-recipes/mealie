# Backend Configuration

## API Environment Variables

### General

| Variables                     |        Default        | Description                                                                                        |
| ----------------------------- | :-------------------: | -------------------------------------------------------------------------------------------------- |
| PUID                          |          911          | UserID permissions between host OS and container                                                   |
| PGID                          |          911          | GroupID permissions between host OS and container                                                  |
| DEFAULT_GROUP                 |         Home          | The default group for users                                                                        |
| DEFAULT_HOUSEHOLD             |        Family         | The default household for users in each group                                                      |
| BASE_URL                      | http://localhost:8080 | Used for Notifications                                                                             |
| TOKEN_TIME                    |          48           | The time in hours that a login/auth token is valid                                                 |
| API_PORT                      |         9000          | The port exposed by backend API. **Do not change this if you're running in Docker**                |
| API_DOCS                      |         True          | Turns on/off access to the API documentation locally                                               |
| TZ                            |          UTC          | Must be set to get correct date/time on the server                                                 |
| ALLOW_SIGNUP<super>\*</super> |         false         | Allow user sign-up without token                                                                   |
| LOG_CONFIG_OVERRIDE           |                       | Override the config for logging with a custom path                                                 |
| LOG_LEVEL                     |         info          | Logging level (e.g. critical, error, warning, info, debug)                                         |
| DAILY_SCHEDULE_TIME           |         23:45         | The time of day to run daily server tasks, in HH:MM format. Use the server's local time, *not* UTC |

<super>\*</super> Starting in v1.4.0 this was changed to default to `false` as part of a security review of the application.

### Security

| Variables                   | Default | Description                                                                         |
| --------------------------- | :-----: | ----------------------------------------------------------------------------------- |
| SECURITY_MAX_LOGIN_ATTEMPTS |    5    | Maximum times a user can provide an invalid password before their account is locked |
| SECURITY_USER_LOCKOUT_TIME  |   24    | Time in hours for how long a users account is locked                                |

### Database

| Variables             | Default  | Description                                                             |
| --------------------- | :------: | ----------------------------------------------------------------------- |
| DB_ENGINE             |  sqlite  | Optional: 'sqlite', 'postgres'                                          |
| POSTGRES_USER         |  mealie  | Postgres database user                                                  |
| POSTGRES_PASSWORD     |  mealie  | Postgres database password                                              |
| POSTGRES_SERVER       | postgres | Postgres database server address                                        |
| POSTGRES_PORT         |   5432   | Postgres database port                                                  |
| POSTGRES_DB           |  mealie  | Postgres database name                                                  |
| POSTGRES_URL_OVERRIDE |   None   | Optional Postgres URL override to use instead of POSTGRES\_\* variables |

### Email

| Variables          | Default | Description                                       |
| ------------------ | :-----: | ------------------------------------------------- |
| SMTP_HOST          |  None   | Required For email                                |
| SMTP_PORT          |   587   | Required For email                                |
| SMTP_FROM_NAME     | Mealie  | Required For email                                |
| SMTP_AUTH_STRATEGY |   TLS   | Required For email, Options: 'TLS', 'SSL', 'NONE' |
| SMTP_FROM_EMAIL    |  None   | Required For email                                |
| SMTP_USER          |  None   | Required if SMTP_AUTH_STRATEGY is 'TLS' or 'SSL'  |
| SMTP_PASSWORD      |  None   | Required if SMTP_AUTH_STRATEGY is 'TLS' or 'SSL'  |

### Webworker

Changing the webworker settings may cause unforeseen memory leak issues with Mealie. It's best to leave these at the defaults unless you begin to experience issues with multiple users. Exercise caution when changing these settings

| Variables       | Default | Description                                                                      |
| --------------- | :-----: | -------------------------------------------------------------------------------- |
| UVICORN_WORKERS |    1    | Sets the number of workers for the web server. [More info here][unicorn_workers] |

### TLS

Use this only when mealie is run without a webserver or reverse proxy.

| Variables            | Default | Description              |
| -------------------- | :-----: | ------------------------ |
| TLS_CERTIFICATE_PATH |  None   | File path to Certificate |
| TLS_PRIVATE_KEY_PATH |  None   | File path to private key |

### LDAP

| Variables            | Default | Description                                                                                                                         |
| -------------------- | :-----: | ----------------------------------------------------------------------------------------------------------------------------------- |
| LDAP_AUTH_ENABLED    |  False  | Authenticate via an external LDAP server in addidion to built-in Mealie auth                                                        |
| LDAP_SERVER_URL      |  None   | LDAP server URL (e.g. ldap://ldap.example.com)                                                                                      |
| LDAP_TLS_INSECURE    |  False  | Do not verify server certificate when using secure LDAP                                                                             |
| LDAP_TLS_CACERTFILE  |  None   | File path to Certificate Authority used to verify server certificate (e.g. `/path/to/ca.crt`)                                       |
| LDAP_ENABLE_STARTTLS |  False  | Optional. Use STARTTLS to connect to the server                                                                                     |
| LDAP_BASE_DN         |  None   | Starting point when searching for users authentication (e.g. `CN=Users,DC=xx,DC=yy,DC=de`)                                          |
| LDAP_QUERY_BIND      |  None   | Optional bind user for LDAP search queries (e.g. `cn=admin,cn=users,dc=example,dc=com`). If `None` then anonymous bind will be used |
| LDAP_QUERY_PASSWORD  |  None   | Optional password for the bind user used in LDAP_QUERY_BIND                                                                         |
| LDAP_USER_FILTER     |  None   | Optional LDAP filter to narrow down eligible users (e.g. `(memberOf=cn=mealie_user,dc=example,dc=com)`)                             |
| LDAP_ADMIN_FILTER    |  None   | Optional LDAP filter, which tells Mealie the LDAP user is an admin (e.g. `(memberOf=cn=admins,dc=example,dc=com)`)                  |
| LDAP_ID_ATTRIBUTE    |   uid   | The LDAP attribute that maps to the user's id                                                                                       |
| LDAP_NAME_ATTRIBUTE  |  name   | The LDAP attribute that maps to the user's name                                                                                     |
| LDAP_MAIL_ATTRIBUTE  |  mail   | The LDAP attribute that maps to the user's email                                                                                    |

### OpenID Connect (OIDC)

:octicons-tag-24: v1.4.0

For usage, see [Usage - OpenID Connect](../authentication/oidc-v2.md)

| Variables                                         | Default | Description                                                                                                                                                                                                                                                                                            |
|---------------------------------------------------|:-------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| OIDC_AUTH_ENABLED                                 |  False  | Enables authentication via OpenID Connect                                                                                                                                                                                                                                                              |
| OIDC_SIGNUP_ENABLED                               |  True   | Enables new users to be created when signing in for the first time with OIDC                                                                                                                                                                                                                           |
| OIDC_CONFIGURATION_URL                            |  None   | The URL to the OIDC configuration of your provider. This is usually something like https://auth.example.com/.well-known/openid-configuration                                                                                                                                                           |
| OIDC_CLIENT_ID                                    |  None   | The client id of your configured client in your provider                                                                                                                                                                                                                                               |
| OIDC_CLIENT_SECRET <br/> :octicons-tag-24: v2.0.0 |  None   | The client secret of your configured client in your provider                                                                                                                                                                                                                                           |
| OIDC_USER_GROUP                                   |  None   | If specified, only users belonging to this group will be able to successfully authenticate. For more information see [this page](../authentication/oidc-v2.md#groups)                                                                                                                                  |
| OIDC_ADMIN_GROUP                                  |  None   | If specified, users belonging to this group will be able to successfully authenticate *and* be made an admin. For more information see [this page](../authentication/oidc-v2.md#groups)                                                                                                                |
| OIDC_AUTO_REDIRECT                                |  False  | If `True`, then the login page will be bypassed and you will be sent directly to your Identity Provider. You can still get to the login page by adding `?direct=1` to the login URL                                                                                                                    |
| OIDC_PROVIDER_NAME                                |  OAuth  | The provider name is shown in SSO login button. "Login with <OIDC_PROVIDER_NAME\>"                                                                                                                                                                                                                     |
| OIDC_REMEMBER_ME                                  |  False  | Because redirects bypass the login screen, you cant extend your session by clicking the "Remember Me" checkbox. By setting this value to true, a session will be extended as if "Remember Me" was checked                                                                                              |
| OIDC_USER_CLAIM                                   |  email  | This is the claim which Mealie will use to look up an existing user by (e.g. "email", "preferred_username")                                                                                                                                                                                            |
| OIDC_NAME_CLAIM                                   |  name   | This is the claim which Mealie will use for the users Full Name                                                                                                                                                                                                                                        |
| OIDC_GROUPS_CLAIM                                 | groups  | Optional if not using `OIDC_USER_GROUP` or `OIDC_ADMIN_GROUP`. This is the claim Mealie will request from your IdP and will use to compare to `OIDC_USER_GROUP` or `OIDC_ADMIN_GROUP` to allow the user to log in to Mealie or is set as an admin. **Your IdP must be configured to grant this claim** |
| OIDC_SCOPES_OVERRIDE                              |  None   | Advanced configuration used to override the scopes requested from the IdP. **Most users won't need to change this**. At a minimum, 'openid profile email' are required.                                                                                                                                |
| OIDC_TLS_CACERTFILE                               |  None   | File path to Certificate Authority used to verify server certificate (e.g. `/path/to/ca.crt`)                                                                                                                                                                                                          |

### OpenAI

:octicons-tag-24: v1.7.0

Mealie supports various integrations using OpenAI. For more information, check out our [OpenAI documentation](./open-ai.md).
For custom mapping variables (e.g. OPENAI_CUSTOM_HEADERS) you should pass values as JSON encoded strings (e.g. `OPENAI_CUSTOM_PARAMS='{"k1": "v1", "k2": "v2"}'`)

| Variables                    | Default | Description                                                                                                                                                                  |
| ---------------------------- | :-----: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OPENAI_BASE_URL              |  None   | The base URL for the OpenAI API. If you're not sure, leave this empty to use the standard OpenAI platform                                                                    |
| OPENAI_API_KEY               |  None   | Your OpenAI API Key. Enables OpenAI-related features                                                                                                                         |
| OPENAI_MODEL                 | gpt-4o  | Which OpenAI model to use. If you're not sure, leave this empty                                                                                                              |
| OPENAI_CUSTOM_HEADERS        |  None   | Custom HTTP headers to add to all OpenAI requests. This should generally be left empty unless your custom service requires them                                              |
| OPENAI_CUSTOM_PARAMS         |  None   | Custom HTTP query params to add to all OpenAI requests. This should generally be left empty unless your custom service requires them                                         |
| OPENAI_ENABLE_IMAGE_SERVICES |  True   | Whether to enable OpenAI image services, such as creating recipes via image. Leave this enabled unless your custom model doesn't support it, or you want to reduce costs     |
| OPENAI_WORKERS               |    2    | Number of OpenAI workers per request. Higher values may increase processing speed, but will incur additional API costs                                                       |
| OPENAI_SEND_DATABASE_DATA    |  True   | Whether to send Mealie data to OpenAI to improve request accuracy. This will incur additional API costs                                                                      |
| OPENAI_REQUEST_TIMEOUT       |   60    | The number of seconds to wait for an OpenAI request to complete before cancelling the request. Leave this empty unless you're running into timeout issues on slower hardware |

### Theming

Setting the following environmental variables will change the theme of the frontend. Note that the themes are the same for all users. This is a break-change when migration from v0.x.x -> 1.x.x.

| Variables             | Default | Description                 |
| --------------------- | :-----: | --------------------------- |
| THEME_LIGHT_PRIMARY   | #E58325 | Light Theme Config Variable |
| THEME_LIGHT_ACCENT    | #007A99 | Light Theme Config Variable |
| THEME_LIGHT_SECONDARY | #973542 | Light Theme Config Variable |
| THEME_LIGHT_SUCCESS   | #43A047 | Light Theme Config Variable |
| THEME_LIGHT_INFO      | #1976D2 | Light Theme Config Variable |
| THEME_LIGHT_WARNING   | #FF6D00 | Light Theme Config Variable |
| THEME_LIGHT_ERROR     | #EF5350 | Light Theme Config Variable |
| THEME_DARK_PRIMARY    | #E58325 | Dark Theme Config Variable  |
| THEME_DARK_ACCENT     | #007A99 | Dark Theme Config Variable  |
| THEME_DARK_SECONDARY  | #973542 | Dark Theme Config Variable  |
| THEME_DARK_SUCCESS    | #43A047 | Dark Theme Config Variable  |
| THEME_DARK_INFO       | #1976D2 | Dark Theme Config Variable  |
| THEME_DARK_WARNING    | #FF6D00 | Dark Theme Config Variable  |
| THEME_DARK_ERROR      | #EF5350 | Dark Theme Config Variable  |

### Docker Secrets

Setting a credential can be done using secrets when running in a Docker container.
This can be used to avoid leaking passwords through compose files, environment variables, or command-line history.
For example, to configure the Postgres database password in Docker compose, create a file on the host that contains only the password, and expose that file to the Mealie service as a secret with the correct name.
Note that environment variables take priority over secrets, so any previously defined environment variables should be removed when migrating to secrets.

```yaml
services:
  mealie:
    ...
    environment:
      ...
      POSTGRES_USER: postgres
    secrets:
      - POSTGRES_PASSWORD

secrets:
  POSTGRES_PASSWORD:
    file: postgrespassword.txt
```

[unicorn_workers]: https://www.uvicorn.org/deployment/#built-in
