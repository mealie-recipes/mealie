# Environment for mise tasks (mise.toml). Values already set in the shell win,
# so overrides like `API_PORT=9100 mise run py` work.
set -a

shell_env="$(export -p)"
# .env is loaded last so it takes precedence over .dev.env
[ -f .dev.env ] && . ./.dev.env
[ -f .env ] && . ./.env
eval "$shell_env"
unset shell_env

DEFAULT_GROUP="${DEFAULT_GROUP:-Home}"
DEFAULT_HOUSEHOLD="${DEFAULT_HOUSEHOLD:-Family}"
PRODUCTION="${PRODUCTION:-false}"
# Install from the committed lockfile; never re-resolve. Required because the
# rolling `exclude-newer` cooling window (pyproject [tool.uv]) would otherwise
# make every `uv run`/`uv sync` re-resolve and fail on in-window pins.
UV_FROZEN="${UV_FROZEN:-1}"
API_PORT="${API_PORT:-9000}"
API_DOCS="${API_DOCS:-True}"
TOKEN_TIME="${TOKEN_TIME:-256}"
# Mailpit SMTP config; start it with `mise run dev:services`
SMTP_HOST="${SMTP_HOST:-localhost}"
SMTP_PORT="${SMTP_PORT:-1025}"
SMTP_FROM_NAME="${SMTP_FROM_NAME:-MealieDev}"
SMTP_FROM_EMAIL="${SMTP_FROM_EMAIL:-mealie@example.com}"
SMTP_AUTH_STRATEGY="${SMTP_AUTH_STRATEGY:-NONE}"
BASE_URL="${BASE_URL:-http://localhost:3000}"
LANG="${LANG:-en-US}"

set +a
