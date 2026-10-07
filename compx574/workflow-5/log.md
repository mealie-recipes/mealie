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
| PHP sandbox | Container `mealie-w5-php` from `env/Dockerfile` (PHP 8.4.26, Composer 2.10.3, Hurl 8.0.1). Shares the dev container's network namespace. No git credentials, SSH keys or registry tokens are mounted. The orchestrator itself runs on the host with Derek's git config, so it is not fully sandboxed |
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
