# Area 3 contract — households, media, shared, utils

PHP: `php-w5/routes/households.php` (paths without `/api`), classes in `php-w5/app/Areas/Households/`. Port 9013.

Conventions for every endpoint below unless stated:
- JSON keys are the camelCase aliases of the Pydantic schema (MealieModel `alias_generator=camelize`), in schema field order (inherited fields first). Pagination envelopes keep `per_page` / `total_pages` snake_case.
- GUID columns are CHAR(32) lowercase hex in SQLite and are returned dashed (`Guid::fromDb`). Datetimes are returned with `Z` (`Dates::out`).
- "user" = `get_current_user` (mealie/core/dependencies/dependencies.py:102), injected by `BaseUserController.user` (mealie/routes/_base/base_controllers.py:139) or `UserAPIRouter` (mealie/routes/_base/routers.py:20). PHP: middleware `mealie:user`. 401 `{"detail":"Could not validate credentials"}` otherwise.
- Household-scoped repos filter by the caller's `group_id` and `household_id` (`HouseholdRepositoryGeneric`, mealie/repos/repository_generic.py:508, `_filter_builder` :92). Group-scoped repos filter by `group_id` only.
- UUID4 path params: malformed or non-v4 -> 422 (dev-mode body from `Errors::validation`).
- `page_all` default order: `created_at` with `orderDirection` (default `desc`) (repository_generic.py:341). `orderBy` on plain columns only.
- `queryFilter` (user-supplied) is NOT applied anywhere (out of scope); it is only echoed into `next`/`previous` like Python does.
- HttpRepo errors (mealie/routes/_base/mixins.py): not found -> 404 `{"detail":{"message":"Not found.","error":true,"exception":null}}`.
- Events (event bus / apprise / webhooks) that Python publishes after writes are not fired.

## Households: self service — mealie/routes/households/controller_household_self_service.py

| Method & path | Python | Schema | Ids | Who | Not implemented |
|---|---|---|---|---|---|
| GET /api/households/self | get_logged_in_user_household | mealie/schema/household/household.py HouseholdInDB (+ ReadHouseholdPreferences, HouseholdUserSummary, ReadWebhook) | households.id hex -> dashed | user | — |
| GET /api/households/self/recipes/{recipe_slug} | get_household_recipe -> services/household_services/household_service.py get_household_recipe | household.py HouseholdRecipeSummary | slug or UUID (any version) matched against recipes.id/slug in caller's group | user | — |
| GET /api/households/members | get_household_members | schema/user/user.py UserOut, PaginationBase | users.id hex | user + `checks.can_manage()` (controller :43, checks.py:28) -> 403 `{"detail":"Forbidden"}` | user `queryFilter` not combined (only household filter applied); `next` echoes `(household_id=<id>)` like Python |
| GET /api/households/preferences | get_household_preferences | household_preferences.py ReadHouseholdPreferences | hex -> dashed | user | — |
| PUT /api/households/preferences | update_household_preferences | UpdateHouseholdPreferences in, ReadHouseholdPreferences out | — | user + `can_manage_household()` (:57) | — |
| PUT /api/households/permissions | set_member_permissions | household_permissions.py SetPermissions in, UserOut out | body userId UUID4 | user + `can_manage()` (:63); 404 user not found; 403 other group / other household / self (:70-77) | — |
| GET /api/households/statistics | get_statistics -> repos/repository_household.py statistics | household_statistics.py HouseholdStatistics | — | user | — |

## Households: cookbooks — controller_cookbooks.py

| Method & path | Python | Schema | Ids | Who | Not implemented |
|---|---|---|---|---|---|
| GET /api/households/cookbooks | get_all (group-wide repo, household_id=None) | schema/cookbook/cookbook.py ReadCookBook, CookBookPagination | CHAR(32) | user | — |
| POST /api/households/cookbooks (201) | create_one -> repos/repository_cookbooks.py create (slugify + retry "name (n)") | CreateCookBook in, ReadCookBook out | new uuid4 hex | user | non-empty `queryFilterString` is not validated by the query-filter builder |
| PUT /api/households/cookbooks | update_many | list[UpdateCookBook] in, list[ReadCookBook] out | body ids | user; each id must be in caller's household (HttpRepo.update_one -> 404) | same |
| GET /api/households/cookbooks/{item_id} | get_one (group-wide, by id if UUID else slug) | ReadCookBook | UUID or slug | user | — |
| PUT /api/households/cookbooks/{item_id} | update_one | CreateCookBook in, ReadCookBook out | str | user; household-scoped | same |
| DELETE /api/households/cookbooks/{item_id} | delete_one | ReadCookBook | str | user; household-scoped | — |

`queryFilter` in ReadCookBook: `{"parts": []}` for an empty string. Non-empty filter strings are not parsed (out of scope) and also return `{"parts": []}` — known difference.

## Households: event notifications — controller_group_notifications.py

| Method & path | Python | Schema | Ids | Who | Not implemented |
|---|---|---|---|---|---|
| GET /api/households/events/notifications | get_all | schema/household/group_events.py GroupEventNotifierOut, GroupEventPagination | CHAR(32); options row via group_events_notifier_options.event_notifier_id | user | — |
| POST /api/households/events/notifications (201) | create_one | GroupEventNotifierCreate in | new uuid4 | user | — |
| GET /api/households/events/notifications/{item_id} | get_one | GroupEventNotifierOut | UUID4 | user | — |
| PUT /api/households/events/notifications/{item_id} | update_one | GroupEventNotifierUpdate in | UUID4 | user | — |
| DELETE /api/households/events/notifications/{item_id} (204) | delete_one | — | UUID4 | user | — |

## Households: recipe actions — controller_group_recipe_actions.py

| Method & path | Python | Schema | Ids | Who |
|---|---|---|---|---|
| GET /api/households/recipe-actions | get_all | schema/household/group_recipe_action.py GroupRecipeActionOut, Pagination | CHAR(32) | user |
| POST /api/households/recipe-actions (201) | create_one | CreateGroupRecipeAction | new uuid4 | user |
| GET /api/households/recipe-actions/{item_id} | get_one | GroupRecipeActionOut | UUID4 | user |
| PUT /api/households/recipe-actions/{item_id} | update_one | SaveGroupRecipeAction in | UUID4 | user |
| DELETE /api/households/recipe-actions/{item_id} | delete_one | GroupRecipeActionOut | UUID4 | user |

## Households: invitations — controller_invitations.py

| Method & path | Python | Schema | Ids | Who |
|---|---|---|---|---|
| GET /api/households/invitations | get_invite_tokens | schema/household/invite_token.py ReadInviteToken (list) | invite_tokens.id INTEGER (not returned); token string | user + `user.admin` else 403 "Only admins can list invite tokens" (:25) |
| POST /api/households/invitations (201) | create_invite_token | CreateInviteToken in, ReadInviteToken out | token = `secrets.token_urlsafe(24)` equivalent | user; ALLOW_PASSWORD_LOGIN (assumed true); `can_invite` else 403 (:42); non-admin cannot target other group/household (:51) |

## Households: webhooks — controller_webhooks.py

| Method & path | Python | Schema | Ids | Who |
|---|---|---|---|---|
| GET /api/households/webhooks | get_all | schema/household/webhook.py ReadWebhook, WebhookPagination | CHAR(32) | user |
| POST /api/households/webhooks (201) | create_one | CreateWebhook in | new uuid4 | user |
| GET /api/households/webhooks/{item_id} | get_one | ReadWebhook | UUID4 | user |
| PUT /api/households/webhooks/{item_id} | update_one | CreateWebhook in | UUID4 | user |
| DELETE /api/households/webhooks/{item_id} | delete_one | ReadWebhook | UUID4 | user |

`scheduledTime` is stored as TIME text `HH:MM:SS[.ffffff]`; accepted inputs: `HH:MM[:SS[.f]]` (UTC) or an ISO datetime with offset (converted to UTC).

## Households: meal plan rules — controller_mealplan_rules.py

| Method & path | Python | Schema | Ids | Who |
|---|---|---|---|---|
| GET /api/households/mealplans/rules | get_all | schema/meal_plan/plan_rules.py PlanRulesOut, Pagination | CHAR(32) | user |
| POST /api/households/mealplans/rules (201) | create_one | PlanRulesCreate | new uuid4 | user |
| GET /api/households/mealplans/rules/{item_id} | get_one | PlanRulesOut | UUID4 | user |
| PUT /api/households/mealplans/rules/{item_id} | update_one | PlanRulesCreate | UUID4 | user |
| DELETE /api/households/mealplans/rules/{item_id} | delete_one | PlanRulesOut | UUID4 | user |

Same `queryFilter` limitation as cookbooks (non-empty string not validated, parsed JSON always `{"parts": []}`).

## Households: meal plans — controller_mealplan.py

| Method & path | Python | Schema | Ids | Who | Not implemented |
|---|---|---|---|---|---|
| GET /api/households/mealplans | get_all (start_date/end_date) | schema/meal_plan/new_meal.py ReadPlanEntry (+ recipe/recipe.py RecipeSummary), PlanEntryPagination | group_meal_plans.id INTEGER; household = users.household_id of the entry's user | user | user `queryFilter`; no next/previous (Python does not set them) |
| POST /api/households/mealplans (201) | create_one | CreatePlanEntry | autoincrement int | user | — |
| GET /api/households/mealplans/today | get_todays_meals | list[ReadPlanEntry] | — | user | server-local date (container TZ) |
| GET /api/households/mealplans/{item_id} | get_one | ReadPlanEntry | int path (422 if not int) | user | — |
| PUT /api/households/mealplans/{item_id} | update_one | UpdatePlanEntry | int | user | — |
| DELETE /api/households/mealplans/{item_id} | delete_one | ReadPlanEntry | int | user | — |

## Shared recipes — mealie/routes/shared/__init__.py

| Method & path | Python | Schema | Ids | Who |
|---|---|---|---|---|
| GET /api/shared/recipes | get_all (optional recipe_id UUID4) | schema/recipe/recipe_share_token.py RecipeShareTokenSummary (list) | CHAR(32) | user (UserAPIRouter) |

## Media — mealie/routes/media/*.py (mounted at /api/media, no auth)

| Method & path | Python | Files | Who |
|---|---|---|---|
| GET /api/media/recipes/{recipe_id}/images/{file_name} | media_recipe.py get_recipe_img | `<data>/recipes/<dashed id>/images/<original.webp|min-original.webp|tiny-original.webp>`; other names 422 | public |
| GET /api/media/recipes/{recipe_id}/images/timeline/{timeline_event_id}/{file_name} | get_recipe_timeline_event_img | `<data>/recipes/<id>/images/timeline/<event id>/<file>` | public |
| GET /api/media/recipes/{recipe_id}/assets/{file_name} | get_recipe_asset | `<data>/recipes/<id>/assets/<file>`, attachment + nosniff | public |
| GET /api/media/users/{user_id}/{file_name} | media_user.py get_user_image | `<data>/users/<id>/<file>`, image/webp | public |
| GET /api/media/docker/validate.txt | media/__init__.py get_validation_text | `<data>/docker-validation/validate.txt` | public |

## Utils — mealie/routes/utility_routes.py

| Method & path | Python | Who |
|---|---|---|
| GET /api/utils/download?token= | download_file + core/dependencies validate_file_token (:178) | public; token = JWT with `file` claim signed with the app secret; file must be under backups/ or groups/ |

## Not implemented

| Route | Reason |
|---|---|
| POST /api/households/events/notifications/{item_id}/test | sends an Apprise notification (outside service) |
| POST /api/households/recipe-actions/{item_id}/trigger/{recipe_slug} | fires an HTTP POST to an outside URL in a background task; also needs full Recipe serialization |
| POST /api/households/invitations/email | sends email (SMTP) |
| POST /api/households/webhooks/rerun | fires webhooks |
| POST /api/households/webhooks/{item_id}/test | fires a webhook |
| POST /api/households/mealplans/random | needs rule `queryFilter` evaluation and `orderBy=random` with seed |
| GET/POST/PUT/DELETE /api/households/shopping/lists, /{item_id}, PUT /{item_id}/label-settings, POST /{item_id}/recipe, POST /{item_id}/recipe/{recipe_id}, POST /{item_id}/recipe/{recipe_id}/delete (9) | ShoppingListService (item merging, unit/food conversion, recipe ingredient scaling) and ShoppingListItemOut `display` computation (ingredient formatting) are too large to reproduce faithfully this round |
| GET/POST /api/households/shopping/items, POST /create-bulk, GET/PUT/DELETE /{item_id}, PUT/DELETE "" (8) | same |
| POST /api/shared/recipes, GET /api/shared/recipes/{item_id}, DELETE /api/shared/recipes/{item_id} | return RecipeShareToken with the full `Recipe` (ingredients, instructions, nutrition, settings, assets, notes, comments…), which is area 2's serializer |

## Helpers duplicated from / missing in shared layer

- `Households\Support\Paginator`: own copy of the pagination envelope. The shared `Pagination` helper (a) turns `perPage=-1` on an empty table into `per_page: 1` (Python returns 0), (b) cannot put a fixed `queryFilter` (e.g. `(household_id=…)`) into `next`, (c) cannot skip next/previous (mealplans), (d) 500s on unknown `orderBy` columns (Python: 400 `Invalid order_by statement …`).
- `Households\Support\Slug`: python-slugify equivalent (not in shared layer).
- `Households\Support\Http`: HttpRepo 404 body and an "integer path param" validator (shared layer has only UUID validators).
- `Households\Support\RecipeSummary`: RecipeSummary serializer for meal plan entries (area 2 owns recipes; no shared serializer).
