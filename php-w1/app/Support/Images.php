<?php

namespace App\Support;

final class Images
{
    public static function writeSet(string $directory, string $bytes): void
    {
        if (! is_dir($directory) && ! mkdir($directory, 0775, true) && ! is_dir($directory)) {
            return;
        }
        $source = @imagecreatefromstring($bytes);
        if ($source === false) {
            file_put_contents($directory.'/original.webp', $bytes);

            return;
        }
        self::save($source, $directory.'/original.webp', imagesx($source));
        self::save($source, $directory.'/min-original.webp', 400);
        self::save($source, $directory.'/tiny-original.webp', 128);
        imagedestroy($source);
    }

    public static function removeSet(string $directory): void
    {
        foreach (['original.webp', 'min-original.webp', 'tiny-original.webp'] as $name) {
            $path = $directory.'/'.$name;
            if (is_file($path)) {
                unlink($path);
            }
        }
    }

    private static function save(\GdImage $source, string $path, int $width): void
    {
        $current = imagesx($source);
        $height = imagesy($source);
        $targetWidth = min($width, $current);
        $targetHeight = (int) max(1, round($height * ($targetWidth / max($current, 1))));
        $canvas = imagecreatetruecolor($targetWidth, $targetHeight);
        imagecopyresampled($canvas, $source, 0, 0, 0, 0, $targetWidth, $targetHeight, $current, $height);
        imagewebp($canvas, $path, 80);
        imagedestroy($canvas);
    }
}
