# Backend Configuration

## API Environment Variables

### General

| Variables                     |        Default        | Description                                                                         |
| ----------------------------- | :-------------------: | ----------------------------------------------------------------------------------- |
| PUID                          |          911          | UserID permissions between host OS and container                                    |
| PGID                          |          911          | GroupID permissions between host OS and container                                   |
| DEFAULT_GROUP                 |         Home          | The default group for users                                                         |
| BASE_URL                      | http://localhost:8080 | Used for Notifications                                                              |
| TOKEN_TIME                    |          48           | The time in hours that a login/auth token is valid                                  |
| API_PORT                      |         9000          | The port exposed by backend API. **Do not change this if you're running in Docker** |
| API_DOCS                      |         True          | Turns on/off access to the API documentation locally.                               |
| TZ                            |          UTC          | Must be set to get correct date/time on the server                                  |
| ALLOW_SIGNUP<super>\*</super> |         false         | Allow user sign-up without token                                                    |
| LOG_CONFIG_OVERRIDE           |                       | Override the config for logging with a custom path                                  |
| LOG_LEVEL                     |         info          | Logging level configured                                                            |
| DAILY_SCHEDULE_TIME           |        23:45          | The time of day to run the daily tasks.                                             |

<super>\*</super> Starting in v1.4.0 this was changed to default to `false` as apart of a security review of the application.

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

| Variables        | Default | Description                                                                                                                       |
| ---------------- | :-----: | --------------------------------------------------------------------------------------------------------------------------------- |
| WEB_GUNICORN     |  false  | Enables Gunicorn to manage Uvicorn web for multiple works                                                                         |
| WORKERS_PER_CORE |    1    | Set the number of workers to the number of CPU cores multiplied by this value (Value \* CPUs). More info [here][workers_per_core] |
| MAX_WORKERS      |  None   | Set the maximum number of workers to use. Default is not set meaning unlimited. More info [here][max_workers]                     |
| WEB_CONCURRENCY  |    2    | Override the automatic definition of number of workers. More info [here][web_concurrency]                                         |

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

For usage, see [Usage - OpenID Connect](../authentication/oidc.md)

| Variables              | Default | Description                                                                                                                                                                                               |
| ---------------------- | :-----: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OIDC_AUTH_ENABLED      |  False  | Enables authentication via OpenID Connect                                                                                                                                                                 |
| OIDC_SIGNUP_ENABLED    |  True   | Enables new users to be created when signing in for the first time with OIDC                                                                                                                              |
| OIDC_CONFIGURATION_URL |  None   | The URL to the OIDC configuration of your provider. This is usually something like https://auth.example.com/.well-known/openid-configuration                                                              |
| OIDC_CLIENT_ID         |  None   | The client id of your configured client in your provider                                                                                                                                                  |
| OIDC_USER_GROUP        |  None   | If specified, only users belonging to this group will be able to successfully authenticate, regardless of the `OIDC_ADMIN_GROUP`. For more information see [this page](../authentication/oidc.md#groups)  |
| OIDC_ADMIN_GROUP       |  None   | If specified, users belonging to this group will be made an admin. For more information see [this page](../authentication/oidc.md#groups)                                                                 |
| OIDC_AUTO_REDIRECT     |  False  | If `True`, then the login page will be bypassed an you will be sent directly to your Identity Provider. You can still get to the login page by adding `?direct=1` to the login URL                        |
| OIDC_PROVIDER_NAME     |  OAuth  | The provider name is shown in SSO login button. "Login with <OIDC_PROVIDER_NAME\>"                                                                                                                        |
| OIDC_REMEMBER_ME       |  False  | Because redirects bypass the login screen, you cant extend your session by clicking the "Remember Me" checkbox. By setting this value to true, a session will be extended as if "Remember Me" was checked |
| OIDC_SIGNING_ALGORITHM |  RS256  | The algorithm used to sign the id token (examples: RS256, HS256)                                                                                                                                          |
| OIDC_USER_CLAIM        |  email  | This is the claim which Mealie will use to look up an existing user by (e.g. "email", "preferred_username") |
| OIDC_GROUPS_CLAIM      | groups  | Optional if not using `OIDC_USER_GROUP` or `OIDC_ADMIN_GROUP`. This is the claim Mealie will request from your IdP and will use to compare to `OIDC_USER_GROUP` or `OIDC_ADMIN_GROUP` to allow the user to log in to Mealie or is set as an admin. **Your IdP must be configured to grant this claim**|
| OIDC_TLS_CACERTFILE    | None    | File path to Certificate Authority used to verify server certificate (e.g. `/path/to/ca.crt`) |

### OpenAI

:octicons-tag-24: v1.7.0

Mealie supports various integrations using OpenAI. To enable OpenAI, [you must provide your OpenAI API key](https://platform.openai.com/api-keys). You can tweak how OpenAI is used using these backend settings. Please note that while OpenAI usage is optimized to reduce API costs, you're unlikely to be able to use OpenAI features with the free tier limits.

| Variables                 |     Default   | Description                                                                                                                    |
| ------------------------- |    :------:   | ------------------------------------------------------------------------------------------------------------------------------ |
| OPENAI_BASE_URL           |      None     | The base URL for the OpenAI API. If you're not sure, leave this empty to use the standard OpenAI platform                      |
| OPENAI_API_KEY            |      None     | Your OpenAI API Key. Enables OpenAI-related features                                                                           |
| OPENAI_MODEL              |     gpt-4o    | Which OpenAI model to use. If you're not sure, leave this empty                                                                |
| OPENAI_WORKERS            |       2       | Number of OpenAI workers per request. Higher values may increase processing speed, but will incur additional API costs         |
| OPENAI_SEND_DATABASE_DATA |      True     | Whether to send Mealie data to OpenAI to improve request accuracy. This will incur additional API costs                        |

### Themeing

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

[workers_per_core]: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/2daa3e3873c837d5781feb4ff6a40a89f791f81b/README.md#workers_per_core
[max_workers]: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/2daa3e3873c837d5781feb4ff6a40a89f791f81b/README.md#max_workers
[web_concurrency]: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/2daa3e3873c837d5781feb4ff6a40a89f791f81b/README.md#web_concurrency
