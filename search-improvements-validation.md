# Recipe search validation

## Upstream PR validation

The upstream PR branch starts at `5edf45b0a` on `mealie-recipes/mealie:mealie-next`.
The search migration follows upstream revision `f3a1ae61d772`.
This branch contains no fork OAuth changes.

The SQLite suite passes 3,931 tests and skips 16 tests.
Six socket tests require a separate run outside the local sandbox.
That separate run passes all 51 tests in the HTTP transport and server modules.
The isolated PostgreSQL search, recipe repository, and backup suite passes 112 tests.
The frontend suite passes 783 tests in 71 files.
The production frontend build, code generators, ESLint, and frontend security checks pass.
Ruff passes for 787 files. Mypy passes for 494 source files.
Semgrep passes both authorization tests, all three XSS tests, and the source scan.

The benchmark results below retain the original fork baseline and reference host.
They do not measure this upstream revision.

## Environment and method

The worktree uses branch `feat/recipe-search-improvements` from commit `1a1ea23df58bf65b0b147b4a27f39bd5a2f01110`.
The original checkout remains separate.

Reference host: Apple M4, 10 CPUs, 24 GiB RAM, macOS 26.4, ARM64.
Python version: 3.14.4. Local SQLite version: 3.50.4.
PostgreSQL uses an isolated PostgreSQL 18 Docker container on localhost port 55432.
The production Python base image passes an FTS5 virtual-table creation probe with SQLite 3.46.1.
The probe uses the Dockerfile's pinned digest `sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170`.

`dev/scripts/benchmark_recipe_search.py` creates 10,000 recipes with eight ingredients per recipe.
The fixture includes common ingredients, overlapping title concepts, phrases, and partial matches.
The script obtains a bearer token through `/api/auth/token`.
It calls `/api/recipes` through FastAPI TestClient without dependency overrides.
Each request includes authorization, query validation, SQL queries, exact totals, schema conversion, and response serialization.
The timer excludes network transport, TLS, and browser behavior.

The warm test uses five concurrent clients and 100 requests per query, for 1,000 requests total.
One request per query warms the application before the concurrent test.
First requests do not represent a controlled cold-cache test.

## Final SQLite result

The final SQLite run meets the aggregate corpus target at 199.430 ms p95 and 131.196 ms median.
The run uses the default SQLite page cache and no concurrent benchmark or test jobs.
The result has 0.570 ms of margin against the 200 ms target. It does not establish performance headroom.
Broad search measures 213.879 ms p95 for its own query group.
The agreed target applies to the complete query corpus. The broad-search group exceeds 200 ms.

| Query | Mode | p95 ms |
|---|---|---:|
| `pork lettuce wrap` | all | 176.850 |
| `"lettuce cups" pork` | all | 166.275 |
| `+pork lettuce wrap` | all | 170.046 |
| `pork -cilantro` | all | 34.669 |
| `pork -"chili peppers"` | all | 35.358 |
| `salt` | all | 191.374 |
| `chi` | all | 187.865 |
| `lettce` | all | 119.975 |
| `pork lettuce wrap` | any | 213.879 |
| `-cilantro` | all | 30.738 |

The final corpus uses `lettce` to exercise successful one-edit typo correction.
The initial corpus uses `lettcue`, which needs two Levenshtein edits and returns no result.
Other queries remain identical across the runs.

The final rebuild takes 1.793 seconds. Search storage occupies 59,826,176 bytes, including primary-key indexes.
Repeated rebuilds and index-page allocation affect the storage result.
Source-update and commit cost measures 0.885 ms median and 3.727 ms p95 across 20 transactions.

The original code on the same fixture measures 71.803 ms p95 and 59.134 ms median in an idle run.
The new search trades more server work for precise search rules and rank.
The synthetic `pork lettuce wrap` query returns 4,001 recipes with the original code and 1,001 recipes with the new code.
The focused regression fixture returns only the intended recipe.
Original-code timings do not imply support for the new operators; the original code ignores their new semantics.

Persistent summary artifacts:

- `dev/reports/recipe-search/sqlite-final.json`
- `dev/reports/recipe-search/sqlite-original.json`

The artifacts include each query group, first requests, fixture details, runtime details, and aggregate results.
The benchmark script can reproduce raw per-request samples.

## Final PostgreSQL result

PostgreSQL 18.6 meets the target at 84.824 ms p95 and 61.379 ms median across 1,000 requests.
The run has no concurrent benchmark or test jobs.
Each query group measures below 99 ms p95.

| Query | Mode | p95 ms |
|---|---|---:|
| `pork lettuce wrap` | all | 97.328 |
| `"lettuce cups" pork` | all | 91.224 |
| `+pork lettuce wrap` | all | 83.559 |
| `pork -cilantro` | all | 39.419 |
| `pork -"chili peppers"` | all | 38.474 |
| `salt` | all | 64.621 |
| `chi` | all | 59.897 |
| `lettce` | all | 91.807 |
| `pork lettuce wrap` | any | 98.288 |
| `-cilantro` | all | 43.767 |

The rebuild takes 7.033 seconds. Search tables and indexes occupy 91,160,576 bytes.
Source-update and commit cost measures 1.942 ms median and 2.741 ms p95 across 20 transactions.
`dev/reports/recipe-search/postgresql-final.json` preserves the summary evidence.
The original PostgreSQL implementation measures 346.827 ms p95 and 206.621 ms median on the same fixture.
`dev/reports/recipe-search/postgresql-original.json` preserves that baseline.
Both baseline runs use original revision `1a1ea23df58bf65b0b147b4a27f39bd5a2f01110` and the final query corpus.

Reproduce SQLite with a dedicated data directory:

```sh
DATA_DIR=/private/tmp/mealie-search-bench-sqlite PRODUCTION=true \
  UV_CACHE_DIR=/private/tmp/mealie-uv-cache \
  uv run --frozen python dev/scripts/benchmark_recipe_search.py \
  --repeats 100 --output /private/tmp/mealie-search-bench-sqlite-final.json
```

For PostgreSQL, create a dedicated benchmark database first.
Set `DB_ENGINE=postgres` and the `POSTGRES_*` connection variables.
The database name must contain `bench`. The data-directory path must contain `search-bench`.
Run the same script and arguments with a PostgreSQL output path.

## Stress test at 100,000 recipes

The stress test uses a separate database, eight ingredients per recipe, five clients, and 100 requests.
This test does not use the 10,000-recipe release limit as an acceptance gate.
The JSON artifacts retain the script's 200 ms comparison field for reference.

SQLite measures 1,671.934 ms p95 and 1,202.049 ms median.
The strong `pork lettuce wrap` query group measures 1,360.864 ms p95.
The broad query group measures 1,714.933 ms p95.
Fixture creation takes 109.327 seconds. Rebuild takes 25.613 seconds.
Search storage occupies 451,555,328 bytes.
Source-update and commit cost measures 1.228 ms median and 44.341 ms p95 across 20 transactions.
`dev/reports/recipe-search/sqlite-stress.json` preserves the evidence.

PostgreSQL measures 5,297.501 ms p95 and 883.100 ms median.
The strong `pork lettuce wrap` query group measures 5,699.199 ms p95.
The broad query group measures 5,513.547 ms p95.
Fixture creation takes 134.165 seconds. Rebuild takes 74.281 seconds.
Search storage occupies 874,971,136 bytes.
Source-update and commit cost measures 1.686 ms median and 2.280 ms p95 across 20 transactions.
`dev/reports/recipe-search/postgresql-stress.json` preserves the evidence.
Both stress runs finish within their five-minute wall-clock caps.
These results show substantial latency at 100,000 recipes. They do not support a 200 ms claim above 10,000 recipes.

## Initial performance result

The first complete SQLite run fails the agreed 200 ms p95 limit.
The aggregate p95 measures 579.883 ms. The median measures 365.185 ms.
Concurrent backend tests and a PostgreSQL benchmark share the host during this run.
This contention does not justify acceptance of the failed result.

| Query | Mode | p95 ms |
|---|---|---:|
| `pork lettuce wrap` | all | 680.560 |
| `"lettuce cups" pork` | all | 473.123 |
| `+pork lettuce wrap` | all | 630.049 |
| `pork -cilantro` | all | 124.168 |
| `pork -"chili peppers"` | all | 115.405 |
| `salt` | all | 593.174 |
| `chi` | all | 566.956 |
| `lettcue` | all | 129.039 |
| `pork lettuce wrap` | any | 658.263 |
| `-cilantro` | all | 100.229 |

SQLite rebuild takes 1.662 seconds.
Twenty recipe source-update transactions measure 0.937 ms median and 6.488 ms p95.
Search tables and indexes occupy 47,075,328 bytes, including primary-key indexes.
This source-update measurement includes transaction commit and trigger cost. It does not measure full recipe-save endpoint overhead.

A separate single-client profile measures these complete request times:

| Query | Complete request ms | SQL execution ms |
|---|---:|---:|
| `salt` | 141.627 | 123.337 |
| `chi` | 141.597 | 121.627 |
| `pork lettuce wrap`, broad | 151.456 | 122.540 |

The profile identifies repeated visible-ID scans, duplicate count/rank work, and a cast on the recipe primary-key join.
These costs require adapter changes and a fresh benchmark process.

The final adapter shares visible IDs, combines FTS alternatives, and computes rank features with one aggregate.
It computes exact totals over narrow rank rows and limits a thin page before full recipe hydration.
These changes preserve all candidates and the exact count.

## Test evidence

The final full SQLite test suite passes 3,928 tests and skips 16 tests in 95.09 seconds.
The skips cover nine LDAP cases, six manual API parser cases, and one long scraper case.
The latest focused SQLite run passes 188 tests after the plural-rule fixes.
The final PostgreSQL search, repository, pagination, and backup suite passes 198 tests in 30.80 seconds.
Frontend security checks and ESLint pass. The full frontend suite passes 782 tests in 71 files after code generation.
An explicit Vue TypeScript check exits with code 2 on both the feature worktree and the original revision.
Both runs report 303 TypeScript diagnostics with vue-tsc 3.3.14 and TypeScript 5.9.3.
The normalized file-and-message comparison finds zero new diagnostics and zero resolved diagnostics.
The project-wide TypeScript check does not pass. The feature introduces no additional diagnostics under that check.
`dev/reports/recipe-search/typescript-comparison.json` preserves the comparison.
Ruff checks pass. The format check covers 795 files. Mypy passes for 501 source files.
Semgrep rule tests pass: two authorization cases and three XSS cases.
The final Semgrep source scan runs five rules on all 501 Python source files and reports zero findings.
The scan uses `--no-git-ignore` and includes the eight new source files.
Both adapters meet the aggregate performance target on the reference host.

## Independent review findings

- Historical migrations import the fixed version-1 helpers.
- Search projections use full source text rather than the existing 255-character normalized columns.
- Both normalizers fold Greek final sigma consistently.
- Phrase matches stay inside one source segment.
- Cookbook and query filters constrain typo vocabulary.
- Backups exclude derived search tables and SQLite FTS shadow tables.
- Restore rebuilds derived search indexes.
- Source triggers avoid complete ingredient rescans on recipe inserts and metadata updates.
- The native recipe primary-key join supports indexed result retrieval.
- Alembic autogeneration excludes derived search tables.
- Bounded plural alternatives cover tomatoes, potatoes, cookies, chilies, berries, tacos, peas, eggs, and dishes.

Tests cover these review fixes. The test evidence section records the final results.

## Coverage and remaining evidence

| Spec task | Evidence | Status |
|---|---|---|
| 1. Worktree and spec | Dedicated branch, worktree, and `search-improvements.md` | Complete |
| 2. Baseline and runtime | Original-code baselines on both databases; reproducible benchmark; local and production-base FTS5 probes | Complete |
| 3. Parser and policy | Independent parser contract tests | Tests pass |
| 4. Storage lifecycle | SQLite and PostgreSQL lifecycle, rebuild, downgrade, backup tests | Complete |
| 5. Retrieval and API | Repository, endpoint, vocabulary-filter tests; generated response type; query-plan review | Complete |
| 6. Interfaces | Controls, URL and stale-response tests; 782 frontend tests; security checks; ESLint; explicit TypeScript comparison | Complete; project-wide TypeScript check has the same 303 baseline diagnostics |
| 7. Acceptance | Query plans; complete-suite checks; both database benchmarks and 100,000-recipe stress reports | Complete for the stated 10,000-recipe corpus target; documented scale and cache limits apply |

## First-request and deployment limits

A controlled OS cold-cache test does not form part of these results.
The first-request samples show a new process after fixture initialization and rebuild, with OS caches intact.
The first `pork lettuce wrap` request measures 134.288 ms on SQLite and 184.593 ms on PostgreSQL.
These samples include first search-query compilation. They exclude process startup and fixture preparation.
No production deployment or live recipe change forms part of this work.
