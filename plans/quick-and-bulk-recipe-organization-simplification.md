# Quick and Bulk Recipe Organization Simplification Plan

## Scope

This audit covers only changes introduced by `upstream/mealie-next...HEAD` on
`agent/quick-and-bulk-recipe-organization`. It intentionally excludes pre-existing
Mealie code, even when a changed component contains older complexity.

The feature architecture is sound: quick organization reuses the existing organizer
selector and recipe PATCH API, while bulk add/remove uses a dedicated atomic endpoint
with permission, scope, and event handling. The remediation below targets localized
branch-added bloat without changing any visible behavior.

## Findings

### 1. Remove the hand-written query serializer

**Files:**

- `frontend/app/components/Domain/Recipe/RecipeCardSection.vue`
- `frontend/app/components/Domain/Recipe/__tests__/recipe-card-section-selection.test.ts`

`stableSerialize()` recursively canonicalizes the search query so a Select All response
can be rejected after the query changes. That check is redundant: the same branch-added
watcher calls `clearSelection()`, which increments `selectAllGeneration`. The generation
already invalidates the pending request.

Actions:

1. Remove `stableSerialize()` and `querySnapshot`.
2. Change `isCurrentSelectAllRequest()` to check only the generation and selection mode.
3. Remove the unmount invalidation; a completed promise assigning to component-local refs
   after unmount has no user-visible effect and does not justify a lifecycle hook.
4. Retain query-change, exit-selection, and newer-request invalidation through the
   generation counter.

### 2. Remove the one-use organizer transform abstraction

**Files:**

- `frontend/app/components/Domain/Recipe/RecipeQuickOrganizeDialog.vue`
- `frontend/app/components/Domain/Recipe/recipe-organizer-transform.ts`
- `frontend/app/components/Domain/Recipe/__tests__/recipe-organizer-transform.test.ts`

The transform module exists only to return `{ tags, recipeCategory }`. Its fallback
deduplication by ID, slug, and normalized name is not part of the existing organizer
editor pattern and protects against data the selector should not produce. Its sole test
only verifies that two empty arrays remain two empty arrays.

Actions:

1. Build the single-recipe PATCH payload directly in `saveOne()` from the dialog's local
   `tags` and `recipeCategory` state.
2. Delete `recipe-organizer-transform.ts` and its test.
3. Preserve the current deep copies made when the dialog opens so cancel/save never
   mutates the input recipe.

### 3. Remove dead dialog configuration

**File:** `frontend/app/components/Domain/Recipe/RecipeQuickOrganizeDialog.vue`

The custom `card-actions` slot replaces `BaseDialog`'s submit controls. Consequently,
`can-submit`, `keep-open`, `submit-disabled`, and `@submit` do not drive the visible Save
button or BaseDialog submission state. They make the dialog appear to use two submission
mechanisms when it uses only the custom actions.

Actions:

1. Remove the dead BaseDialog props and `@submit` listener.
2. Keep `disable-submit-on-enter`: BaseDialog otherwise emits submit on Enter even when
   `can-submit` is false.
3. Keep the custom actions because they prevent cancellation during an active request.

### 4. Simplify branch-added recipe-card click handlers

**Files:**

- `frontend/app/components/Domain/Recipe/RecipeCard.vue`
- `frontend/app/components/Domain/Recipe/RecipeCardMobile.vue`

The normal-mode half of each new `handleCardClick()` checks event targets and then does
nothing regardless of the result; the overlay `NuxtLink` owns navigation. Only selection
mode needs the card click handler.

Actions:

1. Return immediately when selection mode is off.
2. In selection mode, retain the interactive-descendant guard and emit exactly once.
3. Keep the overlay-link structure and explicit organizer-button propagation controls;
   they solve the real nested-action/navigation problem.
4. Do not introduce a composable or shared card wrapper for this small duplication; that
   would replace straightforward code with another abstraction.

### 5. Collapse duplicate controller error handling

**File:** `mealie/routes/recipe/bulk_actions.py`

The branch adds separate `SQLAlchemyError` and generic `Exception` handlers that return
the same status and response shape. The distinction affects only the log message and does
not justify another branch or the SQLAlchemy import.

Actions:

1. Keep explicit 403 and 404 mappings.
2. Replace the two 500 handlers with one logged generic handler.
3. Import `NoEntryFound` directly alongside `PermissionDenied` instead of adding a second
   exceptions import style.

### 6. Trim and correct branch-added documentation

**Files:**

- `docs/docs/contributors/developers-guide/migration-guide.md`
- `docs/docs/documentation/getting-started/features.md`

The 76-line endpoint reference is not a migration and duplicates generated OpenAPI
documentation. The Features guide also places the Tools demo button after the new Bulk
Organization section and claims Data Management has a new combined Organize action,
although this branch adds the combined workflow to recipe cards/search results.

Actions:

1. Remove the bulk endpoint reference from the migration guide.
2. Keep a short user-facing Bulk Organization paragraph in the Features guide.
3. Put the Tools demo button back directly under the Tools subsection.
4. Link integrations directly to Swagger/API usage if a link is useful; do not reproduce
   request and response schemas in prose.
5. Remove the inaccurate `Data Management -> Organize` bullet. Existing Tag and
   Categorize actions remain unchanged.

### 7. Reduce branch-added test ceremony while retaining risk coverage

**Files:**

- `frontend/app/components/Domain/Recipe/__tests__/recipe-card-section-selection.test.ts`
- `frontend/app/components/Domain/Recipe/__tests__/recipe-quick-organize-dialog.test.ts`
- `tests/integration_tests/user_recipe_tests/test_recipe_bulk_action.py`

The test suite contains valuable authorization, scoping, atomicity, and navigation
coverage. The issue is repeated setup and multiple tests for nearly identical defensive
states.

Actions:

1. Delete the transform test with its production module.
2. Retain one stale-query test and one overlapping-request test; remove the unmount-only
   case and redundant stale rejection/spinner variants.
3. Parameterize bulk add/remove dialog payload tests instead of repeating the complete
   interaction.
4. Keep single-recipe clearing, failure behavior, double-submit prevention, card
   navigation, keyboard selection, permission, cross-group, cross-household, and event
   tests.
5. Replace the integration test that monkeypatches global `Session.commit` call order.
   If database-failure rollback coverage is required, test `bulk_update_organizers()` at
   the repository boundary with a deterministic failing transaction; otherwise rely on
   the explicit rollback code plus the endpoint's prevalidation atomicity tests.
6. Add a small request helper in the integration test module only if it removes repeated
   payload/post boilerplate without hiding the assertions.

## Code to Keep

The following branch-added pieces are proportional to the feature and should not be
collapsed merely to reduce line count:

- the dedicated `/recipes/bulk-actions/organize` endpoint;
- UUID-based batch input and scoped organizer lookup;
- all-target permission validation before mutation;
- one-transaction relationship updates with rollback;
- changed-recipe responses and per-household update events;
- the shared quick-organize dialog for single and bulk modes;
- explicit recipe-card selection state and the native overlay link;
- cross-group, locked-recipe, cross-household, and event behavior coverage.

## Suggested Order

1. Correct documentation and remove the transform module.
2. Simplify dialog props, Select All invalidation, and card click handlers.
3. Collapse controller error handling.
4. Consolidate tests after production code settles.
5. Run focused tests, then the repository checks.

## Validation

```bash
cd frontend
yarn test:ci \
  app/components/Domain/Recipe/__tests__/recipe-card-organize.test.ts \
  app/components/Domain/Recipe/__tests__/recipe-card-section-selection.test.ts \
  app/components/Domain/Recipe/__tests__/recipe-quick-organize-dialog.test.ts
cd ..
uv run pytest tests/integration_tests/user_recipe_tests/test_recipe_bulk_action.py
task ui:check
task py:check
```

Manual smoke checks:

1. Open quick organization from desktop and mobile cards without navigating.
2. Edit organizers from a recipe page; cancel once and save once.
3. Select visible recipes, clear selection, and exit selection mode.
4. Select all filtered results, then change the query before the request completes.
5. Bulk add and bulk remove tags and categories.
6. Confirm public/external-group recipe browsing has no organization controls.

## Completion Criteria

- All current user-visible behavior remains unchanged.
- The custom workflow and unrelated historical plan files remain absent from the PR diff.
- No new abstraction is introduced solely to share a few lines between desktop and
  mobile cards.
- Branch-added production and test code is materially smaller and easier to trace.
- Focused tests and `task ui:check` / `task py:check` pass.
