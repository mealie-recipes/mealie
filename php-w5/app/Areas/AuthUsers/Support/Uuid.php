<?php

namespace App\Areas\AuthUsers\Support;

/**
 * UUID parsing as pydantic-core does it (uuid-rs `Uuid::parse_str`), with uuid-rs error texts,
 * plus Python's `uuid.UUID(str)` acceptance used for slug-or-id lookups.
 */
class Uuid
{
    /** @return array{0: ?string, 1: ?string} [32-hex lowercase, error text] */
    public static function parse(string $s): array
    {
        $len = strlen($s);
        $body = null;
        if ($len === 32) {
            $body = $s;
            $simple = true;
        } elseif ($len === 36) {
            $body = $s;
            $simple = false;
        } elseif ($len === 38 && $s[0] === '{' && $s[37] === '}') {
            $body = substr($s, 1, 36);
            $simple = false;
        } elseif ($len === 45 && str_starts_with($s, 'urn:uuid:')) {
            $body = substr($s, 9);
            $simple = false;
        }
        if ($body !== null) {
            if ($simple && preg_match('/^[0-9a-fA-F]{32}$/', $body)) {
                return [strtolower($body), null];
            }
            if (! $simple && preg_match('/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/', $body)) {
                return [strtolower(str_replace('-', '', $body)), null];
            }
        }

        return [null, self::error($s)];
    }

    /** uuid-rs InvalidUuid::into_err. */
    private static function error(string $input): string
    {
        if (strlen($input) >= 2 && $input[0] === '{' && $input[strlen($input) - 1] === '}') {
            $str = substr($input, 1, -1);
            $offset = 1;
            $simple = false;
        } elseif (str_starts_with($input, 'urn:uuid:')) {
            $str = substr($input, 9);
            $offset = 9;
            $simple = false;
        } else {
            $str = $input;
            $offset = 0;
            $simple = true;
        }

        $hyphens = 0;
        $bounds = [0, 0, 0, 0];
        $len = strlen($str);
        for ($i = 0; $i < $len; $i++) {
            $byte = $str[$i];
            $ord = ord($byte);
            if ($ord >= 0x80) {
                // multibyte char: report the whole character
                preg_match('/./us', substr($str, $i), $m);
                $char = $m[0] ?? $byte;

                return 'invalid character: found `'.$char.'` at '.($i + $offset + 1);
            }
            if ($byte === '-') {
                if ($hyphens < 4) {
                    $bounds[$hyphens] = $i;
                }
                $hyphens++;
            } elseif (! ctype_xdigit($byte)) {
                return 'invalid character: found `'.$byte.'` at '.($i + $offset + 1);
            }
        }

        if ($hyphens === 0 && $simple) {
            return 'invalid length: expected length 32 for simple format, found '.strlen($input);
        }
        if ($hyphens !== 4) {
            return 'invalid group count: expected 5, found '.($hyphens + 1);
        }
        $starts = [0, 9, 14, 19, 24];
        $expected = [8, 4, 4, 4, 12];
        for ($g = 0; $g < 4; $g++) {
            if ($bounds[$g] !== $starts[$g + 1] - 1) {
                return "invalid group length in group {$g}: expected {$expected[$g]}, found ".($bounds[$g] - $starts[$g]);
            }
        }

        return 'invalid group length in group 4: expected 12, found '.(strlen($input) - $starts[4]);
    }

    /** Python `uuid.UUID(value)`: returns 32-hex or null on ValueError. */
    public static function python(string $value): ?string
    {
        $hex = str_replace(['urn:', 'uuid:'], '', $value);
        $hex = trim($hex, '{}');
        $hex = str_replace('-', '', $hex);
        if (strlen($hex) !== 32 || ! preg_match('/^[0-9a-fA-F]{32}$/', $hex)) {
            return null;
        }

        return strtolower($hex);
    }
}
