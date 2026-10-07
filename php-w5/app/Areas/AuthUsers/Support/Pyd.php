<?php

namespace App\Areas\AuthUsers\Support;

use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Http\Request;
use stdClass;

/**
 * FastAPI request validation as the Python dev server reports it (mealie/routes/handlers.py):
 * {"status_code":422,"message":"<str(RequestValidationError)>","data":null}.
 * Errors are collected in FastAPI's order (path, query, body) and thrown by done().
 */
class Pyd
{
    /** @var list<string> */
    private array $errors = [];

    /**
     * @param  string  $file  path under mealie/routes/, e.g. "users/crud.py"
     * @param  int  $line  line of the route decorator
     */
    public function __construct(
        private string $file,
        private int $line,
        private string $func,
        private string $method,
        private string $path,
    ) {}

    public function add(string $type, array $loc, string $msg, mixed $input, ?array $ctx = null): void
    {
        $parts = [
            "'type': ".self::repr($type),
            "'loc': ".self::locRepr($loc),
            "'msg': ".self::repr($msg),
            "'input': ".self::repr($input),
        ];
        if ($ctx !== null) {
            $items = [];
            foreach ($ctx as $k => $v) {
                $items[] = self::repr($k).': '.($v instanceof RawRepr ? $v->text : self::repr($v));
            }
            $parts[] = "'ctx': {".implode(', ', $items).'}';
        }
        $this->errors[] = '{'.implode(', ', $parts).'}';
    }

    public function hasErrors(): bool
    {
        return $this->errors !== [];
    }

    public function done(): void
    {
        if ($this->errors === []) {
            return;
        }
        $n = count($this->errors);
        $file = dirname(base_path()).'/mealie/routes/'.$this->file;
        $message = $n.' validation error'.($n === 1 ? '' : 's').': '.implode(' ', $this->errors)
            .'  File "'.$file.'", line '.$this->line.', in '.$this->func.'   '.$this->method.' '.$this->path;

        throw new HttpResponseException(response()->json(
            ['status_code' => 422, 'message' => $message, 'data' => null],
            422,
            [],
            JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE,
        ));
    }

    // ---------------------------------------------------------------- params

    /** Path/query value declared as UUID4 (or UUID when $version is null). Returns 32-hex or null. */
    public function uuid(string $where, string $name, mixed $value, ?int $version = 4): ?string
    {
        return $this->uuidAt([$where, $name], $value, $version);
    }

    public function uuidAt(array $loc, mixed $value, ?int $version = 4): ?string
    {
        if (! is_string($value)) {
            $this->add('uuid_type', $loc, 'UUID input should be a string, bytes or UUID object', $value);

            return null;
        }
        [$hex, $error] = Uuid::parse($value);
        if ($hex === null) {
            $this->add('uuid_parsing', $loc, 'Input should be a valid UUID, '.$error, $value, ['error' => $error]);

            return null;
        }
        if ($version !== null && hexdec($hex[12]) !== $version) {
            $this->add('uuid_version', $loc, "UUID version {$version} expected", $value, ['expected_version' => $version]);

            return null;
        }

        return $hex;
    }

    public function int(string $where, string $name, string $value): ?int
    {
        $trimmed = trim($value);
        if (preg_match('/^[+-]?\d+(_\d+)*$/', $trimmed)) {
            return (int) str_replace('_', '', $trimmed);
        }
        $this->add('int_parsing', [$where, $name], 'Input should be a valid integer, unable to parse string as an integer', $value);

        return null;
    }

    /** Required query string parameter typed `str`. */
    public function queryStr(Request $request, string $name): ?string
    {
        $value = self::queryParam($request, $name);
        if ($value === null) {
            $this->add('missing', ['query', $name], 'Field required', null);
        }

        return $value;
    }

    /** Last value of a query parameter (Starlette semantics), raw. */
    public static function queryParam(Request $request, string $name): ?string
    {
        $qs = (string) $request->server('QUERY_STRING', '');
        $found = null;
        foreach ($qs === '' ? [] : explode('&', $qs) as $pair) {
            $kv = explode('=', $pair, 2);
            if (urldecode($kv[0]) === $name) {
                $found = urldecode($kv[1] ?? '');
            }
        }

        return $found;
    }

    // ---------------------------------------------------------------- body

    /**
     * Parse a JSON body for a single Pydantic model parameter.
     * Returns the decoded object (stdClass) or null after recording an error.
     */
    public function bodyObject(Request $request): ?stdClass
    {
        $raw = $request->getContent();
        if ($raw === '') {
            $this->add('missing', ['body'], 'Field required', null);

            return null;
        }
        $ct = strtolower((string) $request->headers->get('content-type', ''));
        $mime = trim(explode(';', $ct)[0]);
        $isJson = $ct === '' || $mime === 'application/json' || (str_starts_with($mime, 'application/') && str_ends_with($mime, '+json'));
        if (! $isJson) {
            $this->add('model_attributes_type', ['body'], 'Input should be a valid dictionary or object to extract fields from', new RawRepr(self::bytesRepr($raw)));

            return null;
        }
        $decoded = json_decode($raw, false, 512, JSON_BIGINT_AS_STRING);
        if (json_last_error() !== JSON_ERROR_NONE) {
            // FastAPI reports json_invalid immediately (no other errors).
            $this->errors = [];
            $this->add('json_invalid', ['body', 0], 'JSON decode error', new stdClass, ['error' => 'Expecting value']);
            $this->done();
        }
        if (! $decoded instanceof stdClass) {
            $this->add('model_attributes_type', ['body'], 'Input should be a valid dictionary or object to extract fields from', $decoded);

            return null;
        }

        return $decoded;
    }

    /**
     * Validate fields of a model body. Spec per field (in model field order):
     *   name (python name), alias (camel), type: str|bool|float|uuid4|enum,
     *   required(bool), default, nullable(bool), lower/strip (bool), min_length(int), enum(list)
     * Returns [name => value] or null when any field failed.
     */
    public function fields(?stdClass $body, array $specs): ?array
    {
        if ($body === null) {
            return null;
        }
        $out = [];
        $ok = true;
        foreach ($specs as $spec) {
            $name = $spec['name'];
            $alias = $spec['alias'] ?? $name;
            $loc = ['body', $alias];
            if (property_exists($body, $alias)) {
                $value = $body->{$alias};
            } elseif (property_exists($body, $name)) {
                $value = $body->{$name};
            } else {
                if ($spec['required'] ?? false) {
                    $this->add('missing', $loc, 'Field required', $body);
                    $ok = false;
                } else {
                    $out[$name] = $spec['default'] ?? null;
                }

                continue;
            }
            if ($value === null && ($spec['nullable'] ?? false)) {
                $out[$name] = null;

                continue;
            }
            $result = $this->coerce($spec, $loc, $value);
            if ($result instanceof Invalid) {
                $ok = false;

                continue;
            }
            $out[$name] = $result;
        }

        return $ok ? $out : null;
    }

    private function coerce(array $spec, array $loc, mixed $value): mixed
    {
        switch ($spec['type']) {
            case 'str':
                if (! is_string($value)) {
                    $this->add('string_type', $loc, 'Input should be a valid string', $value);

                    return new Invalid;
                }
                if ($spec['strip'] ?? false) {
                    $value = trim($value, " \t\n\r\x0B\f");
                }
                if ($spec['lower'] ?? false) {
                    $value = mb_strtolower($value);
                }
                if (isset($spec['min_length']) && mb_strlen($value) < $spec['min_length']) {
                    $n = $spec['min_length'];
                    $this->add('string_too_short', $loc, "String should have at least {$n} character".($n === 1 ? '' : 's'), $value, ['min_length' => $n]);

                    return new Invalid;
                }

                return $value;
            case 'bool':
                $b = self::toBool($value);
                if ($b === null) {
                    if (is_string($value) || is_int($value) || is_float($value)) {
                        $this->add('bool_parsing', $loc, 'Input should be a valid boolean, unable to interpret input', $value);
                    } else {
                        $this->add('bool_type', $loc, 'Input should be a valid boolean', $value);
                    }

                    return new Invalid;
                }

                return $b;
            case 'float':
                if (is_bool($value)) {
                    return $value ? 1.0 : 0.0;
                }
                if (is_int($value) || is_float($value)) {
                    return (float) $value;
                }
                if (is_string($value)) {
                    $t = trim($value);
                    if (is_numeric($t)) {
                        return (float) $t;
                    }
                    $this->add('float_parsing', $loc, 'Input should be a valid number, unable to parse string as a number', $value);

                    return new Invalid;
                }
                $this->add('float_type', $loc, 'Input should be a valid number', $value);

                return new Invalid;
            case 'uuid4':
                $hex = $this->uuidAt($loc, $value, 4);

                return $hex === null ? new Invalid : $hex;
            case 'enum':
                if (is_string($value) && in_array($value, $spec['enum'], true)) {
                    return $value;
                }
                $quoted = array_map(fn ($e) => "'{$e}'", $spec['enum']);
                $expected = count($quoted) > 1
                    ? implode(', ', array_slice($quoted, 0, -1)).' or '.end($quoted)
                    : $quoted[0];
                $this->add('enum', $loc, 'Input should be '.$expected, $value, ['expected' => $expected]);

                return new Invalid;
        }

        return $value;
    }

    /** Pydantic lax bool. */
    public static function toBool(mixed $value): ?bool
    {
        if (is_bool($value)) {
            return $value;
        }
        if (is_int($value) || is_float($value)) {
            if ($value == 0) {
                return false;
            }
            if ($value == 1) {
                return true;
            }

            return null;
        }
        if (is_string($value)) {
            $v = strtolower(trim($value));
            if (in_array($v, ['0', 'off', 'f', 'false', 'n', 'no'], true)) {
                return false;
            }
            if (in_array($v, ['1', 'on', 't', 'true', 'y', 'yes'], true)) {
                return true;
            }
        }

        return null;
    }

    // ---------------------------------------------------------------- python repr

    public static function locRepr(array $loc): string
    {
        $items = array_map(fn ($p) => self::repr($p), $loc);

        return '('.implode(', ', $items).(count($items) === 1 ? ',' : '').')';
    }

    public static function repr(mixed $v): string
    {
        if ($v instanceof RawRepr) {
            return $v->text;
        }
        if ($v === null) {
            return 'None';
        }
        if ($v === true) {
            return 'True';
        }
        if ($v === false) {
            return 'False';
        }
        if (is_int($v)) {
            return (string) $v;
        }
        if (is_float($v)) {
            if (is_nan($v)) {
                return 'nan';
            }
            if (is_infinite($v)) {
                return $v > 0 ? 'inf' : '-inf';
            }
            if ($v == floor($v) && abs($v) < 1e16) {
                return number_format($v, 1, '.', '');
            }
            $s = var_export($v, true);
            if (preg_match('/^(-?[\d.]+)E([+-])(\d+)$/i', $s, $m)) {
                return $m[1].'e'.$m[2].str_pad($m[3], 2, '0', STR_PAD_LEFT);
            }

            return $s;
        }
        if (is_string($v)) {
            return self::strRepr($v);
        }
        if ($v instanceof stdClass) {
            $items = [];
            foreach (get_object_vars($v) as $k => $val) {
                $items[] = self::strRepr((string) $k).': '.self::repr($val);
            }

            return '{'.implode(', ', $items).'}';
        }
        if (is_array($v)) {
            if (array_is_list($v)) {
                return '['.implode(', ', array_map(fn ($x) => self::repr($x), $v)).']';
            }
            $items = [];
            foreach ($v as $k => $val) {
                $items[] = self::repr($k).': '.self::repr($val);
            }

            return '{'.implode(', ', $items).'}';
        }

        return (string) $v;
    }

    public static function strRepr(string $s): string
    {
        $quote = (str_contains($s, "'") && ! str_contains($s, '"')) ? '"' : "'";
        $out = '';
        $chars = preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY);
        if ($chars === false) {
            $chars = str_split($s);
        }
        foreach ($chars as $c) {
            $out .= match (true) {
                $c === '\\' => '\\\\',
                $c === $quote => '\\'.$quote,
                $c === "\n" => '\\n',
                $c === "\r" => '\\r',
                $c === "\t" => '\\t',
                strlen($c) === 1 && (ord($c) < 0x20 || ord($c) === 0x7F) => sprintf('\\x%02x', ord($c)),
                default => $c,
            };
        }

        return $quote.$out.$quote;
    }

    private static function bytesRepr(string $raw): string
    {
        $quote = (str_contains($raw, "'") && ! str_contains($raw, '"')) ? '"' : "'";
        $out = '';
        foreach (str_split($raw) as $c) {
            $o = ord($c);
            $out .= match (true) {
                $c === '\\' => '\\\\',
                $c === $quote => '\\'.$quote,
                $c === "\n" => '\\n',
                $c === "\r" => '\\r',
                $c === "\t" => '\\t',
                $o < 0x20 || $o >= 0x7F => sprintf('\\x%02x', $o),
                default => $c,
            };
        }

        return 'b'.$quote.$out.$quote;
    }
}
