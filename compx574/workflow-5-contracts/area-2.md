# Area 2 contract — recipe, organizers, unit_and_foods, comments, parser

PHP: routes in `php-w5/routes/recipes.php`, classes in `php-w5/app/Areas/Recipes/` (namespace `App\Areas\Recipes`). Dev port 9012.

Conventions used by every endpoint below unless stated otherwise:

- Ids: GUID columns are CHAR(32) lowercase hex in SQLite (`Guid::toDb`), returned dashed (`Guid::fromDb`). Integer ids (`recipes_ingredients.id`, `recipe_assets.id`, ...) are never exposed.
- Path params typed `UUID4` in Python are checked with the UUID4 rule (malformed or non-v4 → 422 dev-mode body). Messages copy Pydantic's text but cannot copy the Python file/line trailer, so 422 bodies match on status and keys, not on `message`.
- Body models: a non-object JSON body (e.g. `0`) → 422; missing required fields → 422.
- Auth: "user" = `get_current_user` (mealie/core/dependencies/dependencies.py), here `mealie:user` → 401 `{"detail":"Could not validate credentials"}`. Admins are not special unless stated.
- JSON keys are camelCase (MealieModel `alias_generator=camelize`) except the pagination envelope (`page`, `per_page`, `total`, `total_pages`, `items`, `next`, `previous`).
- Datetimes: naive UTC from SQLite returned as `...Z` (Pydantic). `GET /api/recipes` is serialised by orjson in Python, so its datetimes use `+00:00`.
- Pagination (`PaginationQuery`, mealie/schema/response/pagination.py): page, perPage (-1 = all), orderBy (plain column, `col:dir` and comma lists), orderDirection, orderByNullPosition; default order `created_at desc` when no orderBy and no search. `next`/`previous` built like `set_pagination_guides` with the router-relative path (`/categories`, `/units`, `/timeline/events`, ...).
- `search` (tokenized LIKE search, mealie/schema/_mealie/mealie_model.py `filter_search_query`): tags/categories/tools on `name`; foods on `name_normalized`, `plural_name_normalized`; units also on abbreviations; recipes on name/description/ingredient notes (normalized).

## Organizers — mealie/routes/organizers/

All: user (BaseCrudController/BaseUserController → `get_current_user`, mealie/routes/_base/base_controllers.py:139). Repos are group-scoped (`group_id` = caller's group).

| Method + path | Python | Schema | Permission | Not implemented |
|---|---|---|---|---|
| GET /api/organizers/categories | controller_categories.py:get_all | RecipeCategoryPagination / RecipeCategory (mealie/schema/recipe/recipe.py) — id, groupId, name, slug, recipeCount (count from recipes_to_categories) | user | queryFilter, related-field orderBy |
| POST /api/organizers/categories (201) | controller_categories.py:create_one | in CategoryIn; out CategoryOut (recipe_category.py) — id, groupId, name, slug, recipeCount | user + `can_organize` (controller_categories.py:54, checks.py:38) → 403 `{"detail":"Forbidden"}` | event bus |
| GET /api/organizers/categories/empty | controller_categories.py:get_all_empty | list[CategoryBase] — name, id, groupId, slug. Not group-filtered (repository_factory.py:103) | user | — |
| POST /api/organizers/categories/merge | controller_categories.py:merge_categories | in CategoryMerge (fromId, toId UUID4); out CategoryOut | user + can_organize (:80); 400 same ids; 404 from/to not found (string detail) | — |
| GET /api/organizers/categories/{item_id} | controller_categories.py:get_one | CategorySummary — id, slug, name | user | — |
| PUT /api/organizers/categories/{item_id} | controller_categories.py:update_one | in CategoryIn; out CategorySummary | user + can_organize (:102); 404 ErrorResponse "Not found."; 409 on duplicate slug | event bus |
| DELETE /api/organizers/categories/{item_id} | controller_categories.py:delete_one | returns `null` (200) | user + can_organize (:128); missing id → 404 ErrorResponse (NoResultFound via HttpRepo.delete_one) | — |
| GET /api/organizers/categories/slug/{category_slug} | controller_categories.py:get_one_by_slug | RecipeCategoryResponse — id, slug, name, recipes: list[RecipeSummary] (group recipes in that category) | user | — |
| GET /api/organizers/tags | controller_tags.py:get_all | RecipeTagPagination / RecipeTag | user | as categories |
| GET /api/organizers/tags/empty | controller_tags.py:get_empty_tags | no response_model; raw ORM objects (checked against Python) | user | — |
| POST /api/organizers/tags/merge | controller_tags.py:merge_tags | TagMerge → TagOut (name, groupId, id, slug, recipeCount) | user + can_organize (:49) | — |
| GET /api/organizers/tags/{item_id} | controller_tags.py:get_one | RecipeTagResponse — name, id, groupId, slug, recipes[] (RecipeSummary) | user | — |
| POST /api/organizers/tags (201) | controller_tags.py:create_one | TagIn → TagOut | user + can_organize (:69) | event bus |
| PUT /api/organizers/tags/{item_id} | controller_tags.py:update_one | TagIn → RecipeTagResponse | user + can_organize (:91); missing → 500 (repo.update raises NoResultFound, unhandled) | — |
| DELETE /api/organizers/tags/{item_id} | controller_tags.py:delete_recipe_tag | `null`; missing → 400 `{"detail":"Bad Request"}` | user + can_organize (:117) | — |
| GET /api/organizers/tags/slug/{tag_slug} | controller_tags.py:get_one_by_slug | RecipeTagResponse; missing → 500 (None fails response validation) | user | — |
| GET /api/organizers/tools | controller_tools.py:get_all | RecipeToolPagination / RecipeTool — id, groupId, name, slug, recipeCount (always 0), householdsWithTool (household slugs) | user | as categories |
| POST /api/organizers/tools (201) | controller_tools.py:create_one | RecipeToolCreate (name, householdsWithTool) → RecipeTool | user (no organize check) | — |
| GET /api/organizers/tools/{item_id} | controller_tools.py:get_one | RecipeTool | user | — |
| PUT /api/organizers/tools/{item_id} | controller_tools.py:update_one | RecipeToolCreate → RecipeTool | user | — |
| DELETE /api/organizers/tools/{item_id} | controller_tools.py:delete_one | RecipeTool (deleted row) | user | — |
| GET /api/organizers/tools/slug/{tool_slug} | controller_tools.py:get_one_by_slug | RecipeToolResponse — name, householdsWithTool, id, groupId, slug, recipes[]; missing → 500 | user | — |

## Foods / units — mealie/routes/unit_and_foods/

| Method + path | Python | Schema | Permission | Not implemented |
|---|---|---|---|---|
| GET /api/foods | foods.py:get_all | IngredientFoodPagination / IngredientFood (recipe_ingredient.py): id, name, pluralName, description, extras{}, labelId, aliases[{name}], substitutions[{substituteFoodId, note, substituteFood{id,name,pluralName}}], householdsWithIngredientFood (slugs), label (MultiPurposeLabelSummary: name, color, groupId, id), createdAt, updatedAt | user | queryFilter |
| POST /api/foods (201) | foods.py:create_one | CreateIngredientFood → IngredientFood | user + can_organize (foods.py:51) | — |
| PUT /api/foods/merge | foods.py:merge_one | MergeFood (fromFood, toFood) → SuccessResponse `{"message","error":false}`; failure → 500 `{"detail":"Failed to merge foods"}` | user + can_organize (:57) | — |
| GET /api/foods/{item_id} | foods.py:get_one | IngredientFood | user | — |
| PUT /api/foods/{item_id} | foods.py:update_one | CreateIngredientFood → IngredientFood | user + can_organize (:71) | — |
| DELETE /api/foods/{item_id} | foods.py:delete_one | IngredientFood (deleted) | user + can_organize (:77) | — |
| GET /api/units | units.py:get_all | IngredientUnitPagination / IngredientUnit: id, name, pluralName, description, extras, fraction, abbreviation, pluralAbbreviation, useAbbreviation, aliases, standardQuantity, standardUnit, createdAt, updatedAt | user | queryFilter |
| POST /api/units (201) | units.py:create_one | CreateIngredientUnit → IngredientUnit | user | standardized-unit autodetect from locale seed files (`_add_standardized_unit`) only for en-US names |
| PUT /api/units/merge | units.py:merge_one | MergeUnit (fromUnit, toUnit) → SuccessResponse | user | — |
| GET /api/units/{item_id} | units.py:get_one | IngredientUnit | user | — |
| PUT /api/units/{item_id} | units.py:update_one | CreateIngredientUnit → IngredientUnit | user | — |
| DELETE /api/units/{item_id} | units.py:delete_one | IngredientUnit (deleted) | user | — |

Ids: CHAR(32) hex; aliases have their own CHAR(32) id + parent id (composite PK).

## Comments — mealie/routes/comments/__init__.py, mealie/routes/recipe/comments.py

| Method + path | Python | Schema | Permission | Not implemented |
|---|---|---|---|---|
| GET /api/comments | comments:get_all | RecipeCommentPagination / RecipeCommentOut: id, recipeId, text, createdAt, updatedAt, userId, user{id, username, admin, fullName}. Group scope through the recipe | user | queryFilter |
| POST /api/comments (201) | comments:create_one | RecipeCommentCreate (recipeId UUID4, text stripped, non-empty) → RecipeCommentOut | user | — |
| GET /api/comments/{item_id} | comments:get_one | RecipeCommentOut; 404 ErrorResponse "Not found." | user | — |
| PUT /api/comments/{item_id} | comments:update_one | RecipeCommentUpdate (id, text) → RecipeCommentOut | user; owner or admin (comments/__init__.py:35-41) → 403 `{"detail":{"message":"Comment does not belong to user","error":true,"exception":null}}`; missing id → 500 | — |
| DELETE /api/comments/{item_id} | comments:delete_one | SuccessResponse "Comment deleted" | same as PUT | — |
| GET /api/recipes/{slug}/comments | recipe/comments.py:get_recipe_comments | list[RecipeCommentOut]; unknown slug → 500 | user (UserAPIRouter) | — |

## Recipes — mealie/routes/recipe/

| Method + path | Python | Schema | Permission | Not implemented |
|---|---|---|---|---|
| GET /api/recipes/exports | exports.py:get_recipe_formats_and_templates | FormatResponse `{"json":["raw"],"zip":["zip"]}` | user | — |
| GET /api/recipes | recipe_crud_routes.py:get_all | PaginationBase[RecipeSummary] (recipe.py): id, userId, householdId, groupId, name, slug, image, recipeServings, recipeYieldQuantity, recipeYield, totalTime, prepTime, cookTime, performTime, description, recipeCategory[], tags[], tools[], rating, orgURL, dateAdded, dateUpdated, createdAt, updatedAt, lastMade. Group-wide (not household) | user | queryFilter, cookbook, orderBy=random, rating/lastMade per-user aliases in orderBy, `foods` filter via substitutions |
| GET /api/recipes/{slug} | recipe_crud_routes.py:get_one | Recipe (summary + recipeIngredient, recipeInstructions, nutrition, settings, assets, notes, extras, comments). Slug or UUID; 404 ErrorResponse "No Entry Found" | user | — |
| GET /api/recipes/shared/{token_id} | shared_routes.py:get_shared_recipe | Recipe; expired/missing → 404 ErrorResponse "Token Not Found" (expired token row deleted) | public (no auth) | — |
| GET /api/recipes/timeline/events | timeline_events.py:get_all | RecipeTimelineEventPagination / RecipeTimelineEventOut: recipeId, userId, subject (system subjects translated en-US), eventType, eventMessage, image, timestamp, id, groupId, householdId, createdAt, updatedAt | user | queryFilter |
| POST /api/recipes/timeline/events (201) | timeline_events.py:create_one | RecipeTimelineEventIn → Out; 404 `{"detail":"recipe not found"}` | user | event bus |
| GET /api/recipes/timeline/events/{item_id} | timeline_events.py:get_one | Out | user | — |
| PUT /api/recipes/timeline/events/{item_id} | timeline_events.py:update_one | RecipeTimelineEventUpdate (subject, eventMessage, image) → Out (patch semantics) | user | — |
| DELETE /api/recipes/timeline/events/{item_id} | timeline_events.py:delete_one | Out (deleted) | user | image directory removal |
| GET /api/recipes/bulk-actions/export | bulk_actions.py:get_exported_data | list[GroupDataExport]: id, groupId, name, filename, path, size, expires (str), createdAt? (per schema) | user | — |

## Not implemented (route left unregistered)

| Route | Reason |
|---|---|
| POST /api/recipes/test-scrape-url, POST /api/recipes/create/url, /create/url/stream, /create/url/bulk, /create/html-or-json, /create/html-or-json/stream | recipe scraping (recipe-scrapers, outside service) — out of scope |
| POST /api/recipes/create/ai, /create/ai/stream, /create/image | AI provider — out of scope |
| POST /api/recipes/create/zip | archive import (file upload + migration service) |
| GET /api/recipes/suggestions | RecipeSuggestionMixin ranking not ported (time) |
| POST /api/recipes | RecipeService.create_one: defaults, household preferences, timeline event — not ported (time) |
| PUT/PATCH /api/recipes, PUT/PATCH /api/recipes/{slug}, POST /api/recipes/{slug}/duplicate, PATCH /api/recipes/{slug}/last-made, DELETE /api/recipes/{slug} | full Recipe write path (nested ingredients/instructions/organizers, permission SQL, asset dirs) — not ported (time) |
| POST/PUT/DELETE /api/recipes/{slug}/image, POST /api/recipes/{slug}/assets, POST /api/recipes/{slug}/assets/url | image processing / file storage / URL download |
| GET /api/recipes/{slug}/exports | template rendering to files (zip) |
| POST /api/recipes/bulk-actions/tag, /settings, /categorize, /delete | bulk recipe writes — not ported (time) |
| POST /api/recipes/bulk-actions/export, GET /api/recipes/bulk-actions/export/{export_id}/download, DELETE /api/recipes/bulk-actions/export/purge | export archives on disk / file tokens |
| PUT /api/recipes/timeline/events/{item_id}/image | image processing |
| GET /api/recipes/shared/{token_id}/zip | zip file response with image |
| POST /api/parser/ingredient, POST /api/parser/ingredients | nlp/brute/openai parsers (Python-only library / AI) — out of scope |

## Helpers duplicated from / missing in shared layer

- `App\Areas\Recipes\Support\Paginator` — own copy of pagination because the shared `Pagination` (a) uses `max(total,1)` for perPage=-1 (Python returns `per_page = total`, `total_pages = 0` when empty), (b) ignores page=-1 (last page), (c) has no search ordering, (d) turns unknown orderBy into a SQL error instead of 400, (e) cannot build the merged query-string `next` used by `GET /api/recipes`.
- `App\Areas\Recipes\Support\Out` — datetime output that drops a `.000000` fraction like Pydantic, plus the orjson `+00:00` variant.
- `App\Areas\Recipes\Support\Text` — `slugify` (python-slugify defaults incl. unidecode) and `normalize` (SqlAlchemyBase.normalize) — not in shared layer.
- Translation of the few en-US strings needed (`recipe.recipe-created`, etc.) — no i18n helper in shared layer.
