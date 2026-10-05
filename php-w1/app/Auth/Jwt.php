<?php

namespace App\Auth;

use RuntimeException;

final class Jwt
{
    /**
     * @param  array<string, mixed>  $claims
     */
    public static function encode(array $claims, string $secret): string
    {
        $header = self::url(json_encode(['typ' => 'JWT', 'alg' => 'HS256'], JSON_THROW_ON_ERROR));
        $payload = self::url(json_encode($claims, JSON_THROW_ON_ERROR));
        $signature = self::url(hash_hmac('sha256', $header.'.'.$payload, $secret, true));

        return $header.'.'.$payload.'.'.$signature;
    }

    /**
     * @return array<string, mixed>|null
     */
    public static function decode(string $token, string $secret): ?array
    {
        $parts = explode('.', $token);
        if (count($parts) !== 3) {
            return null;
        }

        $expected = self::url(hash_hmac('sha256', $parts[0].'.'.$parts[1], $secret, true));
        if (! hash_equals($expected, $parts[2])) {
            return null;
        }

        $json = self::urlDecode($parts[1]);
        if ($json === null) {
            return null;
        }

        /** @var array<string, mixed>|null $claims */
        $claims = json_decode($json, true);
        if (! is_array($claims)) {
            return null;
        }

        if (isset($claims['exp']) && time() >= (int) $claims['exp']) {
            return null;
        }

        return $claims;
    }

    public static function secret(): string
    {
        $configured = config('mealie.secret');
        if (is_string($configured) && $configured !== '') {
            return $configured;
        }

        if (! config('mealie.production')) {
            return 'shh-secret-test-key';
        }

        $path = (string) config('mealie.secret_file');
        if (is_readable($path)) {
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
        $padded = strtr($value, '-_', '+/');
        $pad = strlen($padded) % 4;
        if ($pad > 0) {
            $padded .= str_repeat('=', 4 - $pad);
        }

        $decoded = base64_decode($padded, true);

        return $decoded === false ? null : $decoded;
    }
}
