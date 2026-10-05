<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\MealieDb;
use ZipArchive;

final class MigrationService
{
    public function __construct(private readonly RecipeService $recipes) {}

    /**
     * @return array<string, mixed>
     */
    public function importArchive(object $user, string $bytes, string $type): array
    {
        $dir = sys_get_temp_dir().'/mealie-migration-'.bin2hex(random_bytes(4));
        mkdir($dir);
        $zipPath = $dir.'/archive.zip';
        file_put_contents($zipPath, $bytes);
        $zip = new ZipArchive;
        $imported = 0;
        $failed = 0;
        $messages = [];
        try {
            if ($bytes === '' || $zip->open($zipPath) !== true) {
                $messages[] = 'The archive could not be opened';

                return $this->report($user, 'failure', $messages);
            }
            $zip->extractTo($dir.'/out');
            $zip->close();
            $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($dir.'/out', \FilesystemIterator::SKIP_DOTS));
            foreach ($iterator as $file) {
                if (! $file->isFile()) {
                    continue;
                }
                $recipe = str_ends_with(strtolower($file->getFilename()), '.json')
                    ? $this->fromJson((string) file_get_contents($file->getPathname()))
                    : ($type === 'chowdown' && str_ends_with(strtolower($file->getFilename()), '.md')
                        ? $this->fromMarkdown((string) file_get_contents($file->getPathname()))
                        : null);
                if ($recipe === null) {
                    continue;
                }
                try {
                    $created = $this->recipes->create($user, ['name' => $recipe['name']]);
                    $this->recipes->update($user, (string) ($created['slug'] ?? ''), $recipe);
                    $imported++;
                    $messages[] = 'Imported '.$recipe['name'];
                } catch (\Throwable $e) {
                    $failed++;
                    $messages[] = $recipe['name'].': '.$e->getMessage();
                }
            }
        } finally {
            $this->removeDir($dir);
        }
        $status = $imported === 0 ? 'failure' : ($failed > 0 ? 'partial' : 'success');
        if ($imported === 0 && $messages === []) {
            $messages[] = 'No recipes were found in the archive';
        }

        return $this->report($user, $status, $messages);
    }

    /**
     * @return array<string, mixed>|null
     */
    private function fromJson(string $json): ?array
    {
        $data = json_decode($json, true);
        if (! is_array($data) || ! isset($data['name']) || ! is_string($data['name'])) {
            return null;
        }
        $lines = $data['recipeIngredient'] ?? $data['ingredients'] ?? [];
        if (is_string($lines)) {
            $lines = preg_split('/\r\n|\n/', $lines) ?: [];
        }
        $ingredients = [];
        foreach (is_array($lines) ? $lines : [] as $line) {
            $text = is_string($line) ? trim($line) : (is_array($line) ? trim((string) ($line['note'] ?? $line['name'] ?? '')) : '');
            if ($text !== '') {
                $ingredients[] = ['note' => $text, 'originalText' => $text, 'quantity' => 0];
            }
        }
        $steps = [];
        $instructions = $data['recipeInstructions'] ?? $data['instructions'] ?? [];
        if (is_string($instructions)) {
            $instructions = preg_split('/\r\n|\n/', $instructions) ?: [];
        }
        foreach (is_array($instructions) ? $instructions : [] as $step) {
            $text = is_string($step) ? trim($step) : (is_array($step) ? trim((string) ($step['text'] ?? '')) : '');
            if ($text !== '') {
                $steps[] = ['text' => $text, 'title' => '', 'summary' => ''];
            }
        }

        return [
            'name' => trim($data['name']),
            'description' => is_string($data['description'] ?? null) ? $data['description'] : '',
            'orgURL' => is_string($data['url'] ?? null) ? $data['url'] : null,
            'recipeIngredient' => $ingredients,
            'recipeInstructions' => $steps,
        ];
    }

    /**
     * @return array<string, mixed>|null
     */
    private function fromMarkdown(string $markdown): ?array
    {
        if (! preg_match('/^---\s*(.*?)\s*---\s*(.*)$/s', $markdown, $match)) {
            return null;
        }
        $title = null;
        if (preg_match('/^title:\s*(.+)$/m', $match[1], $titleMatch)) {
            $title = trim($titleMatch[1], " \t\"'");
        }
        if ($title === null || $title === '') {
            return null;
        }

        return [
            'name' => $title,
            'description' => '',
            'recipeIngredient' => [],
            'recipeInstructions' => trim($match[2]) === '' ? [] : [['text' => trim($match[2]), 'title' => '', 'summary' => '']],
        ];
    }

    /**
     * @param  list<string>  $messages
     * @return array<string, mixed>
     */
    private function report(object $user, string $status, array $messages): array
    {
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('group_reports')->insert([
            'id' => $id,
            'name' => 'Migration',
            'status' => $status,
            'category' => 'migration',
            'timestamp' => $now,
            'group_id' => $user->group_id,
            'created_at' => $now,
            'update_at' => $now,
        ]);
        foreach ($messages as $message) {
            MealieDb::table('report_entries')->insert([
                'id' => Guid::newHex(),
                'report_id' => $id,
                'success' => $status === 'success' ? 1 : 0,
                'message' => $message,
                'timestamp' => $now,
                'created_at' => $now,
                'update_at' => $now,
            ]);
        }

        return [
            'id' => Guid::dashed($id),
            'name' => 'Migration',
            'status' => $status,
            'category' => 'migration',
            'groupId' => Guid::dashed($user->group_id),
            'timestamp' => $now,
        ];
    }

    private function removeDir(string $dir): void
    {
        if (! is_dir($dir)) {
            return;
        }
        $iterator = new \RecursiveIteratorIterator(
            new \RecursiveDirectoryIterator($dir, \FilesystemIterator::SKIP_DOTS),
            \RecursiveIteratorIterator::CHILD_FIRST,
        );
        foreach ($iterator as $file) {
            $file->isDir() ? @rmdir($file->getPathname()) : @unlink($file->getPathname());
        }
        @rmdir($dir);
    }
}
