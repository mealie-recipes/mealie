<?php

namespace App\Support;

/**
 * Mealie's GUID column type (mealie/db/models/_model_utils/guid.py):
 * SQLite stores CHAR(32) lowercase hex without dashes; the API returns dashed UUIDs.
 */
class Guid
{
    /** Dashed or plain UUID string -> 32-char hex for SQLite WHERE clauses. Null if not a UUID. */
    public static function toDb(?string $value): ?string
    {
        if ($value === null) {
            return null;
        }
        $hex = strtolower(str_replace(['-', '{', '}'], '', trim($value)));

        return preg_match('/^[0-9a-f]{32}$/', $hex) ? $hex : null;
    }

    /** 32-char hex from SQLite -> dashed lowercase UUID for JSON. */
    public static function fromDb(?string $value): ?string
    {
        if ($value === null || $value === '') {
            return null;
        }
        $hex = self::toDb($value);
        if ($hex === null) {
            return $value;
        }

        return substr($hex, 0, 8).'-'.substr($hex, 8, 4).'-'.substr($hex, 12, 4).'-'.substr($hex, 16, 4).'-'.substr($hex, 20, 12);
    }

    public static function isUuid(?string $value): bool
    {
        return self::toDb($value) !== null;
    }

    /** Pydantic UUID4 also checks the version nibble; 00000000-... fails with 422. */
    public static function isUuid4(?string $value): bool
    {
        $hex = self::toDb($value);

        return $hex !== null && $hex[12] === '4';
    }

    /**
     * Validate a path/query/body value declared as UUID4 in the Python route and return its DB form.
     * Fails the request with FastAPI's 422 shape otherwise.
     */
    public static function requireUuid4(?string $value, string $loc = 'path'): string
    {
        if (! self::isUuid4($value)) {
            Errors::validation("UUID version 4 expected at {$loc}");
        }

        return self::toDb($value);
    }

    /** Same, for routes declared as plain UUID (no version check). */
    public static function requireUuid(?string $value, string $loc = 'path'): string
    {
        if (! self::isUuid($value)) {
            Errors::validation("Input should be a valid UUID at {$loc}");
        }

        return self::toDb($value);
    }

    public static function new(): string
    {
        return str_replace('-', '', (string) \Illuminate\Support\Str::uuid());
    }
}
