---
name: frontend-e2e
description: Run Mealie's backend and frontend dev servers and drive the UI in a real browser with the Playwright MCP. Use when building or debugging a frontend feature, reproducing a UI bug, checking a change visually (desktop or mobile), taking screenshots for a PR, or writing and running a Playwright spec in tests/e2e.
---

# Frontend end-to-end work

The loop is: start both dev servers, log in, drive the page with the `playwright` MCP tools (`mcp__playwright__*`), edit code, let hot reload pick it up, and check again. When the behavior should stay fixed, turn it into a spec under `tests/e2e/`.

## 1. Check what is already running

Several checkouts of this repo can exist at once (hive worktrees), and they share the default ports. Before starting anything:

```bash
lsof -nP -iTCP:9000 -iTCP:3000 -sTCP:LISTEN
```

For each PID, see which checkout it belongs to:

```bash
lsof -a -p <PID> -d cwd -Fn | tail -1
```

- Process cwd is inside this repo: reuse it.
- Process cwd is another checkout: leave it alone and use other ports (step 2).
- Never kill a server you didn't start in this session without asking.

## 2. Start the servers

Run each one with the Bash tool's `run_in_background: true` so it keeps running and its output stays readable. Backend first:

```bash
mise run py
```

```bash
mise run ui
```

The frontend proxies `/api`, `/docs`, and `/openapi.json` to `API_URL` (default `http://localhost:9000`), so the browser only ever talks to the frontend port.

**Alternate ports** (when the defaults are taken by another checkout). Shell env wins over the `[env]` block in `mise.toml`, so prefix the commands:

```bash
API_PORT=9100 BASE_URL=http://localhost:3100 mise run py
```

```bash
API_URL=http://localhost:9100 PORT=3100 mise run ui
```

Then use `http://localhost:3100` everywhere below.

If `mise run ui` exits with `pnpm: could not resolve pnpm to a regular file within 40 symlink hops`, the shell is using a pnpm other than the one `packageManager` in `frontend/package.json` pins. Install that version, or run the same command from `frontend/` directly: `pnpm run dev --no-fork`, with the same env prefix.

**Wait for readiness** without `sleep`:

```bash
curl -sf --retry 30 --retry-delay 2 --retry-all-errors -o /dev/null http://localhost:9000/api/app/about && echo backend up
curl -sf --retry 60 --retry-delay 2 --retry-all-errors -o /dev/null http://localhost:3000 && echo frontend up
```

The first frontend load compiles on demand and can take 30s or more. If a check fails, read the background task's output before retrying -- a missing `uv sync` / `pnpm install` (`mise run setup`) or a migration error shows up there.

Dev data lives in `dev/data/` (SQLite). It persists across runs. Don't run `mise run dev:clean` without asking -- it deletes the user's local data.

## 3. Log in

Default admin: `changeme@example.com` / `MyPassword`.

Through the UI:

1. `browser_navigate` to `http://localhost:3000/login`
2. `browser_fill_form` with the "Email or Username" and "Password" fields, then click "Login"
3. On a fresh database the app redirects to `/admin/setup`. Click "I'm already set up, just bring me to the homepage" unless the setup flow is what you're testing.

Faster, when login isn't the subject -- `browser_run_code_unsafe`:

```js
async (page) => {
  const res = await page.request.post('http://localhost:3000/api/auth/token', {
    form: { username: 'changeme@example.com', password: 'MyPassword' },
  });
  return res.status();
}
```

The response sets the session cookie on the browser context, so the next `browser_navigate` is logged in. The MCP runs `--isolated`, so the session is gone when the MCP restarts; log in again then.

## 4. Seed data

Create what the page needs through the API instead of clicking through forms. Inside `browser_run_code_unsafe`, `page.request` carries the session cookie:

```js
async (page) => {
  const base = 'http://localhost:3000';
  const slug = await (await page.request.post(`${base}/api/recipes`, { data: { name: 'E2E Test Recipe' } })).json();
  return slug;
}
```

From the shell, get a token and use it as a bearer:

```bash
TOKEN=$(curl -sf -X POST http://localhost:9000/api/auth/token \
  -d username=changeme@example.com -d password=MyPassword | jq -r .access_token)
curl -sf -H "Authorization: Bearer $TOKEN" http://localhost:9000/api/recipes?perPage=5 | jq '.items[].slug'
```

The API reference is at `http://localhost:9000/docs` (`API_DOCS` is on in dev). Give seeded records a recognizable name (prefix `E2E` plus a timestamp) and delete them when you're done, so the user's dev data doesn't fill up with junk.

## 5. Drive the page

- `browser_snapshot` is the main way to look at the page. It returns the accessibility tree with element refs that `browser_click`, `browser_type`, `browser_hover`, etc. take. Prefer it over screenshots for deciding what to do next -- it's cheaper and exact.
- `browser_take_screenshot` for visual checks (layout, spacing, theming) and for images to attach to a PR. Files land in `.playwright-mcp/` (gitignored). Give them descriptive names, e.g. `<issue>-mobile-before.png`.
- `browser_resize` to check layouts. Use `1400x1000` for desktop and `400x900` for mobile -- the same widths `tests/e2e/recipe-card.spec.ts` uses. Vuetify breakpoints change the nav drawer and card grids, so check both when touching layout.
- `browser_console_messages` after every interaction that misbehaves. The `Manifest: Line: 1, column: 1, Syntax error` error is normal in dev and can be ignored.
- `browser_network_requests` to see failed API calls and their status codes. Use `browser_network_request` for one request's body.
- `browser_wait_for` with text after actions that trigger a fetch, instead of re-snapshotting in a loop.
- Dark mode: `browser_emulate_media` with `colorScheme: "dark"`, or toggle it in the user menu.

Mealie uses Vuetify, so many inputs are composites: the snapshot shows the label on a wrapper and the real `<input>` inside. If a click on a select or autocomplete doesn't open it, click the ref for the inner combobox or the field's label text instead.

## 6. Edit, reload, verify

- **Frontend** (`frontend/app/**`): Nuxt HMR applies most changes without a reload. After changes to plugins, middleware, `nuxt.config.ts`, or layouts, `browser_navigate` to the same URL to reload. The MCP blocks service workers, so the PWA cache won't serve stale bundles.
- **Backend** (`mealie/**`): uvicorn reloads on save with a 2s delay. Check the backend task output for import errors before blaming the UI.
- **Pydantic schema changes**: run `mise run dev:generate` so the TypeScript types in `frontend/app/lib/api/types/` match, then reload the page.
- **New UI strings**: add them only to `frontend/app/lang/messages/en-US.json`.

Verify the actual behavior -- what the user would see -- not just that the page rendered. Check the console and network panel once more before calling it done.

## 7. Write a spec (when the behavior should stay fixed)

Specs live in `tests/e2e/*.spec.ts` and use `@playwright/test`. Follow `tests/e2e/recipe-card.spec.ts` for the style: log in with `page.request.post('/api/auth/token', ...)`, seed through the API, assert on the page, clean up in `finally`.

Run a spec against the dev servers:

```bash
cd tests/e2e
pnpm install && pnpm exec playwright install chromium   # once; `mise run setup:e2e` installs every browser plus OS deps && E2E_BASE_URL=http://localhost:3000 PLAYWRIGHT_HTML_OPEN=never pnpm playwright test recipe-card.spec.ts --project chromium
```

`login.spec.ts` and `oidc-native.spec.ts` need the LDAP and OIDC mock servers, so they only pass against the full stack. CI runs that with `mise run e2e`, which builds the production Docker image and serves the app on port 9000 -- it takes several minutes, and it fails if a dev backend already holds port 9000. Run it only when asked or when the change touches auth.

## 8. Clean up

- Delete seeded records.
- Stop the background server tasks you started in this session (TaskStop). Leave servers you found already running.
- Call `browser_close` when done with the browser.
- Report what you verified, with screenshot paths when you took any.
