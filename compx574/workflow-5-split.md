# Workflow 5 — area split

Phase A output. Four areas, implemented in parallel by one sub-agent each. Each area re-implements the listed Python routers in PHP (Laravel 13) inside `php-w5/`, against the existing database `dev/data/mealie.db`.

## Rules for every area

- Copy every HTTP method and full path from the assigned Python router. Paths in `routes/<area>.php` are written without `/api`; `bootstrap/app.php` adds it.
- Python stays where it is and is the reference: `http://127.0.0.1:9000`, started from this worktree with `PRODUCTION=False`.
- Do not register a route that only returns a fixed error and count it as done. A route is either implemented from its Python handler or left unregistered and listed under "not implemented".
- Write the contract section first (see below), then the code.
- Do not read or copy `php-w1/`, `compx574/workflow-1-single-instruction.md`, or anything under `compx574/hurl/`. Do not run `compx574/hurl/run.sh` or `compx574/workflow-5/measure.sh`.
- Never run `php artisan migrate` or any DDL against `dev/data/mealie.db`. No new tables or columns.
- Do not print secrets or tokens.
- Do not commit. The orchestrator commits.
- Commands that need PHP run in the sandbox container: `docker exec mealie-w5-php bash -lc 'cd php-w5 && …'` (working directory is the worktree root `/workspaces/mealie/.worktrees/w5`).
- Run your own server on your port only: `php artisan serve --host=127.0.0.1 --port=<port>`. Port 9001 is reserved for scoring.
- Verification: send the same request to Python :9000 and to your port and compare status and JSON body. Writes against the shared DB are allowed only on rows you created in that check, and you must delete them afterwards. Never modify or delete existing rows. Prefer reads and rejected-input requests.

## Shared layer (Phase 0, read-only for every area)

| File | Use |
|---|---|
| `app/Auth/Jwt.php` | `encode`, `decode`, `secret` (HS256, Mealie's secret rule) |
| `app/Http/Middleware/MealieAuth.php` | route middleware `mealie:user`, `mealie:admin`, `mealie:optional` = `get_current_user`, `get_admin_user`, `try_get_current_user` |
| `app/Support/CurrentUser.php` | the `users` row of the caller (raw hex ids) |
| `app/Support/Guid.php` | `toDb`, `fromDb`, `requireUuid4`, `requireUuid`, `new` (CHAR(32) hex in SQLite, dashed in JSON) |
| `app/Support/Dates.php` | `out` (`2026-08-06T13:35:24.307376Z`), `date`, `nowDb` |
| `app/Support/Errors.php` | `http` (`{"detail": …}`), `validation` (dev-mode 422 body), `errorResponse` (`ErrorResponse` in `detail`), `unauthorized` |
| `app/Support/Json.php` | `camel`, `camelKeys`, `respond`, `body` (JSON object or 422) |
| `app/Support/Pagination.php` | `PaginationBase` envelope (`page`, `per_page`, `total`, `total_pages`, `items`, `next`, `previous`); simple `orderBy`/`orderDirection` only |
| `config/mealie.php`, `config/database.php` | connection name `mealie` |
| `routes/api.php` | loads `routes/auth-users.php`, `routes/recipes.php`, `routes/households.php`, `routes/groups-admin.php` |

## Files no area may change

Everything in `php-w5/` that is not in an area's own list below, including: `app/Auth/**`, `app/Support/**`, `app/Http/Middleware/**`, `bootstrap/**`, `config/**`, `routes/api.php`, `routes/web.php`, `routes/console.php`, `composer.json`, `composer.lock`, `.env`, `.env.example`, `phpunit.xml`. Also everything outside `php-w5/` except the area's own contract file: `mealie/`, `frontend/`, `tests/`, `compx574/hurl/`, `compx574/workflow-5/`, `dev/`, other areas' files.

If an area needs a shared helper that does not exist, it writes its own copy inside its own namespace and lists it in its contract under "helpers duplicated from / missing in shared layer".

---

## Area 1 — auth, users, app, validators

| | |
|---|---|
| Python | `mealie/routes/auth/auth.py`, `auth/auth_cache.py`, `auth/__init__.py`; `users/_helpers.py`, `users/api_tokens.py`, `users/crud.py`, `users/forgot_password.py`, `users/images.py`, `users/ratings.py`, `users/registration.py`, `users/__init__.py`; `app/app_about.py`, `app/__init__.py`; `validators/validators.py`, `validators/__init__.py` |
| Python routes | 32 (auth 7, users 17, app 3, validators 5) |
| May create | `php-w5/routes/auth-users.php`, `php-w5/app/Areas/AuthUsers/**`, `php-w5/tests/Feature/AuthUsers/**`, `compx574/workflow-5-contracts/area-1.md` |
| Dev port | 9011 |

## Area 2 — recipe, organizers, unit_and_foods, comments, parser

| | |
|---|---|
| Python | `mealie/routes/recipe/_base.py`, `recipe/bulk_actions.py`, `recipe/comments.py`, `recipe/exports.py`, `recipe/recipe_crud_routes.py`, `recipe/shared_routes.py`, `recipe/timeline_events.py`, `recipe/__init__.py`; `organizers/controller_categories.py`, `organizers/controller_tags.py`, `organizers/controller_tools.py`, `organizers/__init__.py`; `unit_and_foods/foods.py`, `unit_and_foods/units.py`, `unit_and_foods/__init__.py`; `comments/__init__.py`; `parser/ingredient_parser.py`, `parser/__init__.py` |
| Python routes | 86 (recipe 45, organizers 22, unit_and_foods 12, comments 5, parser 2) |
| May create | `php-w5/routes/recipes.php`, `php-w5/app/Areas/Recipes/**`, `php-w5/tests/Feature/Recipes/**`, `compx574/workflow-5-contracts/area-2.md` |
| Dev port | 9012 |

## Area 3 — households, media, shared (+ utility_routes)

| | |
|---|---|
| Python | `mealie/routes/households/controller_cookbooks.py`, `controller_group_notifications.py`, `controller_group_recipe_actions.py`, `controller_household_self_service.py`, `controller_invitations.py`, `controller_mealplan.py`, `controller_mealplan_rules.py`, `controller_shopping_lists.py`, `controller_webhooks.py`, `households/__init__.py`; `media/media_recipe.py`, `media/media_user.py`, `media/__init__.py`; `shared/__init__.py`; `mealie/routes/utility_routes.py` (module, not a package — the group's split did not place it) |
| Python routes | 74 (households 64, media 5, shared 4, utils 1) |
| May create | `php-w5/routes/households.php`, `php-w5/app/Areas/Households/**`, `php-w5/tests/Feature/Households/**`, `compx574/workflow-5-contracts/area-3.md` |
| Dev port | 9013 |

Note: `media` is mounted at `/api/media` by `mealie/routes/media/__init__.py` (not under `mealie/routes/__init__.py`); check `mealie/app.py` for how it is included.

## Area 4 — groups, admin, explore

| | |
|---|---|
| Python | `mealie/routes/groups/controller_group_ai_providers.py`, `controller_group_households.py`, `controller_group_reports.py`, `controller_group_self_service.py`, `controller_labels.py`, `controller_migrations.py`, `controller_seeder.py`, `groups/__init__.py`; `admin/admin_about.py`, `admin_backups.py`, `admin_debug.py`, `admin_email.py`, `admin_maintenance.py`, `admin_management_ai_providers.py`, `admin_management_groups.py`, `admin_management_households.py`, `admin_management_users.py`, `admin/__init__.py`; `explore/controller_public_cookbooks.py`, `controller_public_foods.py`, `controller_public_households.py`, `controller_public_organizers.py`, `controller_public_recipes.py`, `explore/__init__.py` |
| Python routes | 80 (groups 27, admin 38, explore 15) |
| May create | `php-w5/routes/groups-admin.php`, `php-w5/app/Areas/GroupsAdmin/**`, `php-w5/tests/Feature/GroupsAdmin/**`, `compx574/workflow-5-contracts/area-4.md` |
| Dev port | 9014 |

---

## 不在范围内 (not in scope)

- `mealie/routes/spa/` (static SPA serving).
- Behaviour that needs a Python-only library or an outside service. The route is left unregistered and listed in the area's contract, unless the request can be fully answered without that dependency (for example a validation error before the call):
  - ingredient parsing with the `nlp` and `brute` strategies (`ingredient-parser-nlp`, CRF model) and the `openai` strategy;
  - recipe scraping from a URL or HTML (`recipe-scrapers`, `services/scraper`), and anything that calls an AI provider;
  - creating, restoring or uploading backups, and the group data migrations from other apps (`services/migrations`);
  - sending email (SMTP) and firing webhooks/Apprise notifications;
  - the scheduler and background tasks.
- The `queryFilter` language (`mealie/services/query_filter`), `orderBy` on related fields, and `orderBy=random` with `paginationSeed`. The shared `Pagination` helper ignores them. Areas must not build their own query-filter parser in this round; they list the affected endpoints.
- Server-sent events, OIDC/OAuth login flows against an outside provider.
- Postgres. SQLite only.
