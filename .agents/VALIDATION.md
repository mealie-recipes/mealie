# Validation record and cold-start assumptions

Validated on 2026-07-18 in an isolated macOS worktree at revision `ee181a5`:

- Cold `setup` created Python 3.12 and `.venv` from `uv.lock`, installed frontend dependencies from
  `yarn.lock`, and verified agent-browser 0.27.0. A second setup completed without changing state.
- Duplicate `dev-start`, `seed`, `verify`, `collect`, and `dev-stop` calls were safe. The second seed
  reused `agent-qa-recipe`.
- The backend and frontend bound to `0.0.0.0:9000` and `0.0.0.0:3000`. Backend data was isolated
  under `.agents/state/data` by the explicit testing/data environment.
- `tests/unit_tests/test_config.py`: 30 passed (10 existing pytest warnings).
- Browser QA authenticated, displayed the seeded recipe, and produced a 37 KB screenshot, console
  report, page-error report, 813 KB network report and extracted network-failure report. The steady
  page had no console/page errors. Its two reported HTTP 404s were the expected missing image for a
  recipe seeded without media.
- Every hook passed `bash -n` twice. No services were left listening after validation.

The exe.dev cold path still assumes outbound HTTPS plus `curl`, `tar`, xz support and standard Linux
process tools (`bash`, `pgrep`, and Python after setup). Chromium system libraries vary by image;
use `AGENTS_BROWSER_WITH_DEPS=true .agents/hooks/browser-setup`, which may require root/sudo. A VM
with another process on ports 3000 or 9000 is rejected rather than killed. Password-form browser
login is covered; OIDC-only remote QA needs a project-specific auth hook or pre-authenticated browser
state. Live validation against exe.dev remains an orchestrator integration/evaluation task.
