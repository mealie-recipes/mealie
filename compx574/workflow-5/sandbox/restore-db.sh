#!/bin/sh
# Stop the Python oracle, restore the shared DB snapshot, restart it.
set -eu
W=/Users/derek/Documents/dev/mealie/.worktrees/w5
docker exec competent_colden sh -c 'for p in /proc/[0-9]*; do c=$(tr "\0" " " < $p/cmdline 2>/dev/null); case "$c" in *"python mealie/app.py"*) kill ${p#/proc/} ;; esac; done' || true
sleep 3
cp "$W/dev/data/mealie.p1-shared-snapshot.db" "$W/dev/data/mealie.db"
rm -f "$W/dev/data/mealie.db-journal"
docker exec -d -u vscode -w /workspaces/mealie/.worktrees/w5 competent_colden bash -lc 'PRODUCTION=False uv run python mealie/app.py > /tmp/w5-python.log 2>&1'
for i in $(seq 1 40); do s=$(docker exec competent_colden curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9000/api/app/about || true); [ "$s" = 200 ] && break; sleep 2; done
echo "python=$s db=$(shasum "$W/dev/data/mealie.db" | cut -c1-16)"
