# Migration gateway

The Python backend is being replaced by a Java backend (`backend-java/`) one route at a time. A load balancer on
**:8080** sits in front of both and decides, per path, which backend answers. Today every path goes to Python.

```
browser ─► frontend :3000 ─► gateway :8080 ─┬─► Python (FastAPI) :9000 ─┐
               (API_URL)        (Caddy)     └─► Java (Spring)    :9100 ─┴─► SQLite or Postgres
```

Both backends share one database. Python/Alembic owns the schema; Java never creates or alters tables.

## Why Caddy

We chose [Caddy](https://caddyserver.com/) 2 (`caddy:2.11.4-alpine`), configured in `gateway/Caddyfile`.

- **One route is one line, in any order.** `reverse_proxy /api/foods* {$JAVA_UPSTREAM}` moves a path. Caddy sorts
  `reverse_proxy` rules by path specificity (longest first, unmatched catch-all last), so a new line can go anywhere
  in the file and still win. We checked this by appending a rule after the catch-all.
- **No restart to switch.** The container runs `caddy run --watch`: saving the Caddyfile reloads it gracefully,
  without dropping in-flight requests. Rolling back means deleting the line.
- **Visible routing.** Every response carries `X-Mealie-Backend: python|java`, so the browser's network tab or
  `curl -I` shows which backend served a request.
- **Small and embeddable.** It's a single static binary with good proxy defaults (X-Forwarded-*, streaming, WebSockets). That
  matters later, when production (today a single container) needs the gateway in front of two processes.

We considered these alternatives:

- **nginx** could do the job too. Its `location` precedence rules (prefix vs regex) are easier to get wrong, and
  every switch needs an explicit reload.
- **HAProxy** is the strongest pure load balancer, and map-file routing would also be one line. For two backends in
  dev, it adds more config ceremony than it pays back.
- **Traefik** needs a router, a service, and often a priority per route, so a switch is several lines of YAML rather
  than one.
- **Envoy** is too verbose to hand-edit for this.

## Ports

| Port | What                    | Started by                                  |
|------|-------------------------|---------------------------------------------|
| 3000 | Nuxt frontend           | `task ui` (`API_URL` defaults to :8080)     |
| 8080 | Gateway (Caddy)         | `task gateway`                              |
| 9000 | Python backend          | `task py` / `task py:postgres`              |
| 9100 | Java backend            | `task java`                                 |
| 5432 | Postgres (dev)          | `task dev:postgres` (from `docker/docker-compose.dev.yml`) |

The gateway container reaches the backends on the host through `host.docker.internal`. Override with
`PYTHON_UPSTREAM` / `JAVA_UPSTREAM` when starting it.

## Running the stack

```bash
task stack:sqlite      # gateway + Python + Java + frontend on dev/data/mealie.db
task stack:postgres    # same, after starting the dev Postgres container
```

Both commands run everything in the foreground; Ctrl-C stops it all, including the gateway container. The Postgres
container keeps running (stop it with `docker compose -f docker/docker-compose.dev.yml stop postgres`). Add
`--output prefixed` (`task --output prefixed stack:sqlite`) to label each line with the process it came from.

The stack tasks give Python and Java identical `DB_ENGINE` / `POSTGRES_*` settings. To run the pieces separately,
give both backends the same environment, e.g. for Postgres:

```bash
task dev:postgres
task gateway
task py:postgres
DB_ENGINE=postgres POSTGRES_SERVER=localhost task java
task ui
```

To bypass the gateway, run `API_URL=http://localhost:9000 task ui`.

Notes:

- With `PRODUCTION=false` (as the Taskfile sets it), Python signs tokens with the fixed key `shh-secret-test-key` and
  ignores `dev/data/.secret`. Java follows the same rule, so tokens work on both. In production both read
  `<DATA_DIR>/.secret`.
- The Postgres container is the existing dev service, with data in `dev/data/postgres`. Don't run it alongside
  `task dev:services` under a different name; they would fight over port 5432.
- `curl localhost:9100/api/java/health` shows the engine Java is using, its DB connection, and the Alembic revision.
  If you send a token, it also shows whether Java accepts it.

## Moving a route to Java

1. Implement the endpoint in `backend-java/` with the same path, status codes and JSON as Python.
2. Add read-only cases for it to `dev/rebuild/diff_cases.json`.
3. Run the diff test on **both** engines and get it passing:

   ```bash
   task stack:sqlite     # in one terminal
   task diff -- --expect-engine sqlite
   task stack:postgres   # in one terminal
   task diff -- --expect-engine postgres
   ```

4. Add one line to `gateway/Caddyfile`, inside the `:8080` block next to the other `reverse_proxy` lines:

   ```caddyfile
   reverse_proxy /api/foods* {$JAVA_UPSTREAM}
   ```

5. Check it: `curl -sI localhost:8080/api/foods | grep X-Mealie-Backend` should print `java`.

To roll back, delete the line.

Gotchas:

- `/api/foods*` is a plain string prefix. It also catches `/api/foodsearch`, if such a route existed. Use
  `/api/foods/*` to match only below the segment. To keep one sub-path on Python, add a longer rule pointing at
  `{$PYTHON_UPSTREAM}`.
- To move only some methods, use a named matcher. Named matchers aren't sorted by specificity, so keep them disjoint
  from other Java rules:

  ```caddyfile
  @foodsRead {
      path /api/foods*
      method GET
  }
  reverse_proxy @foodsRead {$JAVA_UPSTREAM}
  ```

## Diff test

`dev/rebuild/diff_test.py` (`task diff`) sends the same request with the same token to :9000 and :9100 and compares
the status code and JSON body, ignoring key order.

Before any case runs, it checks three things:

- Both backends are up.
- Both report the same DB engine (Python's `/api/admin/about` vs Java's `/api/java/health`).
- Both accept the token and resolve it to the same user.

```bash
task diff                                   # all cases in dev/rebuild/diff_cases.json
task diff -- GET /api/foods                 # one ad-hoc case
task diff -- --expect-engine postgres --report /tmp/diff.json
task diff -- --ignore items.*.updatedAt     # ignore a field in every case
```

By default it logs in on Python as `changeme@example.com` / `MyPassword` (the seeded admin). For other
databases, pass `--token` (or `MEALIE_TOKEN`) or `--username/--password`. The token needs admin rights, so the
engine check can read `/api/admin/about`.

Only add **read-only** cases. Both backends write to the same database, so a POST in a case runs twice.

## Checking the Java SQL dialect against a real database

`task java:test` runs the unit and integration tests on a throwaway SQLite file. `task java:test:db ENGINE=sqlite`
and `task java:test:db ENGINE=postgres` also check the dialect read-only against the dev database Python created
(UUIDs, booleans, datetimes, dates, enums). See `backend-java/README.md`.
