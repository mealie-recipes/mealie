# Backend Configuration

## API Environment Variables

### General

| Variables     |        Default        | Description                                                                         |
|---------------|:---------------------:|-------------------------------------------------------------------------------------|
| PUID          |          911          | UserID permissions between host OS and container                                    |
| PGID          |          911          | GroupID permissions between host OS and container                                   |
| DEFAULT_GROUP |         Home          | The default group for users                                                         |
| DEFAULT_EMAIL |  changeme@email.com   | The default username for the superuser                                              |
| BASE_URL      | http://localhost:8080 | Used for Notifications                                                              |
| TOKEN_TIME    |          48           | The time in hours that a login/auth token is valid                                  |
| API_PORT      |         9000          | The port exposed by backend API. **Do not change this if you're running in Docker** |
| API_DOCS      |         True          | Turns on/off access to the API documentation locally.                               |
| TZ            |          UTC          | Must be set to get correct date/time on the server                                  |
| ALLOW_SIGNUP  |         true          | Allow user sign-up without token (should match frontend env)                        |

### Security

| Variables                   | Default | Description                                                                         |
|-----------------------------|:-------:|-------------------------------------------------------------------------------------|
| SECURITY_MAX_LOGIN_ATTEMPTS |    5    | Maximum times a user can provide an invalid password before their account is locked |
| SECURITY_USER_LOCKOUT_TIME  |   24    | Time in hours for how long a users account is locked                                |

### Database

| Variables         | Default  | Description                      |
|-------------------|:--------:|----------------------------------|
| DB_ENGINE         |  sqlite  | Optional: 'sqlite', 'postgres'   |
| POSTGRES_USER     |  mealie  | Postgres database user           |
| POSTGRES_PASSWORD |  mealie  | Postgres database password       |
| POSTGRES_SERVER   | postgres | Postgres database server address |
| POSTGRES_PORT     |   5432   | Postgres database port           |
| POSTGRES_DB       |  mealie  | Postgres database name           |

### Email

| Variables          | Default | Description                                       |
|--------------------|:-------:|---------------------------------------------------|
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
|------------------|:-------:|-----------------------------------------------------------------------------------------------------------------------------------|
| WEB_GUNICORN     |  false  | Enables Gunicorn to manage Uvicorn web for multiple works                                                                         |
| WORKERS_PER_CORE |    1    | Set the number of workers to the number of CPU cores multiplied by this value (Value \* CPUs). More info [here][workers_per_core] |
| MAX_WORKERS      |    1    | Set the maximum number of workers to use. Default is not set meaning unlimited. More info [here][max_workers]                     |
| WEB_CONCURRENCY  |    1    | Override the automatic definition of number of workers. More info [here][web_concurrency]                                         |

### LDAP

| Variables           | Default | Description                                                                                                        |
|---------------------|:-------:|--------------------------------------------------------------------------------------------------------------------|
| LDAP_AUTH_ENABLED   |  False  | Authenticate via an external LDAP server in addition to built-in Mealie auth                                       |
| LDAP_SERVER_URL     |  None   | LDAP server URL (e.g. ldap://ldap.example.com)                                                                     |
| LDAP_TLS_INSECURE   |  False  | Do not verify server certificate when using secure LDAP                                                            |
| LDAP_TLS_CACERTFILE |  None   | File path to Certificate Authority used to verify server certificate (e.g. `/path/to/ca.crt`)                      |
| LDAP_BIND_TEMPLATE  |  None   | Templated DN for users, `{}` will be replaced with the username (e.g. `cn={},dc=example,dc=com`, `{}@example.com`) |
| LDAP_BASE_DN        |  None   | Starting point when searching for users authentication (e.g. `CN=Users,DC=xx,DC=yy,DC=de`)                         |
| LDAP_ADMIN_FILTER   |  None   | Optional LDAP filter, which tells Mealie the LDAP user is an admin (e.g. `(memberOf=cn=admins,dc=example,dc=com)`) |

### Single Sign On

Mealie supports SSO via Trusted Headers added by a Reverse Proxy into every request. See [here](https://www.authelia.com/integration/trusted-header-sso/introduction/) for more information

| Variables        |   Default    | Description                                                                      |
|------------------|:------------:|----------------------------------------------------------------------------------|
| SSO_AUTH_ENABLED |    False     | Authenticate via an external SSO server in addition to built-in Mealie auth      |
| SSO_HEADER_USER  | Remote-User  | The name of the header in which the user ID is provided.                         |
| SSO_HEADER_EMAIL | Remote-Email | The name of the header in which the user email is provided. This is optional.    |
| SSO_HEADER_NAME  | Remote-Name  | The name of the header in which the user fullname is provided. This is optional. |

#### SSO Reverse Proxy Setup

This example uses [Caddy](https://caddyserver.com/) as reverse proxy and [Authelia](https://www.authelia.com/) as Identity Provider. An example Caddyfile should look like this:

```properties
meaile.mydomain.com {
    forward_auth authelia:9091 {
        method GET
        uri /api/verify?rd=https://login.mydomain.com
        header_up X-Forwarded-Method {method}
        header_up X-Forwarded-Uri {uri}
        copy_headers Remote-User Remote-Name Remote-Email
    }
	reverse_proxy mealie:8080
}
```

If you want to run a quick test instead:
```properties
meaile.mydomain.com {
		reverse_proxy mealie:8080 {
            header_up Remote-User "myuser"
            header_up Remote-Name "My Username"
            header_up Remote-Email "me@mydomain.com"
        }
}
```
