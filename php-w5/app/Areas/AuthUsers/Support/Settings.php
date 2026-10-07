<?php

namespace App\Areas\AuthUsers\Support;

/**
 * The parts of mealie/core/settings/settings.py AppSettings this area needs,
 * read from the environment with the Python defaults.
 */
class Settings
{
    public static function str(string $key, ?string $default = null): ?string
    {
        $v = getenv($key);
        if ($v === false) {
            $v = $_ENV[$key] ?? $_SERVER[$key] ?? null;
        }

        return is_string($v) ? $v : $default;
    }

    public static function bool(string $key, bool $default): bool
    {
        $v = self::str($key);
        if ($v === null) {
            return $default;
        }

        return Pyd::toBool($v) ?? $default;
    }

    public static function int(string $key, int $default): int
    {
        $v = self::str($key);

        return $v !== null && is_numeric(trim($v)) ? (int) trim($v) : $default;
    }

    public static function production(): bool
    {
        return (bool) config('mealie.production');
    }

    public static function allowSignup(): bool
    {
        return self::bool('ALLOW_SIGNUP', false);
    }

    public static function allowPasswordLogin(): bool
    {
        return self::bool('ALLOW_PASSWORD_LOGIN', true);
    }

    public static function isDemo(): bool
    {
        return self::bool('IS_DEMO', false);
    }

    /** Hours; validate_token_time caps at 400 days. */
    public static function tokenTime(): int
    {
        return min(self::int('TOKEN_TIME', 48), 400 * 24);
    }

    public static function defaultGroup(): string
    {
        return self::str('DEFAULT_GROUP', 'Home');
    }

    public static function defaultHousehold(): string
    {
        return self::str('DEFAULT_HOUSEHOLD', 'Family');
    }

    public static function maxLoginAttempts(): int
    {
        return self::int('SECURITY_MAX_LOGIN_ATTEMPTS', 5);
    }

    public static function lockoutHours(): int
    {
        return self::int('SECURITY_USER_LOCKOUT_TIME', 24);
    }

    public static function oidcReady(): bool
    {
        if (! self::bool('OIDC_AUTH_ENABLED', false)) {
            return false;
        }
        foreach (['OIDC_CLIENT_ID', 'OIDC_CLIENT_SECRET', 'OIDC_CONFIGURATION_URL'] as $key) {
            if (self::str($key) === null) {
                return false;
            }
        }
        $requiresGroup = self::str('OIDC_USER_GROUP') !== null || self::str('OIDC_ADMIN_GROUP') !== null;

        return ! ($requiresGroup && self::str('OIDC_GROUPS_CLAIM', 'groups') === null);
    }

    public static function ldapEnabled(): bool
    {
        return self::bool('LDAP_AUTH_ENABLED', false) && self::str('LDAP_SERVER_URL') !== null && self::str('LDAP_BASE_DN') !== null;
    }

    /** @return list<string> */
    public static function allowedIframeHosts(): array
    {
        $hosts = ['youtube.com', 'youtube-nocookie.com', 'vimeo.com', 'player.vimeo.com'];
        foreach (explode(',', self::str('ALLOWED_IFRAME_HOSTS', '')) as $h) {
            $h = strtolower(trim($h));
            if ($h !== '' && ! in_array($h, $hosts, true)) {
                $hosts[] = $h;
            }
        }

        return $hosts;
    }

    /** @return array<string, string> AppTheme in field order */
    public static function theme(): array
    {
        $defaults = [
            'light_primary' => '#E58325', 'light_accent' => '#007A99', 'light_secondary' => '#973542',
            'light_success' => '#43A047', 'light_info' => '#1976D2', 'light_warning' => '#FF6D00', 'light_error' => '#EF5350',
            'dark_primary' => '#E58325', 'dark_accent' => '#007A99', 'dark_secondary' => '#973542',
            'dark_success' => '#43A047', 'dark_info' => '#1976D2', 'dark_warning' => '#FF6D00', 'dark_error' => '#EF5350',
        ];
        $out = [];
        foreach ($defaults as $key => $default) {
            $out[$key] = self::str('THEME_'.strtoupper($key), self::str('theme_'.$key, $default));
        }

        return $out;
    }
}
