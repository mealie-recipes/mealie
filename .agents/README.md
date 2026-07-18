# Mealie agent and human hooks

These scripts are direct, repository-owned commands. They do not require an agent runtime or an
`agent-env` wrapper. Run them from any directory inside the checkout.

## Cold start

```sh
.agents/hooks/setup
.agents/hooks/dev-start
.agents/hooks/dev-wait
.agents/hooks/seed
.agents/hooks/verify
```

`setup` installs the locked Python and frontend dependencies. It locally bootstraps Node 22, uv and
agent-browser when missing; it does not depend on another checkout. On Linux, set
`AGENTS_BROWSER_WITH_DEPS=true` before `browser-setup` if the VM also needs Chromium system
libraries installed. That operation may require sudo/root depending on the image.

For an explicitly local, non-portable speed-up, `MEALIE_DEPS_SOURCE=/path/to/mealie` lets `setup`
reuse an existing `.venv` or `frontend/node_modules`. Cold sandboxes must not set it.

`resume` runs setup, preserves the isolated database, starts missing services, and waits for health.
The backend listens on `0.0.0.0:9000`; the frontend listens on `0.0.0.0:3000`. Override them with
`MEALIE_API_PORT` and `MEALIE_WEB_PORT` before starting.

## Useful boundaries

```sh
.agents/hooks/dev-status
.agents/hooks/dev-stop
.agents/hooks/reset        # deletes only .agents/state/data, then restarts
.agents/hooks/login        # API auth; token remains under ignored .agents/state
.agents/hooks/login --browser
.agents/hooks/test hooks
.agents/hooks/test backend tests/unit_tests/test_config.py
.agents/hooks/test frontend app/components/SomeComponent.vue
.agents/hooks/qa           # browser screenshot + console/network/error evidence
.agents/hooks/collect      # non-secret logs and diagnostics
```

Generated state and evidence live in ignored `.agents/state/` and `.agents/artifacts/`. The collect
hook deliberately excludes authentication tokens and browser auth profiles.

For a remote QA installation, set `MEALIE_QA_URL`, `MEALIE_QA_WEB_URL`, `MEALIE_QA_EMAIL`, and
`MEALIE_QA_PASSWORD`, then run `login` or `login --browser`. Do not put those values in the repo,
command output, screenshots, or artifacts.

## Fork arrangement

For agent-authored pull requests, use your fork as `origin` and retain the project repository as
`upstream`:

```sh
git remote rename origin upstream
git remote add origin git@github.com:YOUR_ORG/mealie.git
git fetch --all --prune
```

Create each session branch from the exact upstream revision requested by the task. Publication
credentials should be short-lived and repository-scoped; they are orchestrator concerns, not hook
inputs.
