<?php

namespace App\Support;

/**
 * SQLite stores naive UTC like "2026-08-06 13:35:24.307376".
 * MealieModel.set_tz_info marks datetimes as UTC, so the API returns "2026-08-06T13:35:24.307376Z".
 */
class Dates
{
    public static function out(?string $value): ?string
    {
        if ($value === null || $value === '') {
            return null;
        }
        $value = str_replace(' ', 'T', $value);
        if (preg_match('/(Z|[+-]\d{2}:?\d{2})$/', $value)) {
            return $value;
        }

        return $value.'Z';
    }

    /** Pydantic `date` fields: "2026-08-06". */
    public static function date(?string $value): ?string
    {
        return $value === null || $value === '' ? null : substr($value, 0, 10);
    }

    /** Current UTC time in the stored format. */
    public static function nowDb(): string
    {
        return (new \DateTimeImmutable('now', new \DateTimeZone('UTC')))->format('Y-m-d H:i:s.u');
    }
}
