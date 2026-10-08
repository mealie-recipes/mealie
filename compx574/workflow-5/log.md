# Workflow 5 — Multi-agent (Claude Code orchestrator + parallel sub-agents)

Evidence log for workflow 5. Times are NZDT. Everything below is written while the work happens; nothing is back-filled unless marked.

## Setup

| Item | Value |
|---|---|
| Tool | Claude Code (CLI), model Claude Opus 5.5 (`claude-opus-5-5`) as orchestrator and sub-agents |
| Operator | Derek. Derek delegated the review gates to the orchestrator ("按照你认为合适的去完成 并记录就行"), so gates below were run by the orchestrator, not a human. See "Deviations". |
| Branch | `w5-multi-agent`, from `bbd56a53e` (`add all url into hurl`) on `xiaofang2016/mealie` `mealie-next-backend-rewrite` |
| Working copy | git worktree at `.worktrees/w5` with sparse checkout excluding `php-w1/` and `compx574/workflow-1-single-instruction.md`, so agents cannot read W1 by accident (`git show` could still reach it; the prompt forbids it) |
| Python oracle | Fork's own Python code (not upstream `mealie-next`), run from the worktree inside the VS Code dev container, `PRODUCTION=False uv run python mealie/app.py`, port 9000. Dev mode means JWT secret `shh-secret-test-key` and the debug 422 body `{"status_code":422,"message":...,"data":null}` |
| Database | Copy of Derek's local `dev/data` (alembic `3527efeeec34`, same revision as the fork base) at `.worktrees/w5/dev/data`. **Not** the DB the shared `parity.hurl` IDs were taken from — see "Scoring caveats" |
| PHP sandbox | Container `mealie-w5-php` from `sandbox/Dockerfile` (PHP 8.4.26, Composer 2.10.3, Hurl 8.0.1). Shares the dev container's network namespace. No git credentials, SSH keys or registry tokens are mounted. The orchestrator itself runs on the host with Derek's git config, so it is not fully sandboxed |
| Framework | Laravel 13 (same major as W1's `composer.json`), PHP ^8.3 |

## Workflow as specified by the group (transcribed from the group chat, Monday)

Phase A prompt (split only, no business code):

> 把 Mealie 的 FastAPI 后端（mealie/）用 PHP 重写到新目录 php-w5。Python 后端留在原地。使用相同的 /api 路径，以及已有的 SQLite 数据库 dev/data/mealie.db。不要对这个数据库运行 php artisan migrate。不要修改 frontend/app/lib/api/types/，也不要修改 en-US 以外的语言文件。不要打印密钥。Python 继续跑在 http://127.0.0.1:9000。这个 PHP 应用跑在 http://127.0.0.1:9001。只有本提示明确要求时才提交，提交说明以 workflow-5: 开头。
> 不要读取或复制 php-w1/。不要读取 compx574/workflow-1-single-instruction.md。
> 这是 workflow 5。稍后使用并行子代理。这一轮不要实现 API 行为。
> 把分工写到 compx574/workflow-5-split.md。后端分成下面四个区域，mealie/routes/ 下除 spa 以外的每个 Python 包都要分进去：
> 1. auth、users、app、validators
> 2. recipe、organizers、unit_and_foods、comments、parser
> 3. households、media、shared
> 4. groups、admin、explore
> 每个区域写明：对应的 Python 文件、该区域可以创建的 PHP 文件、任何区域都不能改的文件。每个区域只能把路由写在自己的文件 routes/<area>.php 里。任何区域都不能改其他区域的文件，也不能改 mealie/、frontend/ 或 tests/。
> spa 不在本次范围内。其他不准备实现的内容写在「不在范围内」。写完分工后停止。

Gate A: human checks the split boundaries.

Phase B prompt:

> 分工已通过。按区域各启动一个子代理，并行执行。不要自己实现这些区域。
> 每个子代理只拿到 compx574/workflow-5-split.md 里自己的区域，以及这些规则：只改分配给该区域的 PHP 文件；每个 HTTP 方法和完整路径都从分配到的 Python router 抄写；Python 后端留在原地。
> 写路由代码之前，每个子代理往 compx574/workflow-5-contracts.md 追加一节。它准备实现的每个接口都要写：方法和完整路径及其 Python 来源；JSON 字段名所用的 schema 文件；id 如何存储、如何返回；谁可以调用，依据是哪段 Python 权限检查；不实现什么。
> 子代理返回后，不要消除差异。把冲突写到 compx574/workflow-5-merge.md，只列这些：重复的辅助代码、不同的 JSON 键风格、不同的路由前缀、不同的 id 格式、不同的权限规则。提交，说明以 workflow-5: 开头。然后停止。

Gate B: human reviews only `workflow-5-contracts.md` and the five conflict types in `workflow-5-merge.md`, marks fixes.

Phase C prompt:

> 只处理我在下面标出的冲突。不要新增接口，也不要重开没有冲突的区域。
> <贴上标好的冲突表>
> 把改动补进 compx574/workflow-5-merge.md。提交，说明以 workflow-5: 开头。然后停止。

## Deviations from the group's W5 text, and why

Decided by the orchestrator after reading `run.sh`, `parity.hurl` and the Python auth code (see conversation notes, 2026-10-08 ~01:30–02:10).

| # | Change | Reason |
|---|---|---|
| D1 | **Phase 0 added**: orchestrator builds a shared skeleton before the split is executed — Laravel app, `mealie` DB connection, `App\Auth\Jwt::encode()/secret()`, auth middleware, id/date/JSON/error/pagination helpers, `routes/api.php` that loads each `routes/<area>.php`. Sub-agents may use but not edit it. | `run.sh` requires `App\Auth\Jwt::encode/secret` and a `mealie` connection; the group prompt never says so. Without an owner for shared files, four parallel agents would each scaffold Laravel in the same directory. |
| D2 | **Contracts in one file per area** (`workflow-5-contracts/area-N.md`), concatenated into `workflow-5-contracts.md` afterwards. | Four agents appending to one file at the same time race each other. |
| D3 | **`compx574/hurl/` is held out**: sub-agents are told not to read or run it. They verify by sending the same request to Python :9000 and to their own PHP server and comparing status and body. Orchestrator runs `run.sh` only at phase boundaries. | `parity.hurl` asserts status codes only. An agent that can see it can pass it with status-only stubs. Holding it out keeps it an acceptance test. |
| D4 | **One port per sub-agent** (9011–9014), :9001 kept for scoring. | Group rule allows one PHP on :9001 at a time; parallel agents each need a server. |
| D5 | Added W3's rule: **do not register a route that only returns a fixed error and count it as done.** | Same reason as D3. Keeps W3 and W5 instructions aligned. |
| D6 | **Floor score**: run `run.sh` on the Phase 0 skeleton (no area routes) before any area work. | To report how much of the score comes from the skeleton alone. |
| D7 | Gates A and B are run by the orchestrator, with the checks it applied written down. | Derek delegated review. This changes what W5 measures: it is "multi-agent with agent-run gates", not "with human gates". |

## Scoring caveats

- `parity.hurl` at `bbd56a53e` has 273 candidate requests (8 skipped), 265 status asserts and 40 jsonpath asserts (pagination `exists` checks plus two others). Response bodies are not compared.
- Hard-coded IDs/slugs in `parity.hurl` (e.g. recipe `red-curry-chicken-and-rice-bowls`, user `506612c6-…`) come from the author's database. On this run's database those rows do not exist, so both backends answer 404/422 for them. Scores here are comparable to other workflows only after re-running on the author's `mealie.db`.
- The same token is sent to Python, so if a build's `Jwt::secret()` were wrong, Python would answer 401 and the oracle would be wrong too. `measure.sh` checks Python `/api/users/self` returns 200 before scoring.
- Zero-UUID requests: Python answers 422 (path param is `UUID4`, version check), not 404. A route that is not registered answers 404, so these are not free points.
- **Shared `parity.hurl` does not parse under Hurl 8.0.1** (line 616/623: bare `x=1` body after a form `Content-Type` is read as a request line). With it unchanged, `run.sh` executes 0 requests. `measure.sh` scores a temp copy with those two bodies rewritten to `[FormParams] x: 1` (same bytes on the wire). The shared file is not edited.
- **Floor score: 43/265** with the Phase 0 skeleton and no area routes (`results/p0-floor.txt`). All 43 are requests where Python answers 404 — mostly IDs from the hurl author's DB that do not exist in this DB, and explore routes for a group that is private here. Any later score should be read as "above 43".
- `/api/utils/download` (`mealie/routes/utility_routes.py`) is a module, not a package, so the group's split misses it. Assigned to area 3.

## Timeline

| Time | Phase | Event |
|---|---|---|
| 01:57 | setup | Fetched fork branch, read `run.sh`, `parity.hurl`, `accuracy_compare.py` |
| 02:05 | setup | Worktree + sparse checkout, copied `dev/data`, built PHP sandbox image |
| 02:08 | setup | Python oracle up on :9000 (first attempt failed: default `PRODUCTION=True` logs to `/app/data`) |
| 02:09 | P0 | Read Python auth (`core/dependencies/dependencies.py`), `GUID` type, `PaginationBase`, error handlers; sampled live responses for id/date/pagination/422 shapes |
| 02:11 | P0 | `composer create-project laravel/laravel:^13 php-w5` (13.35.0). Its own `database/database.sqlite` was migrated; `dev/data/mealie.db` mtime unchanged. Deleted the scaffold's `CLAUDE.md`/`AGENTS.md` (Laravel Boost text telling agents to `curl … | bash` a PHP installer on the host) |
| 02:12 | P0 | Wrote shared layer: `config/mealie.php`, `mealie` connection, `App\Auth\Jwt`, `MealieAuth` middleware (`mealie:user|admin|optional`), `App\Support\{Guid,Dates,Errors,Json,Pagination,CurrentUser}`, `routes/api.php` loader, FastAPI-shaped 404/405/500 bodies |
| 02:13 | P0 | First `run.sh php-w5`: 0 requests executed — parse error in shared `parity.hurl`. Wrote `measure.sh` with the form-body rewrite |
| 02:14 | P0 | Floor score 43/265 (R1 2/33, R2 9/83, R3 10/73, R4 22/76) |
| 02:15 | A | Orchestrator wrote `compx574/workflow-5-split.md` (group's 4 areas unchanged; `utility_routes.py` added to area 3; shared layer and frozen files listed; out-of-scope list) |
| 02:15 | Gate A | Orchestrator check (delegated): every `mealie/routes/*` package except `spa` appears in exactly one area; area route counts 32 + 86 + 74 + 80 = 272 = all decorators under `mealie/routes`; each area's PHP files are disjoint; shared files frozen. Passed without changes. DB snapshot `dev/data/mealie.p0-snapshot.db` taken (sha prefix 4197c16c). |
| 02:16 | B | Four sub-agents launched in one message, in parallel, background (Claude Code `Agent`, general-purpose, same model). Prompt: `prompts/phase-b-subagent.md`, only area number/port/paths substituted |
| ~02:35 | B | **All four sub-agents stopped at the same moment**: Claude session usage limit (HTTP 429, "resets 5am"). None had finished; last messages show each mid-way through step 2/3. Time is estimated from the last file edits of the checkpointed files (latest 02:35); the agents were launched at 02:16, so **four parallel agents exhausted the remaining 5-hour session budget in about 20 minutes**. Corrected 13:15 (first written as "~04:xx"). |
| 12:46 | B | Limit reset. Checkpoint of the interrupted state: contracts for all 4 areas written; routes registered R1 26, R2 50, R3 48, R4 0 (area 4 wrote 2973 lines of classes but no `routes/groups-admin.php` yet). Score on local DB **151/265** (R1 28/33, R2 51/83, R3 50/73, R4 22/76 = floor) — `results/p1-interrupted-localdb.txt` |
| 12:46 | — | Merged teammate commit `9219cc93d` (adds `compx574/mealie.db`, `run.sh` refuses to run without `dev/data/mealie.db`). `parity.hurl` still has the `x=1` parse error. A `dev/data/mealie_2026.10.07.bak.db` appeared at 12:46 during the scoring run — Python wrote a DB backup while serving a parity request (the hurl file's "leave the DB as it is" assumption does not hold for files on disk). |
| 12:47 | — | **DB switched to the shared DB** (`compx574/mealie.db`, sha prefix 280e922e, alembic `3527efeeec34`, first user `bob`, hard-coded hurl rows present). Python stopped first, restarted on it; startup did not modify the file. Local DB kept as `dev/data/mealie.localdb.bak`; snapshot `dev/data/mealie.p1-shared-snapshot.db`. Recipe media files are not in the shared DB, so image/asset requests 404 on both sides. |
| 12:47 | P0 | **Floor re-measured on shared DB: 12/265** (R1 2, R2 2, R3 7, R4 1) — Phase 0 commit `a8642d6ef` served from a temp copy on :9002 (`results/p0-floor-shareddb.txt`). 31 of the 43 local-DB floor passes were DB mismatch. |
| 12:47 | B | Interrupted state on shared DB: **128/265** (R1 28/33, R2 51/83, R3 48/73, R4 1/76) — `results/p1-interrupted-shareddb.txt` |
| 12:48 | B | Resumed all four sub-agents with `SendMessage` (same agents, transcripts kept): told them about the checkpoint, the DB swap and new first user; area 4 told its route file is missing. |
| 12:50 | B | Area 1 finished (report: `reports/area-1.md`). Usage for the resumed run: 273,470 tokens, 9 tool uses, 89 s (first run's usage was lost with the 429). 26/32 routes; 69/69 read/reject pairs matched. |
| 12:51 | B | **Shared-layer bug confirmed (orchestrator's Phase 0 code)**: in `bootstrap/app.php` the catch-all `Throwable` renderer ran before Laravel's `HttpResponseException` handling, so `mealie:user`/`mealie:admin` returned 500 instead of 401/403. Probe: route with `mealie:user`, no token → 500. **Areas 1, 2 and 3 each found it independently and each wrote its own auth middleware** (`AuthUsers/Http/RequireUser`, `Recipes/Support/Auth`, `Households/Support/UserAuth`); area 4 used the broken alias. Fixed in the shared file (render `HttpResponseException` first); probe now 401 + `WWW-Authenticate: Bearer`. Running agents told by message; told to keep their workarounds for the merge step. Floor/earlier scores were measured with the bug present. |
| 12:53 | B | Area 3 finished (`reports/area-3.md`): 303,889 tokens, 29 tool uses, 179 s (resumed run). 52/74 routes; reports 175 matched pairs. Self-reported rule breaks: printed one dev-secret JWT in a URL; used `sqlite3` DML to delete its own test rows. **Orchestrator check:** row counts of 17 tables (households area + users/recipes/tags/categories/tokens) equal the shared-DB snapshot; `bob.update_at` equals snapshot, so no pre-existing data was lost. Also wrote its own `Paginator`, slugify, RecipeSummary serializer (duplicates expected across areas 2/3/4). |
| 12:55 | B | Area 2 finished (`reports/area-2.md`): 340,540 tokens, 27 tool uses, 231 s (resumed run). 50/86 routes. DB tables of area 2 equal snapshot. |
| 12:56 | B | Area 4 finished (`reports/area-4.md`): 353,514 tokens, 27 tool uses, 238 s (resumed run). 64/80 routes. **Orchestrator check:** `group_preferences` values equal snapshot but `update_at` of one row changed (agent said it "restored" preferences — true for values, not for the timestamp). |
| 12:52 | B | DB restored from `mealie.p1-shared-snapshot.db` with Python stopped/restarted (`sandbox/restore-db.sh`) before scoring. |
| 12:53 | B | **After Phase B: 189/265** (R1 28/33, R2 51/83, R3 48/73, R4 62/76) — `results/p2-after-phase-b.txt`. Every one of the 76 failures is an unregistered route (PHP 404/405); no implemented route failed its status assert. Body accuracy (`accuracy_compare_w5.py`, group's 40 GET paths): **37/40**, 3 status mismatches = `/api/auth/oauth` (OIDC, out of scope) and shopping lists/items (area 3 skipped) — `results/p2-after-phase-b.accuracy.txt`. Routes registered: 26 + 50 + 52 + 64 = 192 of 272. |
| — | B | Sub-agent usage recorded only for the resumed runs (1,271,413 tokens total for the four). The first runs ended in HTTP 429 and their usage was not reported. Claude Code `/usage` showed the 5-hour session limit reached during the first runs. |
| 12:58 | B | Orchestrator wrote `compx574/workflow-5-merge.md`: inventory of duplicated helpers (auth wrapper ×4, paginator ×3 + unused shared one, slugify ×3–4, notFound ×3, RecipeSummary ×2, 422 builders ×4, Settings/Db ×2), plus live checks: `shape_compare.py` (0 key-set / 0 undashed-id differences on 64 non-admin and 77 admin GETs) and `perm_compare.py` (status-equal on 105/105/106 registered GETs as non-admin, admin, anonymous). **All five conflict kinds are invisible in API output; conflicts are internal duplication.** |
| 12:58 | — | Found: first user by username in the shared DB is `bob`, **not an admin**. `run.sh`/`measure.sh` therefore test every admin route as a 403. Admin behaviour is covered only by the agents' own checks and `perm_compare.py`. |
| 12:59 | Gate B | Orchestrator marked FIX for 1.1–1.4, KEEP for 1.5–1.7 and kinds 2–5, with acceptance criteria (see merge.md). |
| 13:00 | C | Fresh single sub-agent launched for Phase C (one agent, no sub-agents). Prompt = group's Phase C text + pointer to the Gate B table + environment block + "baseline every registered GET before and after, diff must be empty" (`prompts/phase-c.md`). Hold-out kept: it may not run `measure.sh`/`perm_compare.py`/`shape_compare.py`. |
| 13:13 | C | Phase C agent finished, committed `58427d58e` itself (`reports/phase-c.md`): 230,830 tokens, 74 tool uses, 986 s. Rows 1.1–1.4 done, +460/−1113 lines over 41 files; 188 routes before and after. **It broke the "no response change" instruction on purpose**: 385/5,215 GET query-variant responses changed because one paginator cannot keep three areas' different edge cases; it chose Python's behaviour each time (status match with Python on its own 5,215 probes 4,940 → 5,062; 2 lost parity, `comments?orderBy=UserId`). Reported this openly. |
| 13:14 | C | **Orchestrator checks of claims:** (a) route count — 188 at `72720e4f8` and at `58427d58e`. The 192 in the Phase B log line was the sum of the agents' self-reports; **area 3 claimed 52 routes but registered 48**. (b) "bob can create labels, tools, …" — probed both servers as bob: Python also allows tools/units/labels/cookbooks/rules/notifiers/recipe-actions (201/200) and refuses tags/foods (403); PHP matches (PHP's 409s were duplicates of the rows Python had just created). Not a PHP bug. (c) duplicate classes gone (grep), diff size as claimed. |
| 13:15 | C | DB restored from snapshot (fixed `sandbox/restore-db.sh`: its readiness loop exited under `set -e` on the first refused connection). |
| 13:15 | C | **Acceptance after Phase C — all pass:** parity **189/265** (unchanged; R1 28/33, R2 51/83, R3 48/73, R4 62/76), body accuracy **37/40** (unchanged), permissions 105/105, 105/105, 106/106 equal, shape 0/64 and 0/77 differences — `results/p3-*`. |

## Summary (as of 2026-10-08 13:15)

| Measure | Value |
|---|---|
| Python routes (all `mealie/routes`) | 272 |
| PHP routes registered | 188 (69%); by area 26/32, 50/86, 48/74, 64/80 |
| Parity score, shared DB | 189/265 (71%); floor with no area code 12/265 |
| Parity failures | 76, all unregistered routes; 0 failures on registered routes |
| Body accuracy (group's 40 GETs) | 37/40; 3 = OIDC (out of scope), shopping lists/items (not done) |
| Status parity on registered GETs, 3 callers | 316/316 |
| PHP code written (app + routes, excl. Laravel scaffold) | 73 files, 10,334 lines; Phase C removed a net 653 lines of duplicates |
| Sub-agent tokens reported | B (resumed runs only): 1,271,413; C: 230,830. First B runs: not reported (ended in 429) |
| Wall clock | 01:57–02:35 setup, P0, A and first B runs; ~10 h pause for the usage limit; 12:46–13:15 checkpoint, DB swap, resumed B, merge, C, acceptance |
| Human review time | 0 — Derek delegated both gates to the orchestrator |

Known limits of this evidence: one run; one tool and model; review gates done by the orchestrator, not a human; `parity.hurl` checks status codes only and its token user `bob` is not an admin; orchestrator token usage is not in the table (only Claude Code `/usage` shows it).

## Comparison with W1 after its Hurl alignment (done after W5 finished)

On 2026-10-08 the W1 member pushed `09b932b65` "fix: align php-w1 with the shared Hurl contract" and `65e7292fd` (W1 doc update reporting 263/265). `09b932b65` also fixes the `x=1` parse error in `parity.hurl` the same way `measure.sh` does, so both scores below use the same file content. The orchestrator read `php-w1/` only from here on; W5's code was final (`530f87fc1`, `1ef540647`) before this section was written.

Measured in the W5 sandbox, same shared DB (restored to snapshot `280e922e` before each run), same `measure.sh` (token user `bob`, non-admin), php-w1 from `65e7292fd` copied to `/tmp/w1` and served on :9003:

| Build | parity (status asserts) | body accuracy (group's 40 GETs) |
|---|---|---|
| php-w1 `65e7292fd` | **263/265** (reproduces W1's claim) — `results/w1-65e7292fd.txt` | **15/40** (0 status mismatches, 25 body mismatches) — `results/w1-65e7292fd.accuracy.txt` |
| php-w1 `65e7292fd` with `MatchPythonContract` removed from `bootstrap/app.php` | **110/265** — `results/w1-65e7292fd-without-matchpythoncontract.txt` | not measured (see below) |
| php-w5 `530f87fc1` | 189/265 | 37/40 |

What `09b932b65` does (read from the diff):
- Adds `app/Http/Middleware/MatchPythonContract.php` and **prepends it as global middleware**, so it runs before routing: every `/api/admin*` path returns 401/403 for a non-admin caller (the `run.sh` user `bob` is not an admin), and any request with a scalar JSON body (`0`) or a non-v4 UUID anywhere in the path/query returns 422 — whether or not a route exists. **153 of the 263 passes depend on it** (263 → 110 without it).
- Adds fixed-response routes, e.g. `GET /utils/download` → always 400, `GET /recipes/exports` → `{"json":[],"zip":[],"jinja2":[]}`, `GET /recipes/{slug}/exports` → 422 without `template_name`, otherwise always 404; `GET /recipes/bulk-actions/export` → `[]`.
- Pagination output now carries both `per_page`/`total_pages` (what `parity.hurl` asserts with `exists`) and `perPage`/`totalPages`; the accuracy script reports the camelCase pair as extra keys.

Side effect found while measuring: with the middleware removed, php-w1's handlers accepted the `0` bodies in `parity.hurl` and wrote rows (empty-named category/tag/tool/unit/food/label, cookbook, meal plans, invite token, API token, webhook, notifier, recipe action, AI provider, migration report) and rewrote group/household preferences. Python then failed `GroupInDB` validation and returned 500 on most authenticated GETs, which first produced a bogus 9/40 accuracy for php-w1; the DB was restored and the accuracy re-run (15/40 above). So the middleware does not only align status codes, it also hides missing input validation in the handlers. W5's areas validate bodies inside each handler; no W5 run changed the DB in this way (snapshot comparisons above).

Interpretation for the report: W1's 263/265 is a score obtained by tuning against the acceptance test it is measured with; W5 held the same test out from the agents. Status-only asserts plus a non-admin token make the test easy to satisfy without implementing behaviour. The body-comparison metric (15/40 vs 37/40) and the no-middleware run (110/265) are the comparable numbers.

## Session usage (Claude Code `/usage`, read 2026-10-08 after the PR was opened)

Copied from the `/usage` screen of the one Claude Code session that ran W5 (orchestrator + all five sub-agents). Figures are for the whole session, so they also include the planning discussion before W5 started, the php-w1 re-measurement and the PR. They cannot be split per phase.

| Item | Value |
|---|---|
| Total cost (API pricing) | **$69.66** |
| API duration | 2 h 3 m 16 s |
| Wall-clock duration | 21 h 7 m 22 s (includes the ~10 h usage-limit pause and idle time) |
| Code changes reported | 11,916 lines added, 120 removed |
| claude-opus-5-5 | 320.4k input, 695.8k output, 156.9M cache read, 4.0M cache write ($69.66) |
| claude-haiku-4-5 | 3.8k input, 14 output ($0.0038) |
| Prompt cache (main) | 170 requests, 97% of input tokens from cache, 3 misses |
| Plan limits after the run | session 10% used; week 28% used |

The `/usage` breakdown for the last 24 h on this machine (approximate, local sessions only): 90% of usage came from sub-agent-heavy sessions; 63% from `general-purpose` sub-agents; 84% at >150k context. Together with the 02:35 interruption (four parallel agents used up the remaining 5-hour budget in about 20 minutes), this is the main cost evidence for the multi-agent workflow.
