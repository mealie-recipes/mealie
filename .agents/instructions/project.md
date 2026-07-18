# Mealie project guidance

- Inspect code before starting services; code-only work does not require the dev stack.
- Use `.agents/hooks/setup` only when dependencies are needed, and `.agents/hooks/resume` when the
  task needs the running app.
- Start capabilities lazily. Browser work uses `.agents/hooks/browser-setup`; a normal backend test
  does not need Chromium or the frontend.
- Use focused checks through `.agents/hooks/test` before broad suites. Follow Mealie's existing
  Taskfile, uv, Ruff, pytest, Yarn, ESLint, Vue and Nuxt conventions.
- `.agents/hooks/reset` affects only ignored agent data, but is destructive within that boundary.
- Never read, post, persist, or commit `.agents/state/auth.token`, browser profiles, `.env` values,
  Slack tokens, GitHub App keys, or remote-QA passwords.
- Put screenshots and diagnostics under `.agents/artifacts`, then call `.agents/hooks/collect`.
