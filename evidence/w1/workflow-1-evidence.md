# COMPX574 Mealie Migration — Workflow 1 Evidence

**Evidence assembled:** 2026-10-13
**Workflow description:** One high-level migration instruction; no staged
human reviews or endpoint-by-endpoint guidance.

## Evidence sources and limitations

This report uses the preserved baseline logs under this folder, the migration
report at [`../../DJANGO_HTTP_MIGRATION_REPORT.md`](../../DJANGO_HTTP_MIGRATION_REPORT.md),
the migration file manifest at
[`../../validation/django-http/changed-files.json`](../../validation/django-http/changed-files.json),
validation logs under [`../../validation/django-http/`](../../validation/django-http/),
current Git metadata, and the Codex conversation history available in this
workspace.

**The exact original migration prompt is missing.** The available conversation
history does not include the original Workflow 1 implementation turn. The
current user instruction confirms the workflow style (one high-level
instruction, no staged human reviews or endpoint-by-endpoint guidance), but it
is not the verbatim original migration prompt. Session history available here
contains the report-preparation conversations, not the migration implementation
conversation.

No full test suite was rerun to prepare this report. The current worktree
contains unrelated/pre-existing changes; the saved diff summary is labeled as a
worktree snapshot and not represented as a migration-only diff.

## Original instruction, branch, and starting commit

- **Original migration prompt:** **Missing; exact wording could not be recovered.**
- **Workflow constraint:** The user states that Workflow 1 used one high-level
  migration instruction and did not use staged human reviews or
  endpoint-by-endpoint guidance.
- **Starting commit:** `63cf7468f39f2d7f4b3bad2c3fb9141a246c917e`, recorded in
  [`baseline-commit.txt`](baseline-commit.txt).
- **Branch:** Current branch is `migration/fastapi-to-drf-w1`. A separate
  baseline-time branch capture was not found; do not assume this was
  independently recorded at task start.
- **Baseline time:** [`agent-start-time.txt`](agent-start-time.txt) records
  `2026-10-12T23:22:16+00:00`.

## Baseline results (before migration)

These are baseline results, not post-migration results.

| Check | Recorded result | Evidence |
| --- | --- | --- |
| Baseline test suite | **3,179 passed, 18 skipped** in 26m51s. | [`baseline-tests.txt`](baseline-tests.txt) |
| Baseline mypy | **No issues found in 464 source files.** | [`baseline-mypy.txt`](baseline-mypy.txt) |

The baseline log files preserve results but do not include an exact invocation
for either check. **Baseline command strings are therefore missing.** The
baseline test skips include LDAP-service, long-running scraper/parser, and
optional PostgreSQL-driver cases as listed in the log.

## Summary of migration changes attributed to Codex

The repository migration report describes a replacement of Mealie's FastAPI
HTTP runtime with Django and Django REST Framework (DRF), while retaining
SQLAlchemy, Alembic, Pydantic, the existing frontend, and core business
controllers.

The major completed work recorded in the repository includes:

- Added the Django/DRF HTTP layer for settings, URL resolution, request and
  response handling, validation/serialization, middleware, files, OpenAPI,
  ASGI lifecycle, WSGI embedding, and testing.
- Rebound route/controller integration and dependencies; adapted middleware and
  scheduler lifecycle while preserving repository, permission, and service
  behavior.
- Updated application entry points, Python dependencies/lock, task and CI
  configuration, and VS Code launch configuration. FastAPI is reported absent
  from runtime dependencies.
- Adapted existing tests/fixtures and added native Django HTTP and API-contract
  coverage based on a captured pre-migration OpenAPI document.
- Regenerated schema exports, route/test helpers, and frontend API types; added
  Django HTTP developer/deployment documentation.

Representative paths include:

- Runtime and entry points: `mealie/http/`, `mealie/app.py`, `mealie/main.py`
- Route integration: `mealie/routes/_base/controller.py`,
  `mealie/routes/_base/routers.py`, `mealie/core/dependencies/dependencies.py`
- Dependencies and tooling: `pyproject.toml`, `uv.lock`, `Taskfile.yml`,
  `.github/workflows/test-backend.yml`, `.vscode/launch.json`
- Compatibility tests: `tests/unit_tests/test_django_http.py`,
  `tests/unit_tests/test_http_contract.py`,
  `tests/data/http/original-openapi.json`
- Documentation: `docs/docs/contributors/developers-guide/django-http.md`

See the comprehensive file-level manifest at
[`changed-files.json`](../../validation/django-http/changed-files.json).
It states that it compares Python file hashes to captured starting hashes and
that the checkout already contained unrelated dirty files. It lists 204 Python
paths with changes, 21 HTTP modules, and 11 additional configuration,
documentation, test, or generated paths; those categories are reproduced from
the manifest and are not equivalent to a clean Git diff.

## Saved Git diff summary

The companion file [`workflow-1-diff-summary.txt`](workflow-1-diff-summary.txt)
preserves Git diff summary commands and representative statistics. At capture:

- `git diff --shortstat HEAD`: **196 files changed, 552 insertions(+),
  913 deletions(-)**.
- A representative tracked-file subset covering entry points, route adapters,
  dependencies, and task configuration: **7 files changed, 129 insertions(+),
  449 deletions(-)**.
- No staged diff was recorded.

These statistics describe the current tracked worktree diff relative to
`HEAD`, including unrelated/pre-existing edits. They exclude untracked new
files (including new HTTP modules) and must not be interpreted as an exact
migration-only patch. The exact original clean Git diff is **missing**.

## Post-migration validation

The following results are post-migration and distinct from the baseline above.
No tests were rerun for this evidence report.

| Command / check | Actual recorded result | Evidence |
| --- | --- | --- |
| `task py:check -- -n 4` (recorded command in the migration report); component commands shown in log: `uv run ruff format .`, `uv run mypy mealie`, `uv run ruff check mealie`, `uv run pytest -n auto --dist loadfile -n 4` | Format completed; Ruff passed; mypy passed for 485 source files; SQLite pytest **3,197 passed, 16 skipped** in 10m46s. | [`sqlite-final.log`](../../validation/django-http/sqlite-final.log) |
| `uv lock --offline --check` | Passed; 147 packages resolved. | [`final-lock.log`](../../validation/django-http/final-lock.log) |
| Django system check | Passed: no issues identified. | [`django-check.log`](../../validation/django-http/django-check.log) |
| Project code generation | Migration report records successful schema/type/data-path/route generation. Saved log ends with checks passing and files formatted. | [`codegen-final.log`](../../validation/django-http/codegen-final.log) |
| PostgreSQL full suite: `uv run pytest -n auto --dist loadfile -n 4` | **3 failed, 3,194 passed, 16 skipped.** Failures were backup, restore, and restore-data tests; connection errors reported failure to resolve hostname `postgres`. | [`postgres-final.log`](../../validation/django-http/postgres-final.log) |
| Targeted PostgreSQL config/backup regression: `uv run pytest -n auto --dist loadfile tests/unit_tests/test_config.py tests/unit_tests/services_tests/backup_v2_tests/test_backup_v2.py -n 1` | **62 passed** in 3m06s after cache-isolation correction. | [`postgres-cache-regression.log`](../../validation/django-http/postgres-cache-regression.log) |
| PostgreSQL full-suite retry after correction | **No final result recorded.** The log contains only the command header. | [`postgres-verified.log`](../../validation/django-http/postgres-verified.log) |
| `task --force ui:check -- --maxWorkers=1 --pool=threads` | ESLint passed; Vitest showed **45 files / 461 tests passed**, but had **4 worker-startup timeout errors** and the task failed. | [`ui-check-threads.log`](../../validation/django-http/ui-check-threads.log) |
| Frontend serial retry using `--maxWorkers=1` | Vitest showed **39 files / 339 tests passed**, but had **10 worker errors** and the task failed. | [`ui-check-serial.log`](../../validation/django-http/ui-check-serial.log) |
| Retry of four worker-failing frontend tests using `--pool=forks` | **No final result recorded.** | [`ui-remaining.log`](../../validation/django-http/ui-remaining.log) |
| Additional Vue TypeScript check | **No result recorded**; the saved final log is empty. | [`ui-typecheck-final.log`](../../validation/django-http/ui-typecheck-final.log) |
| Source distribution and wheel build | Both built successfully: `mealie-3.28.0.tar.gz` and `mealie-3.28.0-py3-none-any.whl`. | [`build.log`](../../validation/django-http/build.log) |
| API contract | Migration report records structural comparison of **182 documented paths**; it is not exhaustive proof of all runtime behavior. | [`DJANGO_HTTP_MIGRATION_REPORT.md`](../../DJANGO_HTTP_MIGRATION_REPORT.md) |

## Errors, unresolved issues, and human follow-up

- **PostgreSQL:** The full suite initially failed three backup-related tests
  because the temporary PostgreSQL hostname was not resolvable. The migration
  report attributes this to cached temporary connection settings. A
  cache-isolation correction was made, after which the focused regression run
  passed 62 tests. A successful full PostgreSQL rerun is not evidenced.
- **Frontend workers:** Vitest worker-startup timeouts/errors caused nonzero
  frontend runs despite the displayed tests passing. The fork-pool retry has no
  completion result. The extra Vue type check is also pending/unrecorded.
- **External/deployment verification:** The report says live LDAP/OIDC
  providers, TLS/reverse-proxy deployment, browser E2E, and a complete
  production Docker image were not verified. WSGI embedding does not run the
  ASGI lifespan; deployments needing scheduled jobs and SSE must use the ASGI
  entry point.
- **Human reviews or endpoint guidance:** Per the user's Workflow 1 description,
  there were no staged human reviews or endpoint-by-endpoint instructions.
  No separate migration-specific human correction request or approval is
  present in the accessible conversation. The report does not claim one.
- **Commits/PR:** The migration report says no migration commit was made/pushed
  and no pull request was opened. The only evidenced commit remains the starting
  commit.

## Current commit and worktree status

At the time of evidence capture, current `HEAD` is still
`63cf7468f39f2d7f4b3bad2c3fb9141a246c917e`, on
`migration/fastapi-to-drf-w1`. There is no migration commit in the observed
history. `git status --short` reports **213 tracked modified paths, 9
untracked status entries, and no staged entries**; untracked directories may
be displayed as a single status entry. The tracked worktree diff is **not
clean**; its summary is saved in
[`workflow-1-diff-summary.txt`](workflow-1-diff-summary.txt). The locale-sync
workflow change was separately made during a later conversation and is
explicitly not attributed to the migration. The status snapshot and tracked
diff also include unrelated/pre-existing changes. The `git diff --shortstat`
file count is 196, distinct from the porcelain status-entry count; the exact
migration-only diff is unavailable.

[`evidence-preservation.json`](../../validation/django-http/evidence-preservation.json)
records that the original four baseline evidence files were unchanged after
migration. This report and the companion diff summary were added after that
preservation record was created; they are additional evidence, not part of its
hash list.
