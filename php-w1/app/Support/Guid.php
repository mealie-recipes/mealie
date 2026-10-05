<?php

namespace App\Support;

final class Guid
{
    public static function hex(?string $value): ?string
    {
        if ($value === null || $value === '') {
            return null;
        }

        $hex = strtolower(str_replace('-', '', $value));

        return strlen($hex) === 32 && ctype_xdigit($hex) ? $hex : null;
    }

    public static function dashed(?string $value): ?string
    {
        $hex = self::hex($value);
        if ($hex === null) {
            return $value === null || $value === '' ? null : $value;
        }

        return sprintf(
            '%s-%s-%s-%s-%s',
            substr($hex, 0, 8),
            substr($hex, 8, 4),
            substr($hex, 12, 4),
            substr($hex, 16, 4),
            substr($hex, 20, 12),
        );
    }

    public static function newHex(): string
    {
        return bin2hex(random_bytes(16));
    }
}
