# FastAPI to Django/DRF Migration — W2

## Scope
Migrate Mealie's HTTP API to Django REST Framework.
Retain SQLAlchemy, Alembic, Pydantic, and the Nuxt frontend.

## Stage 0: Baseline
- Install existing dependencies.
- Run existing tests and record results.
- Capture the theme endpoint's response and headers.

Gate: Resolve or document baseline failures before implementation.

## Stage 1: Django/DRF pilot
- Add Django and DRF dependencies.
- Add separate Django settings, URLs, and ASGI entry point.
- Implement GET /api/app/about/theme.
- Preserve Pydantic response aliases and Cache-Control.
- Keep the current FastAPI entry point available.

Gate: Compare JSON, status codes, headers, and URL behaviour
against the original endpoint.

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
