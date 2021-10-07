# Backend Configuration

## API Environment Variables

### General

| Variables     |        Default        | Description                                                                         |
| ------------- | :-------------------: | ----------------------------------------------------------------------------------- |
| PUID          |          911          | UserID permissions between host OS and container                                    |
| PGID          |          911          | GroupID permissions between host OS and container                                   |
| DEFAULT_GROUP |         Home          | The default group for users                                                         |
| DEFAULT_EMAIL |  changeme@email.com   | The default username for the superuser                                              |
| BASE_URL      | http://localhost:8080 | Used for Notifications                                                              |
| TOKEN_TIME    |          48           | The time in hours that a login/auth token is valid                                  |
| API_PORT      |         9000          | The port exposed by backend API. **Do not change this if you're running in Docker** |
| API_DOCS      |         True          | Turns on/off access to the API documentation locally.                               |
| TZ            |          UTC          | Must be set to get correct date/time on the server                                  |


### Database

| Variables         | Default  | Description                      |
| ----------------- | :------: | -------------------------------- |
| DB_ENGINE         |  sqlite  | Optional: 'sqlite', 'postgres'   |
| POSTGRES_USER     |  mealie  | Postgres database user           |
| POSTGRES_PASSWORD |  mealie  | Postgres database password       |
| POSTGRES_SERVER   | postgres | Postgres database server address |
| POSTGRES_PORT     |   5432   | Postgres database port           |
| POSTGRES_DB       |  mealie  | Postgres database name           |


### Email

| Variables       | Default | Description        |
| --------------- | :-----: | ------------------ |
| SMTP_HOST       |  None   | Required For email |
| SMTP_PORT       |   587   | Required For email |
| SMTP_FROM_NAME  | Mealie  | Required For email |
| SMTP_TLS        |  true   | Required For email |
| SMTP_FROM_EMAIL |  None   | Required For email |
| SMTP_USER       |  None   | Required For email |
| SMTP_PASSWORD   |  None   | Required For email |

### Webworker
Changing the webworker settings may cause unforeseen memory leak issues with Mealie. It's best to leave these at the defaults unless you begin to experience issues with multiple users. Exercise caution when changing these settings

| Variables        | Default | Description                                                                                                                       |
| ---------------- | :-----: | --------------------------------------------------------------------------------------------------------------------------------- |
| WORKERS_PER_CORE |    1    | Set the number of workers to the number of CPU cores multiplied by this value (Value \* CPUs). More info [here][workers_per_core] |
| MAX_WORKERS      |    1    | Set the maximum number of workers to use. Default is not set meaning unlimited. More info [here][max_workers]                     |
| WEB_CONCURRENCY  |    1    | Override the automatic definition of number of workers. More info [here][web_concurrency]                                         |
