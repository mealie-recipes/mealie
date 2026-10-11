# FastAPI to Django/DRF Migration — W2

## Scope
Migrate Mealie's HTTP API to Django REST Framework.
Retain SQLAlchemy, Alembic, Pydantic, and the Nuxt frontend.

## Stage 0: Baseline
- Install existing dependencies.
- Run existing tests and record results.
- Capture the theme endpoint's response and headers.

Gate: Resolve or document baseline failures before implementation.

### Stage 1 — DRF theme pilot
- Added Django/DRF settings, URLs, ASGI entry point, and theme view.
- Verified GET response, cache headers, 307 redirect, and POST rejection.
- Targeted tests: 8 passed in 10.90s.
- Ruff lint, formatting, and Git whitespace checks passed.
- Full regression suite and deployment integration remain pending.

### Full regression check
- Command: uv run pytest
- Result: 3182 passed, 18 skipped in 1016.35s.
- Skips cover long-running tests, LDAP-service tests, and
  PostgreSQL-specific tests requiring the pgsql extra.
- Theme pilot checks passed; deployment integration remains pending.

## Later stages
1. Add validation and database-session adapters.
2. Migrate authentication and permissions.
3. Migrate API modules individually.
4. Verify deployment and frontend compatibility.
5. Switch the default backend after all checks pass.

## Human review
Status: Pending
Reviewer:
Review comments:
Approval date:

## Stage results
Record changed files, test commands, results, and blockers here.
