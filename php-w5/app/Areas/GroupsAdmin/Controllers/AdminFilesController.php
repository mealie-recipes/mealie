<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Fs;
use App\Auth\Jwt;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;

/** mealie/routes/admin/admin_backups.py (read/delete) and admin_maintenance.py */
class AdminFilesController
{
    // ------------------------------------------------------------ backups

    /** Lexical `(backup_dir / name).resolve()` + is_relative_to check (AdminBackupController._backup_path). */
    private function backupPath(string $name): string
    {
        $base = Fs::dir('BACKUP_DIR');
        $baseReal = realpath($base) ?: $base;
        $parts = [];
        foreach (explode('/', $baseReal.'/'.$name) as $part) {
            if ($part === '' || $part === '.') {
                continue;
            }
            if ($part === '..') {
                array_pop($parts);
            } else {
                $parts[] = $part;
            }
        }
        $candidate = '/'.implode('/', $parts);
        $resolved = realpath($candidate) ?: $candidate;
        if ($resolved !== $baseReal && ! str_starts_with($resolved, rtrim($baseReal, '/').'/')) {
            Errors::http(400);
        }

        return $resolved;
    }

    /** GET /admin/backups */
    public function backups()
    {
        clearstatcache();
        $imports = [];
        foreach (glob(Fs::dir('BACKUP_DIR').'/*.zip') ?: [] as $archive) {
            $mtime = (float) (stat($archive)['mtime'] ?? 0);
            $imports[] = [
                'name' => basename($archive),
                'date' => self::timestamp($archive, $mtime),
                'size' => Fs::prettySize((int) filesize($archive)),
                '_sort' => $mtime,
            ];
        }
        usort($imports, fn ($a, $b) => $b['_sort'] <=> $a['_sort']);
        $imports = array_map(function ($i) {
            unset($i['_sort']);

            return $i;
        }, $imports);

        $templates = array_map('basename', glob(Fs::dir('TEMPLATE_DIR').'/*.*') ?: []);

        return Json::respond(['imports' => $imports, 'templates' => $templates]);
    }

    /** Pydantic datetime from a POSIX timestamp (st_mtime keeps sub-second precision via `stat -c %Y.%N`). */
    private static function timestamp(string $path, float $mtime): string
    {
        $micro = 0;
        $out = @shell_exec('stat -c %y '.escapeshellarg($path).' 2>/dev/null');
        if (is_string($out) && preg_match('/\.(\d{1,9})/', $out, $m)) {
            $micro = (int) substr(str_pad($m[1], 9, '0'), 0, 6);
        }
        $date = gmdate('Y-m-d\TH:i:s', (int) $mtime);

        return $date.($micro ? sprintf('.%06d', $micro) : '').'Z';
    }

    /** GET /admin/backups/{file_name} */
    public function backupToken(string $fileName)
    {
        $file = $this->backupPath($fileName);
        if (! file_exists($file)) {
            Errors::http(404);
        }
        $now = time();
        $token = Jwt::encode(['file' => $file, 'iss' => 'mealie', 'iat' => $now, 'exp' => $now + 30 * 60], Jwt::secret());

        return Json::respond(['fileToken' => $token]);
    }

    /** DELETE /admin/backups/{file_name} */
    public function deleteBackup(string $fileName)
    {
        $file = $this->backupPath($fileName);
        if (! is_file($file)) {
            Errors::http(400);
        }
        if (! @unlink($file)) {
            Errors::http(500, 'Internal Server Error');
        }

        return Json::respond(['message' => "{$fileName} has been deleted.", 'error' => false]);
    }

    // ------------------------------------------------------------ maintenance

    /** pathlib.Path.suffix */
    private static function suffix(string $name): string
    {
        $i = strrpos($name, '.');

        return $i !== false && $i > 0 && $i < strlen($name) - 1 ? substr($name, $i) : '';
    }

    private static function children(string $dir): array
    {
        $out = [];
        foreach (scandir($dir) ?: [] as $item) {
            if ($item !== '.' && $item !== '..') {
                $out[] = $dir.'/'.$item;
            }
        }

        return $out;
    }

    private static function cleanImages(bool $dryRun): int
    {
        $count = 0;
        foreach (self::children(Fs::dir('RECIPE_DATA_DIR')) as $recipeDir) {
            $imageDir = $recipeDir.'/images';
            if (! file_exists($imageDir)) {
                continue;
            }
            foreach (self::children($imageDir) as $image) {
                if (is_dir($image)) {
                    continue;
                }
                if (self::suffix(basename($image)) !== '.webp') {
                    if (! $dryRun) {
                        unlink($image);
                    }
                    $count++;
                }
            }
        }

        return $count;
    }

    private static function cleanRecipeFolders(bool $dryRun): int
    {
        $count = 0;
        foreach (self::children(Fs::dir('RECIPE_DATA_DIR')) as $recipeDir) {
            if (! is_dir($recipeDir)) {
                continue;
            }
            $name = basename($recipeDir);
            $plain = preg_replace('/^(urn:)?(uuid:)?/', '', $name);
            if (Guid::isUuid($plain)) {
                continue;
            }
            if (! $dryRun) {
                Fs::rmtree($recipeDir);
            }
            $count++;
        }

        return $count;
    }

    /** GET /admin/maintenance */
    public function summary()
    {
        clearstatcache();

        return Json::respond([
            'dataDirSize' => Fs::prettySize(Fs::dirSize(Fs::dir('DATA_DIR'))),
            'cleanableImages' => self::cleanImages(true),
            'cleanableDirs' => self::cleanRecipeFolders(true),
        ]);
    }

    /** GET /admin/maintenance/storage */
    public function storage()
    {
        return Json::respond([
            'tempDirSize' => Fs::prettySize(Fs::dirSize(Fs::dir('TEMP_DIR'))),
            'backupsDirSize' => Fs::prettySize(Fs::dirSize(Fs::dir('BACKUP_DIR'))),
            'groupsDirSize' => Fs::prettySize(Fs::dirSize(Fs::dir('GROUPS_DIR'))),
            'recipesDirSize' => Fs::prettySize(Fs::dirSize(Fs::dir('RECIPE_DATA_DIR'))),
            'userDirSize' => Fs::prettySize(Fs::dirSize(Fs::dir('USER_DIR'))),
        ]);
    }

    /** POST /admin/maintenance/clean/images */
    public function cleanImagesRoute()
    {
        try {
            $n = self::cleanImages(false);
        } catch (\Throwable) {
            Errors::errorResponse(500, 'Failed to clean images');
        }

        return Json::respond(['message' => "{$n} Images cleaned", 'error' => false]);
    }

    /** POST /admin/maintenance/clean/temp */
    public function cleanTemp()
    {
        $temp = Fs::dir('TEMP_DIR');
        try {
            Fs::rmtree($temp);
            if (! is_dir($temp) && ! mkdir($temp, 0755, true)) {
                throw new \RuntimeException('mkdir failed');
            }
        } catch (\Throwable) {
            Errors::errorResponse(500, 'Failed to clean temp');
        }

        return Json::respond(['message' => "'.temp' directory cleaned", 'error' => false]);
    }

    /** POST /admin/maintenance/clean/recipe-folders */
    public function cleanRecipeFoldersRoute()
    {
        try {
            $n = self::cleanRecipeFolders(false);
        } catch (\Throwable) {
            Errors::errorResponse(500, 'Failed to clean directories');
        }

        return Json::respond(['message' => "{$n} Recipe folders removed", 'error' => false]);
    }
}
