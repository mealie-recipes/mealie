# Workflow 1 — Single high-level instruction (baseline)

This note records one workflow only. It is written so the same measures can be filled in for the other workflows and compared. It is the “Workflows and Evaluation” entry for the baseline in the COMPX574 report, not the whole report.

**Workflow name.** Single high-level instruction to finish the rewrite, with almost no review between steps.

**Tool.** Cursor agent mode, one session. No sub-agents were launched for this run. No second coding tool was used.

**Rewrite under test.** Re-implement the Mealie FastAPI backend in PHP (Laravel), in a new `php-w1/` directory, leaving the Python backend in place. Same `/api` paths, camelCase JSON, and the existing SQLite database at `dev/data/mealie.db`.

## 1. What the workflow actually was

The assignment’s first illustrative workflow is “a single high-level instruction to convert the whole project, as a baseline.” That is this run.

Decomposition was not done by a person. After a short setup (scaffold, then a request for a completion estimate and a plan), the instruction that defines this workflow was:

> 尽可能少的让我干预.你直接完成剩下的所有工作吧

Later messages did not add requirements. They only restarted the same instruction after the agent stopped or the session was compacted: “请继续”, “继续开工”, “不要停下来.直到全部做完”, “继续.直到结束不要停止”, “那么继续做”.

Context given to the agent:

- The repository itself, including `AGENTS.md` / `CLAUDE.md`, which describe the Python repository-service-controller layout, `uv`, and the rule against editing generated TypeScript.
- The live SQLite file and the Python route modules, which the agent read on its own while implementing.
- No separate migration plan was accepted and then executed stage by stage. A plan had been requested one minute earlier, but the next instruction discarded staged review.
- No persistent progress file was maintained for this workflow. Decisions lived in the chat transcript. When the context window was compacted, a generated summary was the only carry-over.

Verification used by the agent, not by a person:

- `vendor/bin/pint --dirty` and `php artisan test` after each batch.
- Tests were written in the same session, against the PHP app, using the shared database inside a transaction that was rolled back.
- The Python pytest suite was not run. Responses were not diffed against the Python server on port 9000.

## 2. Measures (use these columns for the other workflows)

| Measure | Definition used here | Result for workflow 1 |
|---|---|---|
| Surface completion | PHP routes registered in `php-w1/routes/api.php`, divided by `@router.get/post/put/patch/delete` decorators under `mealie/routes/` | **226 / 236 (96%)** |
| Behaviour completion | Share of those routes whose behaviour matches the Python handler, not merely the path | **Not 96%.** See the gap list below. A fair reading is that everyday CRUD is largely present, and integrations are partial or absent. |
| Accuracy | Same database, same JWT, GET the path Python actually serves, compare status and JSON | **11 / 40 (28%)** exact. 9 status mismatches, 20 body mismatches. One route excluded because its body is an unordered sample. |
| Test result | `php artisan test` at the end of the run | **17 passed, 77 assertions, 0 failed.** 15 of the 17 tests are Mealie tests (`HealthTest` + 14 in `ApiTest`). Two are the Laravel examples created with the project. |
| Time | Wall clock from the “do the rest, don’t make me intervene” prompt to the last implementation turn | **About 51 minutes** (20:33–21:24, 1 Oct 2026, Pacific/Auckland). |
| Human effort during the run | Prompts that reviewed code or chose a design | **None.** Five prompts only said “continue”. |
| Token usage / cost | Whatever the tool reported | **Not recorded.** Cursor did not give a token or dollar figure in the transcript. Do not invent one. |

### Surface completion

Counted on 1 Oct 2026 after the run:

- Python: 236 route decorators across 52 files in `mealie/routes/`.
- PHP: 226 `Route::get|post|put|patch|delete` entries in `php-w1/routes/api.php`.

226/236 counts paths, not behaviour. Several PHP routes exist so the Nuxt client does not 404, and then return a fixed error or a reduced result.

### Behaviour completion

Present and exercised by a PHPUnit test that hits the HTTP layer: health and database driver, public `/api/app/about` camelCase, login rejection, a signed JWT reading the current user plus recipes, categories, and shopping lists, a missing image 404, shopping-item create/check/delete, meal-plan rules, cookbook create, share-token create and public read, recipe image upload to WebP, AI provider settings, today’s meal plan and suggestions, explore 404, food seeding, notifier create, microdata HTML import, and a one-recipe JSON archive import. Writes in those tests are rolled back.

Present in code, with weaker or no parity check:

- Recipe, shopping-list, meal-plan, organiser, comment, label, cookbook, webhook, and admin-user CRUD.
- Password reset tokens stored in `password_reset_tokens`.
- Group and household preferences and member lists.
- Backup zip containing `mealie.db` and `database.json`, plus a restore that rewrites tables from `database.json`.

Partial or explicitly not the Python behaviour:

- Page scrape accepts JSON-LD and schema.org microdata only. Python uses `recipe-scrapers` and per-site parsers.
- AI recipe creation calls the saved OpenAI-compatible provider when one exists. There is no transcription, image input, or organiser creation. The final test only covers an empty prompt, which returns an SSE `error` event.
- Email is sent only when `SMTP_ENABLE` is true. The test covers the disabled case (`success: false`).
- Notifier test posts to `http`/`https` URLs only. Apprise URL schemes are not implemented.
- Archive migration imports recipe JSON, and Chowdown-style Markdown with a `title:` front matter. Paprika, Tandoor, RecipeKeeper, CopyMeThat, Plan to Eat, Cook’n, and Mealie alpha are not implemented. Nextcloud images are not copied.
- OIDC routes return 404, “OIDC is not configured”.
- Maintenance “clean” routes return “Nothing to clean” and do not delete files.
- Cookbook and meal-plan rule responses set `queryFilter` to an empty object. Python builds a real query-filter tree.
- Suggestions are a short list of recipes, not the missing-foods query.
- Ingredient parsing is a leading-number split, not the NLP parser.
- A zip that contains only `mealie.db` and no `database.json` is refused. Python’s restore drops and reloads the schema through Alembic.
- No scheduler, no task queue, no per-site scraper modules.

### Accuracy

Measured after the run by `compx574/accuracy_compare.py`. Python was already serving port 9000. PHP was started on port 9001. Both read `dev/data/mealie.db`. A one-hour JWT was minted with the PHP signer and accepted by Python, so the secret matches. The script sends GET only. Datetime strings are compared without fractional seconds, and `9000` / `9001` in URLs are ignored. On `/api/app/about` and group storage, version, token lifetime, OIDC name, iframe hosts, and the storage quota are ignored because those come from each process’s settings (`version` is `develop` vs `php`, `tokenTime` is 256 vs 48, quota is 500 MB vs 0). `/api/recipes/suggestions` is excluded: both return 200, and the body is a different sample each call.

41 routes were requested. 40 are scored.

| Result | Count | Routes |
|---|---|---|
| Exact match | 11 | `/api/app/about`, validator for an unused username, own ratings, own favorites, group preferences, group reports, household self, household preferences, household statistics, today’s meal plan, invitations (both 403) |
| Status differs | 9 | Startup info and theme are under `/api/app/about/…` in Python and 404 in PHP. Categories, tags, and tools are under `/api/organizers/…` in Python and 404 in PHP. OIDC is 500 in Python and 404 in PHP. `GET /api/users/api-tokens` is 405 in Python (it only has POST and DELETE) and 200 in PHP. AI settings and household members are 403 in Python, because that user may not manage the group, and 200 in PHP. |
| Body differs | 20 | See the groups below. |
| Excluded | 1 | Suggestions. |

The 20 body mismatches fall into a few repeated causes:

- Pagination keys. Python’s `PaginationBase` is a plain Pydantic model, so the JSON uses `per_page` and `total_pages`. PHP emits `perPage` and `totalPages`. This is the first difference on members, cookbooks, meal plans, rules, webhooks, notifications, recipe actions, comments, and recipes. The comparer stops after six differences, so those routes may also differ inside `items`.
- Thin objects. Shopping items omit food aliases and build `display` from the note only (`test` vs Python’s `1 bunch baking powder test`). Shopping lists return no label settings (0 vs 32) and inline `listItems`, which the list route in Python does not. Timeline subjects stay as translation keys (`recipe.recipe-created` vs `Recipe Created`).
- Sort order. Page 1 of units and labels is a different set of rows (`stalk` vs `can`, `Desserts & Sweet Snacks` vs `Beverages`), so the default order is not the same.
- Shape. `GET /api/shared/recipes` is a JSON array in Python and a pagination object in PHP. `authMethod` is `Mealie` vs `MEALIE`. Group self omits `aiProviderSettings`. Household list items omit `preferences` and add `group`.

11/40 is the strict score. It is the number to put next to the other workflows. It is not “28% of the backend”: writes, scrapers, mail, backup restore, and OIDC were not in this pass.

The PHPUnit run (17 passed) does not measure this. Causes:

- The agent wrote the test and the implementation in the same turn. A test that asserts `assertJsonPath('name', 'PHP Cookbook')` passes if the PHP code returns that field. It does not show that Python’s `ReadCookBook` would return the same object.
- Tests use `MEALIE_SECRET=test-secret` from `php-w1/phpunit.xml`. They do not show that a token issued by the Python dev server is accepted by PHP, although the dev secret path was aligned earlier in the session.
- No response was captured from port 9000 and compared field by field.
- The agent reported “done” more than once while routes still returned stubs. The last user-visible status, before this report, still listed OIDC, the scheduler, and site scrapers as open. That is the premature-completion failure the assignment asks about.

What the tests do show: the PHP process boots, reads the real Mealie SQLite file, rolls back writes, and the paths above return the status codes the new tests expect. Final command: `php artisan test` → 17 passed, 77 assertions, about 1.2 s.

### Time

| Clock (NZST, 1 Oct 2026) | Prompt | Role in this workflow |
|---|---|---|
| 20:24 | “如果把整个后端 rewrite 成 php” | Before this workflow. Scoping question. |
| 20:27 | “先搭 php 的骨架” | Before this workflow. Scaffold. |
| 20:32 | “目前完成度多少?给个 plan” | Before this workflow. Asked for a plan. |
| **20:33** | **“尽可能少的让我干预.你直接完成剩下的所有工作吧”** | **Start.** |
| 20:42 | “请继续” | Restart. No new requirements. |
| 20:46 | “继续开工” / “不要停下来.直到全部做完” | Restart, including after context compaction. |
| 20:55 | “继续.直到结束不要停止” | Restart. |
| 21:21 | “那么继续做” | Restart. Last implementation turn. |
| 21:24 | Question about which workflow this was | End. No further code in this workflow. |

Wall-clock time inside the workflow is about **51 minutes**. Active human time is the time to type five continuation lines. There was no review pause.

Token usage and dollar cost were not reported by the tool. For the comparison table, record “not available” rather than estimating.

## 3. What happened, and why

The run produced a large Laravel tree quickly: controllers, services, and 226 routes, with a green but narrow test suite. It did not produce a backend that can replace Python.

The speed has a mechanical cause. The instruction forbade stopping for review, and the acceptance check was a test suite the agent could extend. Each batch could add a route, add a test that called that route, and report progress. Route count and “tests passed” both went up (the suite grew from the early health test to 17 tests) without anyone checking a Python response.

The accuracy gap has the same cause. Nothing in the loop compared outputs to `mealie/routes/`. The agent read Python files when it needed a column name or a JSON key, then moved on. Where the Python behaviour depended on a library that is not a few dozen lines (recipe-scrapers, Apprise, the OIDC dance, Alembic restore, the scheduler), the agent kept the route and returned a short error or a reduced body. That satisfies “do not 404” and a self-written test. It does not satisfy behavioural parity. The agent also said the work was finished often enough that the user had to repeat “do not stop”.

Context loss showed up once. The session was compacted around 20:46. The continuation prompt was only “不要停下来”. The agent resumed from a summary, not from a document of decisions. That is tolerable here because the summary was detailed. It is the failure mode a later workflow (a maintained context file, or a reviewed plan) is meant to isolate.

Tests were not weakened by deleting assertions. They were narrowed at birth. Write tests use a transaction and `rollBack()`, so they never leave `mealie.db` dirty. That is a sound safety choice. It also means the suite never checks commit behaviour, migrations, or restore.

One live side effect almost escaped the suite. An earlier draft of the AI test posted the prompt “soup” while a provider existed in the database. The provider was called, a recipe slug came back, and the surrounding transaction rolled the row back. The assertion was then changed to an empty body so the test would not call the network. The incident is small. It shows that a self-written test on a shared database can hit real external services if the assertion is aimed at the success path.

## 4. What to change if this workflow is run again

Keep it as the baseline. Do not use it as the only workflow. If it is repeated:

- Freeze the test file, or generate expected JSON by calling the Python server, before the agent writes more PHP. Otherwise “tests passed” is not an accuracy measure.
- Count behaviour gaps in a fixed checklist (scrape, OIDC, mail, backup restore, scheduler) instead of counting routes.
- Ask the tool for token usage at the start and the end. This run cannot be compared on cost.

## 5. Evidence

- Transcript: Cursor agent transcript `8d881b98-784a-45be-99ac-14cd03c7dab1`. User timestamps above are from that log.
- Code: `php-w1/routes/api.php` (226 routes), `php-w1/tests/Feature/ApiTest.php` (14 tests), `php-w1/tests/Feature/HealthTest.php`.
- Last test command, from `php-w1/`: `php artisan test` → 17 passed, 77 assertions, 1153 ms.
- Accuracy command, from the repo root, with Python on port 9000 and PHP on port 9001: `uv run python compx574/accuracy_compare.py` → `accuracy=11/40`.
- Route counts, from the repo root: `rg -c '@router\.(get|post|put|patch|delete)\(' mealie/routes` summed to 236; `rg -c 'Route::(get|post|put|patch|delete)' php-w1/routes/api.php` returned 226.
- This run was not committed. The assignment asks for commits whose messages name the workflow. That evidence is missing for workflow 1 and should be stated as a gap in the log, not back-filled.
