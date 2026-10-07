<?php

namespace App\Areas\GroupsAdmin\Support;

/**
 * mealie/pkgs/stats/fs_stats.py, mealie/core/settings/directories.py and python-slugify helpers.
 */
class Fs
{
    public static function dataDir(): string
    {
        return rtrim((string) config('mealie.data_dir'), '/');
    }

    public static function dir(string $name): string
    {
        return match ($name) {
            'DATA_DIR' => self::dataDir(),
            'BACKUP_DIR' => self::dataDir().'/backups',
            'USER_DIR' => self::dataDir().'/users',
            'RECIPE_DATA_DIR' => self::dataDir().'/recipes',
            'TEMPLATE_DIR' => self::dataDir().'/templates',
            'GROUPS_DIR' => self::dataDir().'/groups',
            'TEMP_DIR' => self::dataDir().'/.temp',
        };
    }

    /** Python `str(round(x, 2))` */
    public static function pyFloat(float $value): string
    {
        $s = (string) $value;
        if (! str_contains($s, '.') && ! str_contains($s, 'E') && ! str_contains($s, 'e')) {
            $s .= '.0';
        }

        return $s;
    }

    public static function prettySize(int $size): string
    {
        if ($size < 1024) {
            return "{$size} bytes";
        }
        if ($size < 1024 ** 2) {
            return self::pyFloat(round($size / 1024, 2)).' KB';
        }
        if ($size < 1024 ** 3) {
            return self::pyFloat(round($size / 1024 / 1024, 2)).' MB';
        }
        if ($size < 1024 ** 4) {
            return self::pyFloat(round($size / 1024 / 1024 / 1024, 2)).' GB';
        }

        return self::pyFloat(round($size / 1024 / 1024 / 1024 / 1024, 2)).' TB';
    }

    public static function dirSize(string $path): int
    {
        clearstatcache();
        if (! file_exists($path)) {
            return 0;
        }
        $total = (int) filesize($path);
        if (! is_dir($path)) {
            return $total;
        }
        foreach (scandir($path) ?: [] as $item) {
            if ($item === '.' || $item === '..') {
                continue;
            }
            $itemPath = $path.'/'.$item;
            if (is_file($itemPath)) {
                $total += (int) filesize($itemPath);
            } elseif (is_dir($itemPath)) {
                $total += self::dirSize($itemPath);
            }
        }

        return $total;
    }

    public static function rmtree(string $path): void
    {
        if (is_link($path) || is_file($path)) {
            @unlink($path);

            return;
        }
        if (! is_dir($path)) {
            return;
        }
        foreach (scandir($path) ?: [] as $item) {
            if ($item !== '.' && $item !== '..') {
                self::rmtree($path.'/'.$item);
            }
        }
        @rmdir($path);
    }

    /** python-slugify `slugify(text)` with default options. */
    public static function slugify(string $text): string
    {
        $text = preg_replace("/[']+/", '-', $text);
        $text = Search::unidecode($text);
        $text = strtolower($text);
        $text = preg_replace("/[']+/", '', $text);
        $text = preg_replace('/(?<=\d),(?=\d)/', '', $text);
        $text = preg_replace('/[^-a-zA-Z0-9]+/', '-', $text);
        $text = preg_replace('/-{2,}/', '-', $text);

        return trim($text, '-');
    }
}
