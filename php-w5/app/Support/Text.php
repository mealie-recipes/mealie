<?php

namespace App\Support;

/**
 * python-slugify `slugify()` defaults, text_unidecode and SqlAlchemyBase.normalize (mealie/db/models/_model_base.py).
 */
class Text
{
    /** string.punctuation minus ' and " (NORMALIZE_PUNCTUATION). */
    public const PUNCTUATION = '!#$%&()*+,-./:;<=>?@[\\]^_`{|}~';

    public static function unidecode(string $value): string
    {
        $out = \transliterator_transliterate('Any-Latin; Latin-ASCII', $value);

        return $out === false ? $value : $out;
    }

    public static function slugify(string $value): string
    {
        $value = str_replace("'", '-', $value);
        $value = self::unidecode($value);
        // entities=True, decimal=True, hexadecimal=True
        $value = html_entity_decode($value, ENT_QUOTES | ENT_HTML5, 'UTF-8');
        $value = strtolower($value);
        $value = str_replace("'", '', $value);
        $value = preg_replace('/(?<=\d),(?=\d)/', '', $value);
        $value = preg_replace('/[^-a-z0-9]+/', '-', $value);
        $value = preg_replace('/-{2,}/', '-', $value);

        return trim($value, '-');
    }

    public static function normalize(string $value): string
    {
        $value = self::unidecode($value);
        $value = strtr($value, self::PUNCTUATION, str_repeat(' ', strlen(self::PUNCTUATION)));

        return substr(trim(strtolower($value)), 0, 255);
    }
}
