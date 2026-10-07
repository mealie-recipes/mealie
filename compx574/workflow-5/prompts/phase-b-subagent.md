# Phase B sub-agent prompt (template)

Sent verbatim to each of the four sub-agents, with {N}, {AREA}, {PORT}, {ROUTES_FILE}, {NAMESPACE_DIR} filled from compx574/workflow-5-split.md.

---

You are the area {N} sub-agent in workflow 5 of a group experiment: re-implementing Mealie's FastAPI backend (`mealie/`) in PHP (Laravel 13) in `php-w5/`. Three other sub-agents are working on the other areas at the same time in the same directory. You cannot talk to them.

Working directory (host): /Users/derek/Documents/dev/mealie/.worktrees/w5 — a git worktree. Stay inside it.

Read these sections of `compx574/workflow-5-split.md` and nothing about the other areas' plans: "Rules for every area", "Shared layer", "Files no area may change", "Area {N} — {AREA}", "不在范围内". The rules there are binding. In short: only edit the files your area may create; copy every HTTP method and full path from your Python routers; Python stays where it is; no fixed-error stubs; do not read php-w1/, compx574/workflow-1-single-instruction.md or compx574/hurl/; no migrations; no secrets in output; do not commit.

Environment:
- Python reference server is already running at http://127.0.0.1:9000 (dev mode, secret `shh-secret-test-key`). Do not restart it.
- PHP and Composer exist only in the container: `docker exec mealie-w5-php bash -lc 'cd php-w5 && <cmd>'` (container working dir is the worktree root). The container shares the network with the Python server, so 127.0.0.1:9000 works inside it.
- Start your own server in the background on port {PORT} only: `docker exec -d mealie-w5-php bash -lc 'cd php-w5 && php artisan serve --host=127.0.0.1 --port={PORT} > /tmp/area{N}.log 2>&1'`. Restart it if you change routes and it misbehaves. Stop it when you finish.
- Get a bearer token for the first user (admin) like this, inside the container, and keep it in a shell variable or temp file in the container — never print it:
  `cd php-w5 && php -r 'require "vendor/autoload.php"; $app=require "bootstrap/app.php"; $app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap(); $u=Illuminate\Support\Facades\DB::connection("mealie")->table("users")->orderBy("username")->first(); echo App\Auth\Jwt::encode(["sub"=>App\Support\Guid::fromDb($u->id),"iat"=>time(),"exp"=>time()+7200], App\Auth\Jwt::secret());' > /tmp/area{N}.token`
  For a non-admin caller, sign the same way for another user (check `admin` = 0).
- `sqlite3` is available in the container for reading the DB schema (`sqlite3 ../dev/data/mealie.db .schema <table>` from php-w5). Read-only.

Step 1 — contract (before any route code). Create `compx574/workflow-5-contracts/area-{N}.md`. For every endpoint you plan to implement, write:
- method and full path (with /api), and its Python source (file:function);
- the schema file(s) whose field names the JSON uses (e.g. mealie/schema/recipe/recipe.py RecipeSummary);
- how ids are stored (CHAR(32) hex / integer / slug) and how they are returned;
- who may call it, and which Python permission check that is based on (dependency + any in-handler check, with file:line);
- what of it you are not implementing.
Then a section "Not implemented" listing every Python route of your area you are not registering, with the reason, and a section "Helpers duplicated from / missing in shared layer".

Step 2 — implement. Routes only in `php-w5/{ROUTES_FILE}`; classes only under `php-w5/{NAMESPACE_DIR}` (namespace accordingly); optional tests under your tests folder. Use the shared layer; do not edit it. Read the Python handler, its service/repository code and the Pydantic schemas for every endpoint — field names, defaults, nulls, ordering, status codes and permission checks come from there, not from guesses. Register routes with the same order-sensitive care as FastAPI (static paths before parameterised ones).

Step 3 — verify. For each implemented endpoint compare Python :9000 and your :{PORT} with the same request (status + JSON body, ignoring volatile values such as timestamps you just created). Include at least: an authenticated success case where data exists, a not-found / invalid-id case (Python returns 422 for a malformed or non-v4 UUID on UUID4 params), a bad-body case for writes (body `0`), and an unauthenticated case. Fix differences that come from your code. Keep a short tally.

Finish with a report (under 400 words): endpoints implemented / Python routes in area; verification tally (matched / differ / not checked) with the main remaining differences; anything in the shared layer that was wrong or missing; any rule you could not follow. Do not paste code.
