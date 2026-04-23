#!/bin/bash

PROTO=${PROTO:-http}
PORT=${APP_PORT:-9000}

python -c "
import urllib.request, sys
try:
    urllib.request.urlopen('${PROTO}://127.0.0.1:${PORT}/api/app/about', timeout=10)
    sys.exit(0)
except Exception:
    sys.exit(1)
"
