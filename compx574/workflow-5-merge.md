# Workflow 5 — merge conflicts after Phase B

Written by the orchestrator after all four sub-agents returned (commit `72720e4f8`). Following the group's Phase B instruction, differences are listed here and **not** resolved in Phase B. Only the five kinds the instruction names are listed: duplicated helper code, different JSON key styles, different route prefixes, different id formats, different permission rules.

How each was checked:
- Code: function/class inventory of `php-w5/app/Areas/**` (function names defined in more than one area; files with the same job).
- API output: `workflow-5/shape_compare.py` fetched every GET path in `parity.hurl` from Python :9000 and PHP :9001 and compared recursive key sets and looked for undashed 32-hex ids. Non-admin `bob`: 64 paths where both return 200, 0 key-set differences, 0 undashed ids (`results/p2-shape.txt`). Admin `mikexiao`: 77 paths, 0 and 0 (`results/p2-shape-admin.txt`).
- Permissions: `workflow-5/perm_compare.py` compared status codes on every GET path PHP registers, as non-admin, admin and with no token: 105/105, 105/105, 106/106 equal (`results/p2-permissions.txt`). Write routes were only checked by the sub-agents themselves.

## 1. Duplicated helper code

| # | What | Copies | Notes |
|---|---|---|---|
| 1.1 | Auth middleware wrapper around `MealieAuth` | 4: `AuthUsers/Http/RequireUser`, `Recipes/Support/Auth` (+ `Recipes/Controllers/Base::callAction` catching `HttpResponseException`), `Households/Support/UserAuth`, `GroupsAdmin/Support/Auth` (25 lines each, different files) | All written to work around the Phase 0 renderer bug (fixed at 12:51). Now redundant. Used by 8 route groups. |
| 1.2 | Paginator | 3 + shared: `Recipes/Support/Paginator` (251 lines), `Households/Support/Paginator` (176), `GroupsAdmin/Support/Pager` (197); shared `App\Support\Pagination` used by no area (only its `snake()` once) | Every area found the same gaps in the shared helper: `perPage=-1`, `page=-1`, 400 for unknown/non-filterable `orderBy`, search, fixed filter in `next`, OFFSET without LIMIT on SQLite. |
| 1.3 | slugify / unidecode | 3 slugify (`AuthUsers/Http/ValidatorsController::slugify`, `Recipes/Support/Text::slugify`, `GroupsAdmin/Support/Fs::slugify`), plus `Households/Support/Slug`; 2 unidecode (`Recipes/Support/Text`, `GroupsAdmin/Support/Search`) | Python has one (`python-slugify`). |
| 1.4 | "Not found." HttpRepo error body | 3: `Recipes/Controllers/Base::notFound`, `Households/Support/Http::notFound`, `GroupsAdmin/Support/Checks::notFound` | Python: `ErrorResponse.respond(message="Not found.")` in `mealie/routes/_base/mixins.py`. |
| 1.5 | RecipeSummary serializer | 2 full + 1 partial: `Recipes/Support/RecipeMap::summaries`, `Households/Support/Out::recipeSummary`; `GroupsAdmin` builds recipe tag/category/tool bits (`tagOut`, `recipeTag`, `toolHouseholds` also in Recipes) | Area 3 and area 4 left routes unregistered because they would need area 2's full Recipe serializer (shared recipes, explore recipes). |
| 1.6 | Request-body / 422 builders | 4: `AuthUsers/Support/Pyd` (440 lines) + `Uuid`, `Recipes/Support/Input`, `Households/Support/Input`, `GroupsAdmin/Support/Validator` (322) | Different fidelity: area 1 reproduces Python's message text, others only the status and shape. |
| 1.7 | Settings / Db wrappers | `AuthUsers/Support/Settings` + `GroupsAdmin/Support/Settings`; `Recipes/Support/Db` + `GroupsAdmin/Support/Db` | Small. |

## 2. Different JSON key styles

None found in API output (0 key-set differences on 64 + 77 GET paths). All three paginators emit `per_page`/`total_pages` like Python's `PaginationBase`. Internally the areas build response arrays differently (literal camelCase keys vs mapping functions), which is not visible to clients.

## 3. Different route prefixes

No functional conflict: no route file repeats `/api`; all paths resolve to the Python paths (status-equal on all registered GETs). Style differs only: area 3 writes a leading `/` (`'/households/cookbooks'`), area 4 uses `Route::prefix()` groups, areas 1–2 write full relative paths; path parameter names differ (`{groupSlug}`, `{slug}`, `{item_id}`).

## 4. Different id formats

None in API output (0 undashed ids). Internally area 1 uses its own `Uuid` helper next to the shared `Guid`; others use `Guid`.

## 5. Different permission rules

None in GET status codes for three callers (non-admin, admin, anonymous). The implementation of the same rule is duplicated (1.1), and in-handler checks (`can_manage`, `can_organize`, household ownership) are written per area (`GroupsAdmin/Support/Checks`, inline elsewhere). Write-route permissions were verified only by the sub-agents.

---

## Gate B — marked fixes

Reviewer: orchestrator (Derek delegated review). Rule used: fix duplicates where one shared version can replace the copies without changing any response; record the rest. Acceptance for Phase C, checked by the orchestrator afterwards: `measure.sh` score not below 189/265; `accuracy_compare_w5.py` not below 37/40; `perm_compare.py` 0 differences for all three callers; `shape_compare.py` 0 differences for both users; no route added or removed.

| # | Decision | Fix |
|---|---|---|
| 1.1 | **FIX** | Delete the four wrappers and `Recipes/Controllers/Base::callAction`. Route files use the shared aliases `mealie:user` / `mealie:admin` / `mealie:optional`, choosing per route what the wrapper did. |
| 1.2 | **FIX** | Replace `App\Support\Pagination` with one paginator that covers what the three area versions do (behaviour of each must be preserved per route: allowed `orderBy` columns, default order, search, fixed filters in `next`/`previous`, `perPage=-1`, `page=-1`). The three areas call it; delete their copies. |
| 1.3 | **FIX** | One `App\Support\Text::slugify` and `::unidecode` (start from `Recipes/Support/Text`); delete the copies and call the shared one. |
| 1.4 | **FIX** | Add `Errors::notFound()` (HttpRepo "Not found." body) to the shared `Errors`; delete the three copies. |
| 1.5 | KEEP | Record only. Unifying the recipe serializer would mainly unlock routes that are not registered, and Phase C must not add routes. |
| 1.6 | KEEP | Record only. Message text is not asserted anywhere; merging four validators is large and risks response changes. |
| 1.7 | KEEP | Record only (small). |
| 2–5 | KEEP | No conflict visible to clients. |

## Phase C changes

Only rows 1.1–1.4 were changed. No route was added or removed (188 routes before and after); no migration. Totals for `php-w5/` (git, with rename detection): 41 files, +460 / −1113 lines.

| # | Deleted | Added / edited |
|---|---|---|
| 1.1 | `AuthUsers/Http/RequireUser`, `Recipes/Support/Auth`, `Households/Support/UserAuth`, `GroupsAdmin/Support/Auth`, `Recipes/Controllers/Base::callAction` | The four route files use `mealie:user` (and `mealie:admin` for `/admin`), the same mode each wrapper used. Thrown `HttpResponseException`s are rendered by the existing handler in `bootstrap/app.php`. |
| 1.2 | `Recipes/Support/Paginator` (251), `Households/Support/Paginator` (176), `GroupsAdmin/Support/Pager` (197), `GroupsAdmin/Support/Search` (71) | `App\Support\Pagination` rewritten (287 lines): one `page($request, $query, $map, $route, $opt)` with options `table`, `columns` (`name => true` for lower(), `false`, or a raw SQL expression; `created_at`/`update_at` are always allowed), `model` (other table columns give "Cannot filter on Model.col"), `search`/`normalizeSearch`/`searchExtra`, `queryFilter` (fixed filter for next/previous), `guides` (`merge` for GET /recipes), `route = null` (no guides). The 26 paginated routes call it with the columns, search, default order and fixed filter they had before. |
| 1.3 | `Recipes/Support/Text`, `Households/Support/Slug`, `GroupsAdmin/Support/Fs::slugify`, `AuthUsers/Http/ValidatorsController::slugify`, `GroupsAdmin/Support/Search::unidecode` | `App\Support\Text` (from `Recipes/Support/Text`: `slugify`, `unidecode`, `normalize`, `PUNCTUATION`). `slugify` also decodes HTML entities after unidecode, as python-slugify does (the `AuthUsers` copy did this). |
| 1.4 | `Recipes/Controllers/Base::notFound`, `Households/Support/Http::notFound`, `GroupsAdmin/Support/Checks::notFound` | `Errors::notFound()` added. The call sites use it. |

### Regression check (PHP :9015 before vs after, same data)

- GET set: every GET route (176 concrete paths with real and unknown ids) × admin, bob and no token. The 26 paginated routes also had 29 query variants (`perPage=-1`, `page=2&perPage=1`, `orderBy=nope`, `page=-1`, search, bad ints/enums, `queryFilter`, snake-case names, …) × 3 callers, plus 46 `orderBy` values × admin and bob. That is 5215 requests. The baseline was recorded twice (0 differences). Empty lists were seeded with 2 rows each first and the rows were deleted afterwards.
- Result: **385 of 5215 differ**. 0 differ on plain paths except 3 storage-size bodies, which changed because files on disk changed between runs. Python now gives the same bodies. The 382 query-variant differences come from area-specific edge behaviour that one shared paginator cannot keep. In each case the shared version takes the variant that matches Python:
  - 339 now equal Python (status + body; 422 compared without Python's traceback/ctx). These cover Households/GroupsAdmin 422 message text in the area-2 format (148), `orderBy=updatedAt` 400→200 (32), `perPage=-2` 500→200 (29), snake-case `per_page`/`order_by` now ignored (69), `orderBy=NAME` 200→400 (16), `orderBy=UserId` 400→200 (2), `"name:asc" is invalid` message (7), `orderBy=random&paginationSeed=1` 400→200 (16), and search on comments/timeline now keeps the default `created_at` order (20).
  - 15 now match Python's status only: random order is accepted but not shuffled (13), and timeline row order (2).
  - 28 still differ from Python: `orderBy=random` without a seed is a 422 in the area-2 format, while Python returns a 500 (26). `comments?orderBy=UserId` is now 200 like the existing `userId`, because the area-2 column list treats `user_id` as filterable and Python does not. The column list was not changed (2).
- Status parity with Python over the whole set: 4940 → 5062 of 5215. Plain paths: 558/558 before and after.
- Write routes (443 requests, run against the old and the new code on rows created and deleted by the check): every write route with no token and as bob, admin PUT/DELETE on unknown ids for every item route, and create/get/update/delete of tools, categories, tags, cookbooks, labels, admin groups and admin households with names containing `'`, `&amp;`, `1,000` and CJK text. **0 differences in auth, not-found or error bodies**. 34 differ, all in `slug`: `&amp;` → `a-b`, `1,000` → `1000` (cookbooks), CJK → pinyin (cookbooks, admin groups/households). Each new slug equals python-slugify's output. 4 bob POSTs differ only because the earlier run had already created rows with the same name.
- Leftover rows from the checks: 0. These checks did not use `run.sh`, `measure.sh`, `perm_compare.py` or `shape_compare.py`.
