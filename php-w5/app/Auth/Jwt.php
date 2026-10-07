<?php

namespace App\Auth;

use RuntimeException;

/**
 * HS256 JWT compatible with mealie/core/security (PyJWT, ALGORITHM = "HS256").
 * compx574/hurl/run.sh calls encode() and secret() directly: keep both signatures.
 */
class Jwt
{
    public static function encode(array $claims, string $secret): string
    {
        $header = self::url(json_encode(['alg' => 'HS256', 'typ' => 'JWT']));
        $payload = self::url(json_encode($claims, JSON_UNESCAPED_SLASHES));
        $signature = self::url(hash_hmac('sha256', $header.'.'.$payload, $secret, true));

        return $header.'.'.$payload.'.'.$signature;
    }

    /** Returns the claims, or null when the signature, algorithm or exp is invalid. */
    public static function decode(string $token, string $secret): ?array
    {
        $parts = explode('.', $token);
        if (count($parts) !== 3) {
            return null;
        }
        [$header, $payload, $signature] = $parts;

        $head = json_decode((string) self::urlDecode($header), true);
        if (! is_array($head) || ($head['alg'] ?? null) !== 'HS256') {
            return null;
        }

        $expected = self::url(hash_hmac('sha256', $header.'.'.$payload, $secret, true));
        if (! hash_equals($expected, $signature)) {
            return null;
        }

        $claims = json_decode((string) self::urlDecode($payload), true);
        if (! is_array($claims)) {
            return null;
        }
        if (isset($claims['exp']) && is_numeric($claims['exp']) && $claims['exp'] < time()) {
            return null;
        }

        return $claims;
    }

    /** Same rule as mealie/core/settings/settings.py determine_secrets(). */
    public static function secret(): string
    {
        $configured = config('mealie.secret');
        if (is_string($configured) && $configured !== '') {
            return $configured;
        }

        if (! config('mealie.production')) {
            return 'shh-secret-test-key';
        }

        $path = rtrim((string) config('mealie.data_dir'), '/').'/.secret';
        if (is_file($path)) {
            $secret = trim((string) file_get_contents($path));
            if ($secret !== '') {
                return $secret;
            }
        }

        throw new RuntimeException('Mealie signing secret is not configured.');
    }

    private static function url(string $value): string
    {
        return rtrim(strtr(base64_encode($value), '+/', '-_'), '=');
    }

    private static function urlDecode(string $value): ?string
    {
        $decoded = base64_decode(strtr($value, '-_', '+/'), true);

        return $decoded === false ? null : $decoded;
    }
}
