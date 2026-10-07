<?php

namespace App\Areas\Recipes\Support;

use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/**
 * Minimal Pydantic-style reader for a MealieModel request body.
 * Fields are looked up by camelCase alias first, then by snake_case name (populate_by_name=True).
 * Errors are collected and reported together in FastAPI's dev-mode 422 body.
 */
class Input
{
    private array $errors = [];

    public function __construct(public array $data, private string $loc = 'body') {}

    public static function fromRequest(Request $request): self
    {
        return new self(Json::body($request));
    }

    public function has(string $field): bool
    {
        return array_key_exists(Json::camel($field), $this->data) || array_key_exists($field, $this->data);
    }

    public function raw(string $field): mixed
    {
        $alias = Json::camel($field);
        if (array_key_exists($alias, $this->data)) {
            return $this->data[$alias];
        }

        return $this->data[$field] ?? null;
    }

    private function fail(string $field, string $type, string $msg): void
    {
        $this->errors[] = "{'type': '{$type}', 'loc': ('{$this->loc}', '".Json::camel($field)."'), 'msg': '{$msg}'}";
    }

    private function missing(string $field): void
    {
        $this->fail($field, 'missing', 'Field required');
    }

    public function str(string $field, bool $required = true, ?string $default = null, bool $nullable = false): ?string
    {
        if (! $this->has($field)) {
            if ($required) {
                $this->missing($field);
            }

            return $default;
        }
        $v = $this->raw($field);
        if ($v === null && $nullable) {
            return null;
        }
        if (! is_string($v)) {
            $this->fail($field, 'string_type', 'Input should be a valid string');

            return $default;
        }

        return $v;
    }

    public function uuid4(string $field, bool $required = true, bool $nullable = false): ?string
    {
        if (! $this->has($field)) {
            if ($required) {
                $this->missing($field);
            }

            return null;
        }
        $v = $this->raw($field);
        if ($v === null && $nullable) {
            return null;
        }
        if (! is_string($v) || ! Guid::isUuid($v)) {
            $this->fail($field, 'uuid_parsing', 'Input should be a valid UUID');

            return null;
        }
        if (! Guid::isUuid4($v)) {
            $this->fail($field, 'uuid_version', 'UUID version 4 expected');

            return null;
        }

        return Guid::toDb($v);
    }

    public function bool(string $field, bool $default, bool $nullable = false): ?bool
    {
        if (! $this->has($field)) {
            return $default;
        }
        $v = $this->raw($field);
        if ($v === null && $nullable) {
            return null;
        }
        if (is_bool($v)) {
            return $v;
        }
        if ($v === 0 || $v === 1) {
            return (bool) $v;
        }
        if (is_string($v)) {
            $l = strtolower($v);
            if (in_array($l, ['0', 'off', 'f', 'false', 'n', 'no'], true)) {
                return false;
            }
            if (in_array($l, ['1', 'on', 't', 'true', 'y', 'yes'], true)) {
                return true;
            }
        }
        $this->fail($field, 'bool_parsing', 'Input should be a valid boolean');

        return $default;
    }

    public function float(string $field, ?float $default, bool $nullable = true): ?float
    {
        if (! $this->has($field)) {
            return $default;
        }
        $v = $this->raw($field);
        if ($v === null && $nullable) {
            return null;
        }
        if (is_int($v) || is_float($v)) {
            return (float) $v;
        }
        if (is_string($v) && is_numeric(trim($v))) {
            return (float) trim($v);
        }
        $this->fail($field, 'float_parsing', 'Input should be a valid number');

        return $default;
    }

    /** list of strings, e.g. householdsWithTool */
    public function strList(string $field): array
    {
        if (! $this->has($field)) {
            return [];
        }
        $v = $this->raw($field);
        if (! is_array($v) || ! array_is_list($v)) {
            $this->fail($field, 'list_type', 'Input should be a valid list');

            return [];
        }
        foreach ($v as $item) {
            if (! is_string($item)) {
                $this->fail($field, 'string_type', 'Input should be a valid string');

                return [];
            }
        }

        return $v;
    }

    /** list of objects; returns raw arrays */
    public function objList(string $field): array
    {
        if (! $this->has($field)) {
            return [];
        }
        $v = $this->raw($field);
        if ($v === null) {
            $this->fail($field, 'list_type', 'Input should be a valid list');

            return [];
        }
        if (! is_array($v) || ! array_is_list($v)) {
            $this->fail($field, 'list_type', 'Input should be a valid list');

            return [];
        }
        foreach ($v as $item) {
            if (! is_array($item) || (array_is_list($item) && $item !== [])) {
                $this->fail($field, 'model_type', 'Input should be a valid dictionary or instance');

                return [];
            }
        }

        return $v;
    }

    public function error(string $field, string $type, string $msg): void
    {
        $this->fail($field, $type, $msg);
    }

    /** Throw the collected 422, if any. */
    public function check(): void
    {
        if ($this->errors === []) {
            return;
        }
        $n = count($this->errors);
        $head = $n === 1 ? '1 validation error: ' : "{$n} validation errors: ";
        Errors::validation($head.implode(' ', $this->errors));
    }

    /** Path/query param declared UUID4 in Python. */
    public static function pathUuid4(string $value, string $name = 'item_id'): string
    {
        if (! Guid::isUuid($value)) {
            Errors::validation("1 validation error: {'type': 'uuid_parsing', 'loc': ('path', '{$name}'), 'msg': 'Input should be a valid UUID', 'input': '{$value}'}");
        }
        if (! Guid::isUuid4($value)) {
            Errors::validation("1 validation error: {'type': 'uuid_version', 'loc': ('path', '{$name}'), 'msg': 'UUID version 4 expected', 'input': '{$value}'}");
        }

        return Guid::toDb($value);
    }
}
