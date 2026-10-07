<?php

namespace App\Areas\Recipes\Support;

use App\Support\Guid;

/** Output helpers for values read from SQLite. */
class Out
{
    /** Pydantic datetime with UTC tz: "2026-08-05T12:50:26.067976Z", no fraction when it is zero. */
    public static function dt(?string $value, string $suffix = 'Z'): ?string
    {
        if ($value === null || $value === '') {
            return null;
        }
        $value = str_replace(' ', 'T', $value);
        $value = preg_replace('/(Z|[+-]\d{2}:?\d{2})$/', '', $value);
        $value = preg_replace('/\.0+$/', '', $value);

        return $value.$suffix;
    }

    /** orjson datetime (used where Python bypasses Pydantic serialisation). */
    public static function dtOrjson(?string $value): ?string
    {
        return self::dt($value, '+00:00');
    }

    public static function id(?string $value): ?string
    {
        return Guid::fromDb($value);
    }

    public static function bool(mixed $value): ?bool
    {
        return $value === null ? null : (bool) $value;
    }

    public static function float(mixed $value): ?float
    {
        return $value === null ? null : (float) $value;
    }
}
