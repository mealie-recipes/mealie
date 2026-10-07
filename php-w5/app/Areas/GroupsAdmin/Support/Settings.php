<?php

namespace App\Areas\GroupsAdmin\Support;

/**
 * The subset of mealie/core/settings/settings.py AppSettings this area needs, read from the
 * process environment with the same variable names and defaults.
 */
class Settings
{
    public static function get(string $name, ?string $default = null): ?string
    {
        $value = getenv($name);

        return $value === false ? $default : $value;
    }

    public static function bool(string $name, bool $default): bool
    {
        $value = self::get($name);
        if ($value === null) {
            return $default;
        }

        return Validator::parseBool($value) ?? $default;
    }

    public static function baseUrl(): string
    {
        $url = self::get('BASE_URL', 'http://localhost:8080');

        return str_ends_with($url, '/') ? substr($url, 0, -1) : $url;
    }

    /** AppSettings.validate_smtp */
    public static function smtpEnabled(): bool
    {
        $required = [
            self::get('SMTP_HOST'),
            self::get('SMTP_PORT', '587'),
            self::get('SMTP_FROM_NAME', 'Mealie'),
            self::get('SMTP_FROM_EMAIL'),
            self::get('SMTP_AUTH_STRATEGY', 'TLS'),
        ];
        $user = self::get('SMTP_USER');
        $password = self::get('SMTP_PASSWORD');
        if ($user || $password) {
            $required[] = $user;
            $required[] = $password;
        }
        foreach ($required as $value) {
            if ($value === null || $value === '') {
                return false;
            }
        }

        return true;
    }

    /** AppSettings.LDAP_FEATURE.enabled */
    public static function ldapEnabled(): bool
    {
        return self::bool('LDAP_AUTH_ENABLED', false)
            && self::get('LDAP_SERVER_URL') !== null
            && self::get('LDAP_BASE_DN') !== null;
    }

    /** AppSettings.OIDC_FEATURE.enabled */
    public static function oidcReady(): bool
    {
        if (! self::bool('OIDC_AUTH_ENABLED', false)) {
            return false;
        }
        if (self::get('OIDC_CLIENT_ID') === null || self::get('OIDC_CLIENT_SECRET') === null || self::get('OIDC_CONFIGURATION_URL') === null) {
            return false;
        }
        $requiresGroupClaim = self::get('OIDC_USER_GROUP') !== null || self::get('OIDC_ADMIN_GROUP') !== null;

        return ! ($requiresGroupClaim && self::get('OIDC_GROUPS_CLAIM', 'groups') === null);
    }

    /** mealie/__init__.py __version__ (APP_VERSION) */
    public static function appVersion(): string
    {
        $file = dirname(base_path()).'/mealie/__init__.py';
        if (is_file($file) && preg_match('/__version__\s*=\s*["\']([^"\']+)["\']/', (string) file_get_contents($file), $m)) {
            return $m[1];
        }

        return 'develop';
    }
}
