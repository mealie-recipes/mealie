# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mealie is a self-hosted recipe manager, meal planner, and shopping list application. FastAPI backend (Python 3.12) + Nuxt 3 frontend (Vue 3 + TypeScript). SQLAlchemy ORM supporting SQLite and PostgreSQL. Multi-tenant: data scoped to **groups** → **households**.

- **Development:** Frontend on port 3000, backend on port 9000 (separate processes)
- **Production:** Single Docker container; frontend statically generated and served via FastAPI SPA module

## Essential Commands (Taskfile.yml)

All commands use the `task` runner. Python commands use `uv` (not `python` or `pip`).

```bash
task setup              # Install all dependencies (Python + Node)
task dev:services       # Start Postgres & Mailpit containers
task py                 # Start backend (port 9000)
task ui                 # Start frontend (port 3000)

# Testing
task py:test            # Run pytest
task py:test -- -k "test_name"  # Run single test
task ui:test            # Run Vitest frontend tests
task e2e                # Run Playwright end-to-end tests

# Code quality
task py:check           # Format + lint + type-check + test (full validation)
task py:format          # Ruff format
task py:lint            # Ruff check
task py:mypy            # Mypy type checking
task ui:check           # Frontend lint + test

# Code generation (REQUIRED after Pydantic schema changes)
task dev:generate       # Generate TypeScript types, schema exports, test helpers

# Database
task py:migrate -- "description"  # Generate Alembic migration
task py:postgres        # Run backend with PostgreSQL config

# Docker
task docker:prod        # Build and run production Docker compose
```

## Architecture

### Backend — Repository-Service-Controller Pattern

```
mealie/
├── routes/    # Controllers: inherit BaseUserController or BaseAdminController
├── services/  # Business logic: inherit BaseService
├── repos/     # Data access: SQLAlchemy, accessed via AllRepositories factory
├── schema/    # Pydantic models (*In, *Out, *Create, *Update suffixes)
├── db/models/ # SQLAlchemy ORM models
├── core/      # Settings, security, config
└── alembic/   # Database migrations
```

**Key patterns:**
- Dependency injection: `repos: AllRepositories = Depends(get_repositories)` — repos are automatically scoped to group/household
- Settings: `get_app_settings()` (cached singleton, never instantiate `AppSettings()` directly)
- Sessions: `Depends(generate_session)` in routes, `session_context()` in services/scripts
- Route controllers use `HttpRepo` mixin for common CRUD (`mealie/routes/_base/mixins.py`)

### Frontend

```
frontend/
├── components/Domain/   # Feature-specific (domain-prefixed, e.g., AdminDashboard)
├── components/global/   # Reusable primitives (Base prefix, e.g., BaseButton)
├── components/Layout/   # Layout (App prefix if props, The prefix if singleton)
├── composables/         # Shared state/logic (no Vuex)
├── lib/api/             # API clients extending BaseAPI/BaseCRUDAPI
├── lib/api/types/       # AUTO-GENERATED from Pydantic schemas — never edit manually
└── pages/               # Nuxt page components
```

**Key patterns:**
- API calls: `const api = useUserApi(); await api.recipes.getOne(id);`
- Auth: `useAuthBackend()` for auth state, `useMealieAuth()` for user management
- Translations: only modify `en-US` locale files; other locales managed by Crowdin (PRs touching them will be rejected)

## Critical Rules

1. **Run `task dev:generate` after any Pydantic schema change** — generates TypeScript types, schema `__init__.py` exports, and test helpers
2. **Never manually edit** `frontend/lib/api/types/` or `mealie/schema/*/__init__.py` — these are auto-generated
3. **Repositories are group/household-scoped** — passing wrong context IDs causes 404s
4. **Type hints mandatory** on all Python functions (mypy-compatible)
5. **Run `task py:check` and `task ui:check`** before submitting PRs
6. **Conventional Commits** for PR titles

## Key Reference Files

- `Taskfile.yml` — all dev commands
- `mealie/routes/_base/base_controllers.py` — controller base classes
- `mealie/repos/repository_factory.py` — repository factory and available repos
- `frontend/lib/api/base/base-clients.ts` — API client base classes
- `tests/conftest.py` — test fixtures and setup
- `dev/code-generation/main.py` — code generation entry point
