<?php

namespace App\Areas\Households\Support;

use Illuminate\Support\Str;

/** python-slugify `slugify(text)` with default options. */
class Slug
{
    public static function make(string $text): string
    {
        $text = Str::ascii($text);
        $text = strtolower($text);
        $text = preg_replace('/[^a-z0-9]+/', '-', $text);

        return trim($text, '-');
    }
}
