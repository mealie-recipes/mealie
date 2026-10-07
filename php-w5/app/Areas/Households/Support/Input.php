<?php

namespace App\Areas\Households\Support;

use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/**
 * Minimal Pydantic-like field parsing for request bodies (MealieModel: camelCase alias or snake_case name).
 * Errors are FastAPI dev-mode 422 bodies; the message text is shorter than Python's.
 */
class Input
{
    public const MISSING = "\0missing";

    public static function object(Request $request): array
    {
        return Json::body($request);
    }

    /** Body declared as list[Model]: must be a JSON array of objects. */
    public static function listOfObjects(Request $request): array
    {
        $raw = $request->getContent();
        $decoded = json_decode($raw === '' ? 'null' : $raw, true);
        if (! is_array($decoded) || ! array_is_list($decoded)) {
            Errors::validation('Input should be a valid list at body');
        }
        foreach ($decoded as $i => $item) {
            if (! is_array($item) || (array_is_list($item) && $item !== [])) {
                Errors::validation("Input should be a valid dictionary or object to extract fields from at body.{$i}");
            }
        }

        return $decoded;
    }

    /** Optional body (`Model | None = None`): empty body -> null. */
    public static function optionalObject(Request $request): ?array
    {
        $raw = $request->getContent();
        if ($raw === '') {
            return null;
        }
        $decoded = json_decode($raw, true);
        if ($decoded === null) {
            return null;
        }

        return Json::body($request);
    }

    public static function raw(array $data, string $name): mixed
    {
        $camel = Json::camel($name);
        if (array_key_exists($camel, $data)) {
            return $data[$camel];
        }
        if (array_key_exists($name, $data)) {
            return $data[$name];
        }

        return self::MISSING;
    }

    private static function fail(string $loc, string $msg): never
    {
        Errors::validation("{$msg} at body.{$loc}");
    }

    private static function missing(string $loc): never
    {
        self::fail($loc, 'Field required');
    }

    public static function str(array $data, string $name, mixed $default = self::MISSING, bool $nullable = false): ?string
    {
        $v = self::raw($data, $name);
        if ($v === self::MISSING) {
            if ($default === self::MISSING) {
                self::missing($name);
            }

            return $default;
        }
        if ($v === null && $nullable) {
            return null;
        }
        if (! is_string($v)) {
            self::fail($name, 'Input should be a valid string');
        }

        return $v;
    }

    public static function bool(array $data, string $name, mixed $default = self::MISSING, bool $nullable = false): ?bool
    {
        $v = self::raw($data, $name);
        if ($v === self::MISSING) {
            if ($default === self::MISSING) {
                self::missing($name);
            }

            return $default;
        }
        if ($v === null && $nullable) {
            return null;
        }
        $b = self::toBool($v);
        if ($b === null) {
            self::fail($name, 'Input should be a valid boolean');
        }

        return $b;
    }

    public static function toBool(mixed $v): ?bool
    {
        if (is_bool($v)) {
            return $v;
        }
        if (is_int($v) || is_float($v)) {
            return $v == 1 ? true : ($v == 0 ? false : null);
        }
        if (is_string($v)) {
            $s = strtolower($v);
            if (in_array($s, ['1', 'on', 't', 'true', 'y', 'yes'], true)) {
                return true;
            }
            if (in_array($s, ['0', 'off', 'f', 'false', 'n', 'no'], true)) {
                return false;
            }
        }

        return null;
    }

    public static function int(array $data, string $name, mixed $default = self::MISSING): ?int
    {
        $v = self::raw($data, $name);
        if ($v === self::MISSING) {
            if ($default === self::MISSING) {
                self::missing($name);
            }

            return $default;
        }
        $i = self::toInt($v);
        if ($i === null) {
            self::fail($name, 'Input should be a valid integer');
        }

        return $i;
    }

    public static function toInt(mixed $v): ?int
    {
        if (is_bool($v)) {
            return null;
        }
        if (is_int($v)) {
            return $v;
        }
        if (is_float($v) && floor($v) == $v) {
            return (int) $v;
        }
        if (is_string($v) && preg_match('/^\s*[+-]?\d+\s*$/', $v)) {
            return (int) $v;
        }

        return null;
    }

    public static function float(array $data, string $name, mixed $default = self::MISSING): ?float
    {
        $v = self::raw($data, $name);
        if ($v === self::MISSING) {
            if ($default === self::MISSING) {
                self::missing($name);
            }

            return $default;
        }
        if (is_bool($v) || ! (is_int($v) || is_float($v) || (is_string($v) && is_numeric(trim($v))))) {
            self::fail($name, 'Input should be a valid number');
        }

        return (float) $v;
    }

    /** @param  string[]  $allowed */
    public static function enum(array $data, string $name, array $allowed, mixed $default = self::MISSING): ?string
    {
        $v = self::raw($data, $name);
        if ($v === self::MISSING) {
            if ($default === self::MISSING) {
                self::missing($name);
            }

            return $default;
        }
        if (! is_string($v) || ! in_array($v, $allowed, true)) {
            self::fail($name, 'Input should be '.implode(', ', array_map(fn ($a) => "'{$a}'", $allowed)));
        }

        return $v;
    }

    /** UUID field -> 32-char hex. $v4 enforces the version nibble like Pydantic UUID4. */
    public static function uuid(array $data, string $name, bool $v4 = true, mixed $default = self::MISSING, bool $nullable = false): ?string
    {
        $v = self::raw($data, $name);
        if ($v === self::MISSING) {
            if ($default === self::MISSING) {
                self::missing($name);
            }

            return $default;
        }
        if ($v === null && $nullable) {
            return null;
        }
        if (! is_string($v) || ! Guid::isUuid($v)) {
            self::fail($name, 'Input should be a valid UUID');
        }
        if ($v4 && ! Guid::isUuid4($v)) {
            self::fail($name, 'UUID version 4 expected');
        }

        return Guid::toDb($v);
    }

    /** Pydantic `date`: "YYYY-MM-DD" (or a datetime string at midnight). */
    public static function date(array $data, string $name, mixed $default = self::MISSING): ?string
    {
        $v = self::raw($data, $name);
        if ($v === self::MISSING) {
            if ($default === self::MISSING) {
                self::missing($name);
            }

            return $default;
        }
        $d = is_string($v) ? self::parseDate($v) : null;
        if ($d === null) {
            self::fail($name, 'Input should be a valid date');
        }

        return $d;
    }

    public static function parseDate(string $v): ?string
    {
        if (! preg_match('/^(\d{4})-(\d{2})-(\d{2})$/', $v, $m) || ! checkdate((int) $m[2], (int) $m[3], (int) $m[1])) {
            return null;
        }

        return $v;
    }

    /** Integer path parameter (FastAPI `int`). */
    public static function pathInt(string $value, string $name = 'item_id'): int
    {
        $i = self::toInt($value);
        if ($i === null) {
            Errors::validation("Input should be a valid integer, unable to parse string as an integer at path.{$name}");
        }

        return $i;
    }
}
