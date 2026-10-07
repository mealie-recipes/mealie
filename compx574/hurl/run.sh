#!/bin/sh
# Run the shared Hurl file against one PHP build.
# Usage: compx574/hurl/run.sh [php-directory] [candidate-url]
set -eu

root=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
if [ ! -f "$root/dev/data/mealie.db" ]; then
  echo "Copy compx574/mealie.db to dev/data/mealie.db before running." >&2
  exit 1
fi
php_dir=${1:-php-w1}
candidate=${2:-http://127.0.0.1:9001}

token=$(
  cd "$root/$php_dir"
  php -r '
require "vendor/autoload.php";
$app = require "bootstrap/app.php";
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
$row = Illuminate\Support\Facades\DB::connection("mealie")->table("users")->orderBy("username")->first();
$hex = str_replace("-", "", (string) $row->id);
$sub = sprintf("%s-%s-%s-%s-%s", substr($hex, 0, 8), substr($hex, 8, 4), substr($hex, 12, 4), substr($hex, 16, 4), substr($hex, 20, 12));
echo App\Auth\Jwt::encode([
    "sub" => $sub,
    "rme" => false,
    "iss" => "mealie",
    "iat" => time(),
    "exp" => time() + 3600,
], App\Auth\Jwt::secret());
'
)

hurl --test --continue-on-error \
  --secret "token=$token" \
  --variable "candidate=$candidate" \
  "$root/compx574/hurl/parity.hurl"
