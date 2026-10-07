#!/bin/sh
# Workflow 5 scoring wrapper around the shared parity check. Run inside the mealie-w5-php container.
# Usage: compx574/workflow-5/measure.sh <label> [php-directory] [candidate-url]
#
# Differences from compx574/hurl/run.sh, all on the measuring side (the shared files are not edited):
#  1. parity.hurl is copied to a temp file and bare form bodies ("x=1" after a form Content-Type) are
#     rewritten to [FormParams]. Hurl 8.0.1 rejects the bare form and the whole file fails to parse.
#  2. The token is minted the same way, then checked against Python /api/users/self. If Python does not
#     answer 200 the oracle is wrong (bad secret) and scoring stops.
#  3. A JSON report is scored per candidate request: pass = every assert on that request succeeded.
#     Writes results/<label>.txt (summary + per-request table) and results/<label>.hurl.txt (raw output).
set -eu

label=${1:?label required}
php_dir=${2:-php-w5}
candidate=${3:-http://127.0.0.1:9001}
root=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
out="$root/compx574/workflow-5/results"
tmp=$(mktemp -d)
mkdir -p "$out"

awk 'prev ~ /^Content-Type: application\/x-www-form-urlencoded$/ && $0 ~ /^[A-Za-z_]+=/ {
       split($0, kv, "="); print "[FormParams]"; print kv[1] ": " kv[2]; prev = $0; next }
     { print; prev = $0 }' "$root/compx574/hurl/parity.hurl" > "$tmp/parity.hurl"

token=$(
  cd "$root/$php_dir"
  php -r '
require "vendor/autoload.php";
$app = require "bootstrap/app.php";
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
$row = Illuminate\Support\Facades\DB::connection("mealie")->table("users")->orderBy("username")->first();
$hex = str_replace("-", "", (string) $row->id);
$sub = sprintf("%s-%s-%s-%s-%s", substr($hex, 0, 8), substr($hex, 8, 4), substr($hex, 12, 4), substr($hex, 16, 4), substr($hex, 20, 12));
echo App\Auth\Jwt::encode(["sub" => $sub, "rme" => false, "iss" => "mealie", "iat" => time(), "exp" => time() + 3600], App\Auth\Jwt::secret());
'
)

oracle=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $token" http://127.0.0.1:9000/api/users/self)
if [ "$oracle" != "200" ]; then
  echo "Python rejected the minted token (status $oracle); refusing to score." >&2
  exit 2
fi

set +e
hurl --test --continue-on-error --secret "token=$token" --variable "candidate=$candidate" \
  --report-json "$tmp/report" "$tmp/parity.hurl" > "$out/$label.hurl.txt" 2>&1
set -e

php -r '
[$_, $report, $candidate, $label, $phpDir] = $argv;
$entries = json_decode(file_get_contents($report), true)[0]["entries"];
$region = function (string $path): string {
    $map = ["auth" => 1, "users" => 1, "app" => 1, "validators" => 1,
            "recipes" => 2, "organizers" => 2, "foods" => 2, "units" => 2, "comments" => 2, "parser" => 2,
            "households" => 3, "media" => 3, "shared" => 3, "utils" => 3,
            "groups" => 4, "admin" => 4, "explore" => 4];
    $seg = explode("/", trim(parse_url($path, PHP_URL_PATH), "/"))[1] ?? "";
    return isset($map[$seg]) ? "R".$map[$seg] : "R?";
};
$rows = []; $prevStatus = null; $byRegion = [];
foreach ($entries as $e) {
    $call = end($e["calls"]);
    $url = $call["request"]["url"];
    if (!str_starts_with($url, $candidate)) { $prevStatus = $call["response"]["status"] ?? null; continue; }
    $path = substr($url, strlen($candidate));
    $pass = $e["asserts"] !== [] && !in_array(false, array_column($e["asserts"], "success"), true);
    $r = $region($path);
    $byRegion[$r] ??= [0, 0];
    $byRegion[$r][1]++;
    if ($pass) { $byRegion[$r][0]++; }
    $rows[] = sprintf("%s\t%s\t%s %s\tpy=%s\tphp=%s", $pass ? "PASS" : "FAIL", $r, $call["request"]["method"], $path, $prevStatus ?? "-", $call["response"]["status"] ?? "-");
}
$pass = count(array_filter($rows, fn ($l) => str_starts_with($l, "PASS")));
ksort($byRegion);
echo "label=$label php_dir=$phpDir date=".date("c")."\n";
echo "score=$pass/".count($rows)." (candidate requests with every assert passing; 8 skipped endpoints excluded)\n";
foreach ($byRegion as $r => [$p, $t]) { echo "$r=$p/$t\n"; }
echo "\n".implode("\n", $rows)."\n";
' "$tmp/report/report.json" "$candidate" "$label" "$php_dir" > "$out/$label.txt"

head -7 "$out/$label.txt"
rm -rf "$tmp"
