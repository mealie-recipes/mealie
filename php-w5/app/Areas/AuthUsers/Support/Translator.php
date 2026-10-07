<?php

namespace App\Areas\AuthUsers\Support;

use Illuminate\Http\Request;

/** mealie/lang/providers.py get_locale_provider + mealie/pkgs/i18n JsonProvider.t */
class Translator
{
    /** @var array<string, array> */
    private static array $cache = [];

    public static function t(Request $request, string $key): string
    {
        $locale = $request->headers->get('accept-language') ?: 'en-US';
        $dir = dirname(base_path()).'/mealie/lang/messages';
        $file = "{$dir}/{$locale}.json";
        if (! preg_match('/^[A-Za-z0-9_-]+$/', $locale) || ! is_file($file)) {
            $file = "{$dir}/en-US.json";
        }
        self::$cache[$file] ??= json_decode((string) file_get_contents($file), true) ?: [];

        $value = self::$cache[$file];
        foreach (explode('.', $key) as $part) {
            if (! is_array($value) || ! array_key_exists($part, $value)) {
                return $key;
            }
            $value = $value[$part];
        }

        return is_string($value) ? $value : $key;
    }
}
