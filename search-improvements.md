# Recipe search improvements

## Goal

Make recipe search precise, predictable, and fast for libraries of 10,000 recipes.

Perform all work on branch `feat/recipe-search-improvements` in `/private/tmp/mealie-search-improvements`.
Preserve the original checkout and its local changes.

## Search contract

| Query | Result |
|---|---|
| `pork lettuce wrap` | Require all concepts; treat lettuce wraps and lettuce cups as equivalent |
| `"lettuce cups" pork` | Require the literal phrase and the pork concept |
| `+pork lettuce wrap` | Require the literal word `pork`, including in broad mode |
| `pork -cilantro` | Exclude literal mentions of cilantro |
| `pork -"chili peppers"` | Exclude the literal phrase |

- Normalize case, accents, punctuation, and whitespace.
- Search titles, descriptions, ingredient text, and structured ingredient food names.
- Match literal words at word boundaries. Match phrases within one field or ingredient.
- Apply culinary synonyms, plural variants, and conservative typo correction only to ordinary terms.
- Match the longest culinary phrase first. Never equate generic `cup` and `wrap`.
- Support prefix lookup for a single ordinary term.
- Broad mode accepts any ordinary concept. It retains quoted phrases, literal requirements, and exclusions.
- Support double quotes and leading ASCII `+` and `-`. Keep internal hyphens and apostrophes as ordinary text.
- Reject unmatched quotes and empty signed expressions with a clear validation error.
- Allow exclusion-only queries against the normal recipe list.
- Rank complete coverage, exact title phrase, title coverage, description coverage, then ingredient coverage.
- Prefer literal matches over expansions. Use existing sort preferences and recipe ID as tie breakers.
- Preserve response shapes, exact totals, permissions, and recipe filters.
- Exclusions describe recorded text. They do not guarantee ingredient absence.

## Architecture

- Separate the typed parser, search policy, and database adapter.
- Keep recipe-search policy outside response schemas.
- Use SQLite FTS5 and PostgreSQL full-text indexes behind one behavior contract.
- Use application-normalized tokens without database-specific stemming or stop-word removal.
- Maintain searchable segments in the same transaction as source changes.
- Preserve field and ingredient boundaries.
- Use shared rank features rather than database-native relevance scores.
- Use RapidFuzz only for unmatched ordinary words with at least five characters.
- Allow one Levenshtein edit. Reject ambiguous corrections.
- Restrict typo vocabulary to visible recipe titles and plausible word lengths.
- Limit input to 512 characters, 32 clauses, and four alternatives per ordinary concept.
- Reject excessive input explicitly.
- Keep counts, rank, and pagination consistent. Do not truncate candidates before final rank.
- Do not load full recipe collections into Python.
- Require no external search service or AI provider.

## Performance contract

Target warm server-response p95 at or below 200 ms with five concurrent clients and 10,000 recipes.
Document the reference hardware, database versions, cache state, query corpus, and concurrency.
Include authorization, match, count, rank, hydration, and serialization in the measurement.
Measure cold requests, index size, backfill duration, and recipe-save overhead separately.
Use 100,000 recipes as a stress test, not a release target.
Treat the latency limit as an acceptance target, not a measured result.

## Tasks

### 1. Worktree and specification

- Create the dedicated branch and worktree from committed `mealie-next`.
- Save this specification as `search-improvements.md` at the worktree root.
- Recheck the clean worktree against the plan before any prerequisite port.

Acceptance: The worktree has its own branch and specification. The original checkout remains unchanged.

### 2. Baselines and runtime support

- Record current result quality and endpoint latency on both databases.
- Create a reproducible 10,000-recipe fixture with realistic ingredients and text lengths.
- Record hardware, software versions, cache state, query corpus, and concurrency.
- Verify FTS5 support in supported SQLite runtimes and production images.

Acceptance: Baselines reproduce reliably. Supported runtimes provide the required index capability.

### 3. Parser and search policy

- Add ordinary, required-literal, phrase, and excluded clause types.
- Implement normalization, syntax validation, limits, and broad-mode rules.
- Add lettuce-wrap and lettuce-cup equivalents.
- Implement conservative typo expansion and the shared rank contract.
- Add database-independent tests for syntax, contradictions, boundaries, expansions, and errors.

Acceptance: Tests cover each search rule without dependence on a database adapter.

### 4. Search storage and lifecycle

- Add searchable segments, indexes, and title vocabulary for both databases.
- Add Alembic migrations and existing-data backfill.
- Update search data after recipe create, import, edit, delete, and structured food-name changes.
- Include bulk operations and a rebuild command.
- Test rollback and index consistency.
- Keep searchable segments private. Enforce visibility through authoritative recipe records.

Acceptance: Both databases produce equivalent current search documents. Rebuild restores results without recipe changes.

### 5. Retrieval and API

- Compile parsed queries into safe backend expressions.
- Apply tenant, household, cookbook, public visibility, and existing filters before result selection.
- Apply the same visibility constraints to typo vocabulary.
- Implement shared rank, exact counts, and stable pagination.
- Add `searchMode=all|any`, default `all`, to authenticated and public recipe-list endpoints.
- Replace recipe-specific legacy search. Leave other entity searches unchanged.
- Run `mise run dev:generate` after schema changes.

Acceptance: Both adapters pass one behavior suite. Broad mode retains explicit requirements and exclusions.

### 6. Interfaces

- Update the recipe explorer and search dialog.
- Add syntax help, Broaden Search, and Show Strong Matches controls.
- Reset mode and pagination when query text changes.
- Preserve mode in explorer URLs. Encode literal `+` correctly.
- Retain debounce behavior. Prevent stale responses from replacing current results.
- Show clear syntax errors.
- Modify only `en-US` translation strings.

Acceptance: Both interfaces produce equivalent queries and preserve explicit syntax across URL round trips.

### 7. Validation and release notes

- Add the supplied Sesame-Lime Lettuce Cups recipe and pork-only, chicken-cup, and unrelated-wrap distractors.
- Require the supplied recipe first for `pork lettuce wrap`. Exclude distractors in strong mode.
- Test literals, prefixes, plurals, synonyms, typo ambiguity, exclusions, and SQL wildcard characters.
- Test visibility, totals, stable pages, food renames, imports, deletion, and rebuild.
- Benchmark common terms, short prefixes, phrases, broad mode, exclusions, and exclusion-only queries.
- Inspect query plans for selective positive searches.
- Meet the latency target without candidate truncation or weaker permission checks.
- Run focused tests, `mise run py:check`, and `mise run ui:check`.
- Document syntax, compatibility changes, benchmark results, and release notes.

Acceptance: Both databases pass correctness tests. The benchmark report demonstrates the performance target.

## Plan coverage

| Requirement | Tasks |
|---|---|
| Dedicated worktree | 1 |
| Concepts and culinary equivalents | 3, 5, 7 |
| Quotes, required terms, exclusions | 3, 6, 7 |
| Database-independent semantics | 3, 5, 7 |
| SQLite and PostgreSQL indexes | 2, 4, 5 |
| Migration, backfill, updates, rebuild | 4, 7 |
| Explicit broad mode | 3, 5, 6 |
| Tenant and public visibility | 4, 5, 7 |
| Stable pages and exact totals | 5, 7 |
| Performance at 10,000 recipes | 2, 7 |
| Generated types and English-only translations | 5, 6 |

Track implementation evidence and open validation gaps in `search-improvements-validation.md`.

## Implementation status

Tasks 1 through 7 are complete in the dedicated worktree.
The [validation report](search-improvements-validation.md) records the final tests, query plans, benchmarks, and limits.
The `dev/reports/recipe-search/` directory contains persistent result summaries for both databases and both collection sizes.
The 10,000-recipe corpus meets the aggregate p95 target on the reference host.
SQLite has little margin and exceeds 200 ms for the broad-search query group.
The 100,000-recipe stress results do not meet that target and do not form a release gate.
No production deployment or live recipe change forms part of this work.
