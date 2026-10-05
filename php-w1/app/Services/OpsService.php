<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use ZipArchive;

final class OpsService
{
    /**
     * @return array{valid: bool}
     */
    public function validateUnique(string $table, string $column, string $value): array
    {
        $exists = MealieDb::table($table)->whereRaw('lower('.$column.') = ?', [strtolower($value)])->exists();

        return ['valid' => ! $exists];
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function reports(object $user, ?string $category): array
    {
        $builder = MealieDb::table('group_reports')->where('group_id', $user->group_id);
        if (is_string($category) && $category !== '') {
            $builder->where('category', $category);
        }

        return $builder->orderByDesc('timestamp')->get()->map(fn ($row) => $this->report($row, false))->all();
    }

    /**
     * @return array<string, mixed>|null
     */
    public function report(object $row, bool $withEntries): array
    {
        $out = [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'status' => $row->status,
            'category' => $row->category,
            'groupId' => Guid::dashed($row->group_id),
            'timestamp' => JsonShape::dateTime($row->timestamp),
        ];
        if ($withEntries) {
            $out['entries'] = MealieDb::table('report_entries')->where('report_id', $row->id)->orderBy('timestamp')->get()
                ->map(fn ($entry) => [
                    'id' => Guid::dashed($entry->id),
                    'reportId' => Guid::dashed($entry->report_id),
                    'success' => JsonShape::bool($entry->success),
                    'message' => $entry->message ?? '',
                    'exception' => $entry->exception,
                    'timestamp' => JsonShape::dateTime($entry->timestamp),
                ])->all();
        }

        return $out;
    }

    /**
     * @return array<string, mixed>|null
     */
    public function findReport(object $user, string $id): ?array
    {
        $hex = Guid::hex($id);
        $row = $hex === null ? null : MealieDb::table('group_reports')->where('id', $hex)->where('group_id', $user->group_id)->first();

        return $row === null ? null : $this->report($row, true);
    }

    public function deleteReport(object $user, string $id): bool
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return false;
        }
        $row = MealieDb::table('group_reports')->where('id', $hex)->where('group_id', $user->group_id)->first();
        if ($row === null) {
            return false;
        }
        MealieDb::table('report_entries')->where('report_id', $hex)->delete();

        return MealieDb::table('group_reports')->where('id', $hex)->delete() > 0;
    }

    /**
     * @return array<string, mixed>
     */
    public function notifiers(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('group_events_notifiers')->where('household_id', $user->household_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->notifier($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createNotifier(object $user, array $payload): array
    {
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('group_events_notifiers')->insert([
            'id' => $id,
            'name' => (string) ($payload['name'] ?? 'Notifier'),
            'enabled' => JsonShape::bool($payload['enabled'] ?? true) ? 1 : 0,
            'apprise_url' => (string) ($payload['appriseUrl'] ?? $payload['apprise_url'] ?? ''),
            'group_id' => $user->group_id,
            'household_id' => $user->household_id,
            'created_at' => $now,
            'update_at' => $now,
        ]);
        $this->writeOptions($id, $payload['options'] ?? []);

        return $this->notifier(MealieDb::table('group_events_notifiers')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateNotifier(object $user, string $id, array $payload): ?array
    {
        $row = $this->ownedNotifier($user, $id);
        if ($row === null) {
            return null;
        }
        MealieDb::table('group_events_notifiers')->where('id', $row->id)->update([
            'name' => (string) ($payload['name'] ?? $row->name),
            'enabled' => array_key_exists('enabled', $payload) ? (JsonShape::bool($payload['enabled']) ? 1 : 0) : $row->enabled,
            'apprise_url' => (string) ($payload['appriseUrl'] ?? $payload['apprise_url'] ?? $row->apprise_url),
            'update_at' => MealieDb::now(),
        ]);
        if (isset($payload['options']) && is_array($payload['options'])) {
            $this->writeOptions($row->id, $payload['options']);
        }

        return $this->notifier(MealieDb::table('group_events_notifiers')->where('id', $row->id)->first());
    }

    public function deleteNotifier(object $user, string $id): bool
    {
        $row = $this->ownedNotifier($user, $id);
        if ($row === null) {
            return false;
        }
        MealieDb::table('group_events_notifier_options')->where('event_notifier_id', $row->id)->delete();

        return MealieDb::table('group_events_notifiers')->where('id', $row->id)->delete() > 0;
    }

    /**
     * @return array<string, mixed>
     */
    public function actions(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('recipe_actions')->where('household_id', $user->household_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('title')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->action($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createAction(object $user, array $payload): array
    {
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('recipe_actions')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'household_id' => $user->household_id,
            'action_type' => (string) ($payload['actionType'] ?? $payload['action_type'] ?? 'link'),
            'title' => (string) ($payload['title'] ?? 'Action'),
            'url' => (string) ($payload['url'] ?? ''),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->action(MealieDb::table('recipe_actions')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateAction(object $user, string $id, array $payload): ?array
    {
        $hex = Guid::hex($id);
        $row = $hex === null ? null : MealieDb::table('recipe_actions')->where('id', $hex)->where('household_id', $user->household_id)->first();
        if ($row === null) {
            return null;
        }
        MealieDb::table('recipe_actions')->where('id', $hex)->update([
            'action_type' => (string) ($payload['actionType'] ?? $payload['action_type'] ?? $row->action_type),
            'title' => (string) ($payload['title'] ?? $row->title),
            'url' => (string) ($payload['url'] ?? $row->url),
            'update_at' => MealieDb::now(),
        ]);

        return $this->action(MealieDb::table('recipe_actions')->where('id', $hex)->first());
    }

    public function deleteAction(object $user, string $id): bool
    {
        $hex = Guid::hex($id);

        return $hex !== null && MealieDb::table('recipe_actions')->where('id', $hex)->where('household_id', $user->household_id)->delete() > 0;
    }

    /**
     * @return array<string, mixed>
     */
    public function seed(object $user, string $table, string $locale): array
    {
        $names = $table === 'ingredient_foods' ? $this->foodNames($locale) : $this->unitNames($locale);
        $created = 0;
        foreach ($names as $name) {
            $exists = MealieDb::table($table)->where('group_id', $user->group_id)->whereRaw('lower(name) = ?', [strtolower($name)])->exists();
            if ($exists) {
                continue;
            }
            $now = MealieDb::now();
            $extra = $table === 'ingredient_units' ? [
                'abbreviation' => $name,
                'fraction' => 0,
                'use_abbreviation' => 0,
                'name_normalized' => Str::lower($name),
            ] : [
                'on_hand' => 0,
                'name_normalized' => Str::lower($name),
            ];
            MealieDb::table($table)->insert(array_merge($extra, [
                'id' => Guid::newHex(),
                'group_id' => $user->group_id,
                'name' => $name,
                'description' => '',
                'created_at' => $now,
                'update_at' => $now,
            ]));
            $created++;
        }

        return ['message' => $created.' '.$table.' seeded'];
    }

    /**
     * @return array{imports: list<array<string, mixed>>, templates: list<string>}
     */
    public function backups(): array
    {
        $imports = [];
        foreach (glob($this->backupDir().'/*.zip') ?: [] as $file) {
            $imports[] = [
                'name' => basename($file),
                'date' => date('c', (int) filemtime($file)),
                'size' => $this->pretty((int) filesize($file)),
            ];
        }
        usort($imports, fn ($a, $b) => strcmp($b['date'], $a['date']));

        return ['imports' => $imports, 'templates' => []];
    }

    public function createBackup(): string
    {
        $dir = $this->backupDir();
        if (! is_dir($dir) && ! mkdir($dir, 0775, true) && ! is_dir($dir)) {
            throw new \RuntimeException('Backup directory is not writable');
        }
        $name = 'mealie_'.gmdate('Y-m-d_H-i-s').'.zip';
        $zip = new ZipArchive;
        if ($zip->open($dir.'/'.$name, ZipArchive::CREATE) !== true) {
            throw new \RuntimeException('Could not create the backup archive');
        }
        $database = (string) config('database.connections.mealie.database');
        if (is_file($database)) {
            $zip->addFile($database, 'mealie.db');
        }
        $zip->addFromString('database.json', json_encode($this->databaseDump(), JSON_THROW_ON_ERROR));
        $zip->close();

        return $name;
    }

    public function restoreBackup(string $name): void
    {
        $path = $this->backupPath($name);
        if ($path === null) {
            throw new \RuntimeException('Backup was not found');
        }
        $zip = new ZipArchive;
        if ($zip->open($path) !== true) {
            throw new \RuntimeException('Backup archive could not be opened');
        }
        $json = $zip->getFromName('database.json');
        $zip->close();
        if (! is_string($json) || $json === '') {
            throw new \RuntimeException('This archive has no database.json. Stop Mealie and replace the database file from mealie.db instead.');
        }
        $dump = json_decode($json, true);
        if (! is_array($dump)) {
            throw new \RuntimeException('database.json is not valid');
        }
        $this->restoreDump($dump);
    }

    /**
     * @return array<string, list<array<string, mixed>>>
     */
    public function databaseDump(): array
    {
        $connection = DB::connection('mealie');
        $names = $connection->getDriverName() === 'pgsql'
            ? $connection->select("select tablename as name from pg_tables where schemaname = 'public'")
            : $connection->select("select name from sqlite_master where type = 'table' and name not like 'sqlite_%'");
        $dump = [];
        foreach ($names as $table) {
            $name = (string) $table->name;
            $dump[$name] = $connection->table($name)->get()->map(fn ($row) => (array) $row)->all();
        }

        return $dump;
    }

    /**
     * @param  array<string, mixed>  $dump
     */
    private function restoreDump(array $dump): void
    {
        unset($dump['alembic_version']);
        $connection = DB::connection('mealie');
        $sqlite = $connection->getDriverName() === 'sqlite';
        $outer = $connection->transactionLevel() > 0;
        if ($sqlite && ! $outer) {
            $connection->statement('PRAGMA foreign_keys = OFF');
        }
        $connection->beginTransaction();
        try {
            foreach ($dump as $table => $rows) {
                if (! is_string($table) || ! is_array($rows) || ! $connection->getSchemaBuilder()->hasTable($table)) {
                    continue;
                }
                $connection->table($table)->delete();
            }
            foreach ($dump as $table => $rows) {
                if (! is_string($table) || ! is_array($rows) || $rows === [] || ! $connection->getSchemaBuilder()->hasTable($table)) {
                    continue;
                }
                foreach (array_chunk($rows, 100) as $chunk) {
                    $connection->table($table)->insert($chunk);
                }
            }
            $connection->commit();
        } catch (\Throwable $e) {
            $connection->rollBack();
            throw $e;
        } finally {
            if ($sqlite && ! $outer) {
                $connection->statement('PRAGMA foreign_keys = ON');
            }
        }
    }

    public function backupPath(string $name): ?string
    {
        if (! preg_match('/^[A-Za-z0-9._-]+\.zip$/', $name)) {
            return null;
        }
        $path = $this->backupDir().'/'.$name;

        return is_file($path) ? $path : null;
    }

    public function deleteBackup(string $name): bool
    {
        $path = $this->backupPath($name);

        return $path !== null && unlink($path);
    }

    public function storeUpload(string $original, string $bytes): bool
    {
        $name = pathinfo($original, PATHINFO_FILENAME);
        $name = preg_replace('/[^A-Za-z0-9._-]/', '', $name) ?: 'upload';
        if (! str_ends_with(strtolower($original), '.zip') || $bytes === '') {
            return false;
        }
        $dir = $this->backupDir();
        if (! is_dir($dir) && ! mkdir($dir, 0775, true) && ! is_dir($dir)) {
            return false;
        }

        return file_put_contents($dir.'/'.$name.'.zip', $bytes) !== false;
    }

    /**
     * @return array<string, mixed>
     */
    public function maintenance(): array
    {
        $root = rtrim((string) config('mealie.data_dir'), '/');

        return [
            'dataDirSize' => $this->pretty($this->dirSize($root)),
            'cleanableImages' => count(glob($root.'/recipes/*/images/min-original.webp') ?: []),
            'cleanableDirs' => 0,
        ];
    }

    /**
     * @return array<string, string>
     */
    public function storageDetails(): array
    {
        $root = rtrim((string) config('mealie.data_dir'), '/');

        return [
            'tempDirSize' => $this->pretty($this->dirSize($root.'/temp')),
            'backupsDirSize' => $this->pretty($this->dirSize($root.'/backups')),
            'groupsDirSize' => $this->pretty($this->dirSize($root.'/groups')),
            'recipesDirSize' => $this->pretty($this->dirSize($root.'/recipes')),
            'userDirSize' => $this->pretty($this->dirSize($root.'/users')),
        ];
    }

    /**
     * @return array{logs: string}
     */
    public function logs(int $lines): array
    {
        $path = storage_path('logs/laravel.log');
        if (! is_file($path)) {
            return ['logs' => ''];
        }
        $content = file($path) ?: [];

        return ['logs' => implode('', array_slice($content, -max(1, min($lines, 500))))];
    }

    /**
     * @return array<string, mixed>
     */
    public function groupStorage(object $user): array
    {
        $bytes = $this->dirSize(rtrim((string) config('mealie.data_dir'), '/').'/recipes');

        return [
            'usedStorageBytes' => $bytes,
            'usedStorageStr' => $this->pretty($bytes),
            'totalStorageBytes' => 0,
            'totalStorageStr' => '0 B',
        ];
    }

    /**
     * @return array<string, mixed>
     */
    public function households(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('households')->where('group_id', $user->group_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->household($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createHousehold(object $user, array $payload): array
    {
        $name = trim((string) ($payload['name'] ?? 'Household'));
        $id = Guid::newHex();
        $now = MealieDb::now();
        $slug = $this->uniqueSlug('households', 'group_id', $user->group_id, Str::slug($name) ?: 'household');
        MealieDb::table('households')->insert([
            'id' => $id,
            'name' => $name,
            'slug' => $slug,
            'group_id' => $user->group_id,
            'created_at' => $now,
            'update_at' => $now,
        ]);
        MealieDb::table('household_preferences')->insert([
            'id' => Guid::newHex(),
            'household_id' => $id,
            'private_household' => 0,
            'first_day_of_week' => 0,
            'show_announcements' => 1,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->household(MealieDb::table('households')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateHousehold(object $user, string $id, array $payload): ?array
    {
        $hex = Guid::hex($id);
        $row = $hex === null ? null : MealieDb::table('households')->where('id', $hex)->where('group_id', $user->group_id)->first();
        if ($row === null) {
            return null;
        }
        $name = trim((string) ($payload['name'] ?? $row->name));
        MealieDb::table('households')->where('id', $hex)->update([
            'name' => $name,
            'slug' => $name === $row->name ? $row->slug : $this->uniqueSlug('households', 'group_id', $user->group_id, Str::slug($name) ?: $row->slug),
            'update_at' => MealieDb::now(),
        ]);

        return $this->household(MealieDb::table('households')->where('id', $hex)->first());
    }

    public function deleteHousehold(object $user, string $id): bool
    {
        $hex = Guid::hex($id);
        if ($hex === null || $hex === $user->household_id) {
            return false;
        }
        if (MealieDb::table('users')->where('household_id', $hex)->exists()) {
            return false;
        }
        MealieDb::table('household_preferences')->where('household_id', $hex)->delete();

        return MealieDb::table('households')->where('id', $hex)->where('group_id', $user->group_id)->delete() > 0;
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createGroup(array $payload): array
    {
        $name = trim((string) ($payload['name'] ?? 'Group'));
        $id = Guid::newHex();
        $now = MealieDb::now();
        $slug = $this->uniqueGroupSlug(Str::slug($name) ?: 'group');
        MealieDb::table('groups')->insert([
            'id' => $id,
            'name' => $name,
            'slug' => $slug,
            'created_at' => $now,
            'update_at' => $now,
        ]);
        MealieDb::table('group_preferences')->insert([
            'id' => Guid::newHex(),
            'group_id' => $id,
            'private_group' => 0,
            'show_announcements' => 1,
            'first_day_of_week' => 0,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return ['id' => Guid::dashed($id), 'name' => $name, 'slug' => $slug];
    }

    public function deleteGroup(string $id): bool
    {
        $hex = Guid::hex($id);
        if ($hex === null || MealieDb::table('users')->where('group_id', $hex)->exists()) {
            return false;
        }
        MealieDb::table('group_preferences')->where('group_id', $hex)->delete();

        return MealieDb::table('groups')->where('id', $hex)->delete() > 0;
    }

    /**
     * @param  list<string>  $labelIds
     */
    public function replaceLabelSettings(object $user, string $listId, array $labelIds): bool
    {
        $hex = Guid::hex($listId);
        if ($hex === null) {
            return false;
        }
        $list = MealieDb::table('shopping_lists')->where('id', $hex)->where('group_id', $user->group_id)->first();
        if ($list === null) {
            return false;
        }
        MealieDb::table('shopping_lists_multi_purpose_labels')->where('shopping_list_id', $hex)->delete();
        $position = 0;
        foreach ($labelIds as $labelId) {
            $label = Guid::hex($labelId);
            if ($label === null) {
                continue;
            }
            MealieDb::table('shopping_lists_multi_purpose_labels')->insert([
                'id' => Guid::newHex(),
                'shopping_list_id' => $hex,
                'label_id' => $label,
                'position' => $position,
                'created_at' => MealieDb::now(),
                'update_at' => MealieDb::now(),
            ]);
            $position++;
        }

        return true;
    }

    /**
     * @param  array<string, mixed>  $options
     */
    private function writeOptions(string $notifierId, array $options): void
    {
        $columns = [
            'recipeCreated' => 'recipe_created',
            'recipeUpdated' => 'recipe_updated',
            'recipeDeleted' => 'recipe_deleted',
            'userSignup' => 'user_signup',
            'dataMigrations' => 'data_migrations',
            'dataExport' => 'data_export',
            'dataImport' => 'data_import',
            'mealplanEntryCreated' => 'mealplan_entry_created',
            'mealplanEntryUpdated' => 'mealplan_entry_updated',
            'mealplanEntryDeleted' => 'mealplan_entry_deleted',
            'shoppingListCreated' => 'shopping_list_created',
            'shoppingListUpdated' => 'shopping_list_updated',
            'shoppingListDeleted' => 'shopping_list_deleted',
            'cookbookCreated' => 'cookbook_created',
            'cookbookUpdated' => 'cookbook_updated',
            'cookbookDeleted' => 'cookbook_deleted',
            'tagCreated' => 'tag_created',
            'tagUpdated' => 'tag_updated',
            'tagDeleted' => 'tag_deleted',
            'categoryCreated' => 'category_created',
            'categoryUpdated' => 'category_updated',
            'categoryDeleted' => 'category_deleted',
            'labelCreated' => 'label_created',
            'labelUpdated' => 'label_updated',
            'labelDeleted' => 'label_deleted',
        ];
        $fields = ['update_at' => MealieDb::now()];
        foreach ($columns as $camel => $column) {
            $fields[$column] = JsonShape::bool($options[$camel] ?? $options[$column] ?? false) ? 1 : 0;
        }
        $existing = MealieDb::table('group_events_notifier_options')->where('event_notifier_id', $notifierId)->first();
        if ($existing === null) {
            MealieDb::table('group_events_notifier_options')->insert(array_merge($fields, [
                'id' => Guid::newHex(),
                'event_notifier_id' => $notifierId,
                'created_at' => MealieDb::now(),
            ]));

            return;
        }
        MealieDb::table('group_events_notifier_options')->where('id', $existing->id)->update($fields);
    }

    /**
     * @return array<string, mixed>
     */
    private function notifier(object $row): array
    {
        $options = MealieDb::table('group_events_notifier_options')->where('event_notifier_id', $row->id)->first();

        return [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'enabled' => JsonShape::bool($row->enabled),
            'groupId' => Guid::dashed($row->group_id),
            'householdId' => Guid::dashed($row->household_id),
            'appriseUrl' => $row->apprise_url,
            'options' => [
                'recipeCreated' => JsonShape::bool($options->recipe_created ?? false),
                'recipeUpdated' => JsonShape::bool($options->recipe_updated ?? false),
                'recipeDeleted' => JsonShape::bool($options->recipe_deleted ?? false),
                'userSignup' => JsonShape::bool($options->user_signup ?? false),
                'dataMigrations' => JsonShape::bool($options->data_migrations ?? false),
                'dataExport' => JsonShape::bool($options->data_export ?? false),
                'dataImport' => JsonShape::bool($options->data_import ?? false),
                'mealplanEntryCreated' => JsonShape::bool($options->mealplan_entry_created ?? false),
                'shoppingListCreated' => JsonShape::bool($options->shopping_list_created ?? false),
                'shoppingListUpdated' => JsonShape::bool($options->shopping_list_updated ?? false),
                'shoppingListDeleted' => JsonShape::bool($options->shopping_list_deleted ?? false),
                'cookbookCreated' => JsonShape::bool($options->cookbook_created ?? false),
                'cookbookUpdated' => JsonShape::bool($options->cookbook_updated ?? false),
                'cookbookDeleted' => JsonShape::bool($options->cookbook_deleted ?? false),
                'tagCreated' => JsonShape::bool($options->tag_created ?? false),
                'tagUpdated' => JsonShape::bool($options->tag_updated ?? false),
                'tagDeleted' => JsonShape::bool($options->tag_deleted ?? false),
                'categoryCreated' => JsonShape::bool($options->category_created ?? false),
                'categoryUpdated' => JsonShape::bool($options->category_updated ?? false),
                'categoryDeleted' => JsonShape::bool($options->category_deleted ?? false),
                'labelCreated' => JsonShape::bool($options->label_created ?? false),
                'labelUpdated' => JsonShape::bool($options->label_updated ?? false),
                'labelDeleted' => JsonShape::bool($options->label_deleted ?? false),
                'notifierId' => Guid::dashed($row->id),
            ],
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function action(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'groupId' => Guid::dashed($row->group_id),
            'householdId' => Guid::dashed($row->household_id),
            'actionType' => $row->action_type,
            'title' => $row->title,
            'url' => $row->url,
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function household(object $row): array
    {
        $group = MealieDb::table('groups')->where('id', $row->group_id)->first();

        return [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'slug' => $row->slug,
            'groupId' => Guid::dashed($row->group_id),
            'group' => $group->name ?? '',
        ];
    }

    private function ownedNotifier(object $user, string $id): ?object
    {
        $hex = Guid::hex($id);

        return $hex === null ? null : MealieDb::table('group_events_notifiers')->where('id', $hex)->where('household_id', $user->household_id)->first();
    }

    /**
     * @return list<string>
     */
    private function foodNames(string $locale): array
    {
        if (str_starts_with(strtolower($locale), 'zh')) {
            return ['鸡蛋', '牛奶', '面粉', '盐', '糖', '洋葱', '大蒜', '番茄'];
        }

        return ['egg', 'milk', 'flour', 'salt', 'sugar', 'onion', 'garlic', 'tomato'];
    }

    /**
     * @return list<string>
     */
    private function unitNames(string $locale): array
    {
        if (str_starts_with(strtolower($locale), 'zh')) {
            return ['克', '千克', '毫升', '升', '茶匙', '汤匙'];
        }

        return ['teaspoon', 'tablespoon', 'cup', 'gram', 'kilogram', 'milliliter'];
    }

    private function backupDir(): string
    {
        return rtrim((string) config('mealie.data_dir'), '/').'/backups';
    }

    private function pretty(int $bytes): string
    {
        if ($bytes < 1024) {
            return $bytes.' B';
        }
        if ($bytes < 1048576) {
            return round($bytes / 1024, 1).' KB';
        }

        return round($bytes / 1048576, 1).' MB';
    }

    private function dirSize(string $path): int
    {
        if (! is_dir($path)) {
            return 0;
        }
        $size = 0;
        $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($path, \FilesystemIterator::SKIP_DOTS));
        foreach ($iterator as $file) {
            if ($file->isFile()) {
                $size += $file->getSize();
            }
        }

        return $size;
    }

    private function uniqueGroupSlug(string $slug): string
    {
        $candidate = $slug;
        $i = 2;
        while (MealieDb::table('groups')->where('slug', $candidate)->exists()) {
            $candidate = $slug.'-'.$i;
            $i++;
        }

        return $candidate;
    }

    private function uniqueSlug(string $table, string $column, string $owner, string $slug): string
    {
        $candidate = $slug;
        $i = 2;
        while (MealieDb::table($table)->where($column, $owner)->where('slug', $candidate)->exists()) {
            $candidate = $slug.'-'.$i;
            $i++;
        }

        return $candidate;
    }
}
