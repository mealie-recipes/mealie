# Django REST Framework HTTP migration

## Status

Django is now the default HTTP application. Django URL resolution, middleware,
request parsing and DRF `APIView` dispatch serve the existing controllers.
There is no embedded FastAPI application or FastAPI runtime dependency.
SQLAlchemy, Alembic, Pydantic and Nuxt remain in place.

The implementation has substantial automated coverage, but verification is not
complete. The results and limits below distinguish tested behavior from behavior
that still needs deployment or external-service verification.

## Changed files

The exact source manifest is [validation/django-http/changed-files.json](validation/django-http/changed-files.json).
It compares existing Python files with captured starting byte hashes and lists
new HTTP modules and additional configuration, documentation and generated files.
It includes formatting and generated export changes. The checkout already had
unrelated dirty files when this work began; those are not claimed as migration work.

The principal changes are:

- `mealie/http/`: Django/DRF settings, views, URL resolution, dependency contexts,
  Pydantic validation and serialization, parsers, middleware, response and file
  handling, OpenAPI generation, ASGI lifecycle, WSGI embedding and test transport.
- `mealie/app.py`, `mealie/main.py`: default Django application and Uvicorn ASGI
  entrypoint. `Taskfile.yml` and `.vscode/launch.json` use this application.
  The existing package command and Docker entrypoint reach the new application
  through `mealie.main`; no separate FastAPI deployment is retained.
- `mealie/routes/`, `mealie/core/dependencies/`, schema dependency helpers and
  affected services: replace framework imports and route binding while retaining
  business controllers, SQLAlchemy repositories and permission checks.
- Scheduler runner/service: use asgiref and cancel application-owned scheduled
  tasks on shutdown.
- `pyproject.toml`, `uv.lock`: add Django/DRF and remove FastAPI; CI environment
  cache probes now check Django/DRF imports.
- Existing tests and fixtures: use the HTTPX-compatible Django test transport.
  Configuration tests isolate temporary settings and clear their cached settings
  after each test. Assertions are retained.
- `tests/unit_tests/test_django_http.py`, `test_http_contract.py` and
  `tests/data/http/original-openapi.json`: native ASGI, streaming, lifecycle,
  validation, file and pre-migration API contract coverage.
- Generated schema exports, test route/data helpers and TypeScript types were
  regenerated through the project generator. `recipe.ts` gains three duration
  fields already present in the backend schema. No backend data model or Alembic
  migration was needed. Managed non-English translations were not edited.
- `docs/docs/contributors/developers-guide/django-http.md`: development and
  deployment documentation for the new application.

## Implemented behavior and evidence

- Contract tests compare all 182 documented pre-migration paths, HTTP methods,
  parameter locations/required flags, response statuses and request-body presence.
  Component schema shapes and security declarations match after removing
  descriptive text. This is structural compatibility evidence, not proof of every
  possible input or response byte sequence.
- Existing integration tests run through Django's WSGI handler and DRF views.
  Additional tests exercise the actual Django ASGI handler, bearer authentication,
  group/household boundaries and application lifespan.
- Pydantic retains request coercion, aliases, validation and response filtering.
  Legacy error envelopes, OAuth form credentials, cookies, API tokens and
  authorization dependency chains remain supported.
- Multipart uploads, file downloads, cache/modified headers, byte ranges,
  redirects, production SPA fallback and generated OpenAPI/docs are implemented.
- Dependency sessions remain open through streams and background work and close
  on completion/errors. Synchronous endpoints/dependencies run in worker threads;
  asynchronous endpoints and SSE retain asynchronous execution. Tests cover
  stream cleanup, background ordering and scheduler shutdown.
- ASGI startup initializes the SQLAlchemy database with the existing Alembic path
  and starts the scheduler. WSGI embedding does not run the ASGI lifespan;
  deployments requiring SSE and scheduled jobs must use the default ASGI entrypoint.

## Validation

Logs are preserved under [validation/django-http](validation/django-http).

| Check | Verified result |
| --- | --- |
| SQLite `task py:check -- -n 4` | 3,197 passed, 16 skipped; Ruff format/lint and mypy passed (485 source files) |
| PostgreSQL full suite, before cache-isolation fix | 3,194 passed, 16 skipped, 3 backup failures from a cached temporary `postgres:5432` address |
| PostgreSQL configuration + backup regression | 62 passed after cache-isolation fix |
| PostgreSQL full suite after fix | Pending final run |
| Frontend `task --force ui:check -- --maxWorkers=1 --pool=threads` | ESLint passed; 45 files / 461 tests passed, but four worker-startup timeout errors caused a nonzero result |
| Retry of four frontend worker failures | Pending final run |
| Extra Vue TypeScript check | Pending final run; checker tooling was absent from the checkout and installed only in `/tmp` |
| Django system check | Passed |
| `uv lock --offline --check` | Passed, 147 packages |
| Project code generation | Passed for schema, types, data paths and routes; locale generators intentionally excluded |
| Wheel and source distribution | Built successfully; wheel includes 21 HTTP modules and has no FastAPI requirement |
| `evidence/w1` | Byte hashes unchanged; see `evidence-preservation.json` |

The 16 backend skips are existing LDAP-service and long-running external
parser/scraper skips. Tests were not deleted, assertions were not relaxed and
frontend timeouts were not increased. Some earlier sandboxed runs stalled because
thread/event-loop communication was restricted; the reported backend runs were
executed outside that sandbox against local test resources.

## Remaining dependencies, incomplete work and blockers

FastAPI is absent from Python dependencies, the lock file and executable imports.
Historical FastAPI references remain in comments, provenance links and tests
asserting that it is not loaded. Starlette remains explicitly pinned for
Authlib's outbound OIDC client and `URLPath`; it does not host the HTTP API.
Uvicorn remains the ASGI server. `python-multipart` remains a legacy dependency;
the new HTTP upload parser uses Django instead.

Frontend verification remains incomplete until the worker-startup failures and
extra Vue type check have final results. The structural API comparison and passing
backend tests do not establish exhaustive compatibility for arbitrary malformed
inputs, proxies, disconnect timing or all production traffic.

Live LDAP/OIDC providers, TLS/proxy deployment, browser end-to-end flows and a
complete production Docker image were not verified. Those checks would need
isolated configured services and deployment fixtures; no production services or
upstream credentials were used. No commits were pushed and no pull request was
opened. The only database service used for this migration is a disposable local
PostgreSQL test container.
