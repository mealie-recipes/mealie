<?php

namespace App\Areas\Households\Support;

use App\Support\Errors;
use App\Support\Guid;

/** HttpRepo (mealie/routes/_base/mixins.py) error bodies and small shared helpers for this area. */
class Http
{
    /** HttpRepo.delete_one when the row is missing: NoResultFound -> 404 with the generic message. */
    public static function deleteNotFound(string $message = 'An unexpected error occurred'): never
    {
        Errors::http(404, ['message' => $message, 'error' => true, 'exception' => 'No row was found when one was required']);
    }

    /** Python int(...) / float(...) formatting for nullable floats (JSON_PRESERVE_ZERO_FRACTION does the rest). */
    public static function float(mixed $v): ?float
    {
        return $v === null ? null : (float) $v;
    }

    public static function bool(mixed $v): ?bool
    {
        return $v === null ? null : (bool) $v;
    }

    public static function id(?string $hex): ?string
    {
        return Guid::fromDb($hex);
    }

    /** secrets.token_urlsafe(n) */
    public static function urlSafeToken(int $bytes = 24): string
    {
        return rtrim(strtr(base64_encode(random_bytes($bytes)), '+/', '-_'), '=');
    }
}
