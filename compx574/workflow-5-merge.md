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

(Filled in after Phase C.)
