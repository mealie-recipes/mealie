<?php

namespace App\Areas\GroupsAdmin\Support;

use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/**
 * Minimal Pydantic (lax mode) field validation for request bodies and query strings.
 * Errors are collected and reported in one dev-mode 422 body, like RequestValidationError.
 * Keys are looked up by camelCase alias first, then by field name (populate_by_name=True).
 */
class Validator
{
    /** @var list<array{type:string, loc:list<string>, msg:string}> */
    private array $errors = [];

    public function __construct(private array $data, private array $prefix = ['body']) {}

    /** Request body that must be a JSON object (Pydantic model param). */
    public static function body(Request $request): self
    {
        return new self(Json::body($request));
    }

    public static function query(Request $request): self
    {
        return new self($request->query->all(), ['query']);
    }

    public function data(): array
    {
        return $this->data;
    }

    /** @return array{0: bool, 1: mixed} */
    public function raw(string $field): array
    {
        $camel = Json::camel($field);
        if (array_key_exists($camel, $this->data)) {
            return [true, $this->data[$camel]];
        }
        if (array_key_exists($field, $this->data)) {
            return [true, $this->data[$field]];
        }

        return [false, null];
    }

    public function has(string $field): bool
    {
        return $this->raw($field)[0];
    }

    public function error(string $field, string $type, string $msg): void
    {
        $this->errors[] = ['type' => $type, 'loc' => array_merge($this->prefix, [$this->locName($field)]), 'msg' => $msg];
    }

    private function locName(string $field): string
    {
        // Pydantic reports the alias for missing fields and the key that was used otherwise.
        $camel = Json::camel($field);

        return array_key_exists($field, $this->data) && ! array_key_exists($camel, $this->data) ? $field : $camel;
    }

    private function missing(string $field): void
    {
        $this->error($field, 'missing', 'Field required');
    }

    public function str(string $field, bool $required = true, ?string $default = null, bool $nullable = false, bool $strip = false, int $minLength = 0): ?string
    {
        [$found, $value] = $this->raw($field);
        if (! $found) {
            if ($required) {
                $this->missing($field);
            }

            return $default;
        }
        if ($value === null && $nullable) {
            return null;
        }
        if (! is_string($value)) {
            $this->error($field, 'string_type', 'Input should be a valid string');

            return $default;
        }
        if ($strip) {
            $value = trim($value);
        }
        if (mb_strlen($value) < $minLength) {
            $this->error($field, 'string_too_short', "String should have at least {$minLength} character".($minLength === 1 ? '' : 's'));
        }

        return $value;
    }

    public function bool(string $field, bool $required = false, ?bool $default = null, bool $nullable = false): ?bool
    {
        [$found, $value] = $this->raw($field);
        if (! $found) {
            if ($required) {
                $this->missing($field);
            }

            return $default;
        }
        if ($value === null && $nullable) {
            return null;
        }
        $parsed = self::parseBool($value);
        if ($parsed === null) {
            $this->error($field, 'bool_parsing', 'Input should be a valid boolean');

            return $default;
        }

        return $parsed;
    }

    public static function parseBool(mixed $value): ?bool
    {
        if (is_bool($value)) {
            return $value;
        }
        if (is_int($value) || is_float($value)) {
            return $value == 1 ? true : ($value == 0 ? false : null);
        }
        if (is_string($value)) {
            $v = strtolower(trim($value));
            if (in_array($v, ['1', 'on', 't', 'true', 'y', 'yes'], true)) {
                return true;
            }
            if (in_array($v, ['0', 'off', 'f', 'false', 'n', 'no'], true)) {
                return false;
            }
        }

        return null;
    }

    public function int(string $field, bool $required = false, ?int $default = null, bool $nullable = false): ?int
    {
        [$found, $value] = $this->raw($field);
        if (! $found) {
            if ($required) {
                $this->missing($field);
            }

            return $default;
        }
        if ($value === null && $nullable) {
            return null;
        }
        $parsed = self::parseInt($value);
        if ($parsed === null) {
            $this->error($field, 'int_parsing', 'Input should be a valid integer');

            return $default;
        }

        return $parsed;
    }

    public static function parseInt(mixed $value): ?int
    {
        if (is_int($value)) {
            return $value;
        }
        if (is_float($value) && floor($value) === $value) {
            return (int) $value;
        }
        if (is_string($value) && preg_match('/^\s*[+-]?\d+\s*$/', $value)) {
            return (int) trim($value);
        }

        return null;
    }

    /** UUID / UUID4 field; returns the 32-char DB form. */
    public function uuid(string $field, bool $required = true, bool $nullable = false, bool $v4 = true, bool $emptyAsNull = false): ?string
    {
        [$found, $value] = $this->raw($field);
        if (! $found) {
            if ($required) {
                $this->missing($field);
            }

            return null;
        }
        if ($emptyAsNull && ! $value) {
            return null;
        }
        if ($value === null && $nullable) {
            return null;
        }
        if (! is_string($value) || ! Guid::isUuid($value)) {
            $this->error($field, 'uuid_parsing', 'Input should be a valid UUID');

            return null;
        }
        if ($v4 && ! Guid::isUuid4($value)) {
            $this->error($field, 'uuid_version', 'UUID version 4 expected');

            return null;
        }

        return Guid::toDb($value);
    }

    /** dict[str, str] */
    public function strDict(string $field, array $default = []): array
    {
        [$found, $value] = $this->raw($field);
        if (! $found) {
            return $default;
        }
        if (! is_array($value) || (array_is_list($value) && $value !== [])) {
            $this->error($field, 'dict_type', 'Input should be a valid dictionary');

            return $default;
        }
        foreach ($value as $v) {
            if (! is_string($v)) {
                $this->error($field, 'string_type', 'Input should be a valid string');

                return $default;
            }
        }

        return $value;
    }

    /** Nested model (object) or null. */
    public function object(string $field, bool $required = false, bool $nullable = true): ?array
    {
        [$found, $value] = $this->raw($field);
        if (! $found) {
            if ($required) {
                $this->missing($field);
            }

            return null;
        }
        if ($value === null && $nullable) {
            return null;
        }
        if (! is_array($value) || (array_is_list($value) && $value !== [])) {
            $this->error($field, 'model_attributes_type', 'Input should be a valid dictionary or object to extract fields from');

            return null;
        }

        return $value;
    }

    public function enum(string $field, array $allowed, bool $required = false, ?string $default = null): ?string
    {
        [$found, $value] = $this->raw($field);
        if (! $found || ($value === null && ! $required)) {
            if (! $found && $required) {
                $this->missing($field);
            }

            return $default;
        }
        if (! is_string($value) || ! in_array($value, $allowed, true)) {
            $quoted = array_map(fn ($a) => "'{$a}'", $allowed);
            $last = array_pop($quoted);
            $this->error($field, 'enum', 'Input should be '.($quoted ? implode(', ', $quoted).' or '.$last : $last));

            return $default;
        }

        return $value;
    }

    /** Merge the errors of a nested validator (loc is prefixed with the parent field). */
    public function nested(string $field, array $data): self
    {
        return new self($data, array_merge($this->prefix, [Json::camel($field)]));
    }

    public function absorb(self $child): void
    {
        array_push($this->errors, ...$child->errors);
    }

    public function custom(string $field, string $msg): void
    {
        $this->error($field, 'value_error', 'Value error, '.$msg);
    }

    public function fails(): bool
    {
        return $this->errors !== [];
    }

    /** Abort with the dev-mode 422 body when anything failed. */
    public function check(): void
    {
        if (! $this->errors) {
            return;
        }
        $n = count($this->errors);
        $parts = array_map(function ($e) {
            $loc = "('".implode("', '", $e['loc'])."',)";
            if (count($e['loc']) > 1) {
                $loc = "('".implode("', '", $e['loc'])."')";
            }

            return "{'type': '{$e['type']}', 'loc': {$loc}, 'msg': '{$e['msg']}'}";
        }, $this->errors);

        Errors::validation($n.' validation error'.($n === 1 ? '' : 's').': '.implode(' ', $parts));
    }
}
