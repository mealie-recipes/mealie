<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

final class CatalogService
{
    /**
     * @return array<string, mixed>
     */
    public function page(object $user, Request $request, string $table): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table($table)->where('group_id', $user->group_id);
        if (is_string($query['search']) && $query['search'] !== '') {
            $builder->where('name', 'like', '%'.$query['search'].'%');
        }
        $total = (clone $builder)->count();
        $perPage = $query['perPage'] < 0 ? max($total, 1) : $query['perPage'];
        $rows = $builder->orderBy('name')->forPage($query['page'], $perPage)->get();

        return Pages::make($rows->map(fn ($row) => $this->organizer($row, $table))->all(), $query['page'], $perPage, $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createOrganizer(object $user, string $table, array $payload): array
    {
        $name = trim((string) ($payload['name'] ?? ''));
        $id = Guid::newHex();
        $now = MealieDb::now();
        $row = [
            'id' => $id,
            'group_id' => $user->group_id,
            'name' => $name,
            'slug' => $this->uniqueSlug($table, $user->group_id, Str::slug($name) ?: 'item'),
            'created_at' => $now,
            'update_at' => $now,
        ];
        if ($table === 'tools') {
            $row['on_hand'] = 0;
        }
        MealieDb::table($table)->insert($row);

        return $this->organizer((object) $row, $table);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function organizerBySlug(object $user, string $table, string $slug): ?array
    {
        $row = MealieDb::table($table)->where('group_id', $user->group_id)->where('slug', $slug)->first();

        return $row === null ? null : $this->organizer($row, $table);
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function emptyOrganizers(object $user, string $table): array
    {
        $foreign = $table === 'tags' ? 'tag_id' : 'category_id';
        $pivot = $table === 'tags' ? 'recipes_to_tags' : 'recipes_to_categories';
        $used = MealieDb::table($pivot)->pluck($foreign);
        $builder = MealieDb::table($table)->where('group_id', $user->group_id);
        if ($used->isNotEmpty()) {
            $builder->whereNotIn('id', $used);
        }

        return $builder->orderBy('name')->get()
            ->map(fn ($row) => $this->organizer($row, $table))->all();
    }

    /**
     * @param  list<string>  $sourceIds
     * @return array<string, mixed>|null
     */
    public function mergeOrganizers(object $user, string $table, string $targetId, array $sourceIds): ?array
    {
        $target = Guid::hex($targetId);
        if ($target === null) {
            return null;
        }
        $row = MealieDb::table($table)->where('id', $target)->where('group_id', $user->group_id)->first();
        if ($row === null) {
            return null;
        }
        $foreign = match ($table) {
            'tags' => 'tag_id',
            'tools' => 'tool_id',
            default => 'category_id',
        };
        $pivot = match ($table) {
            'tags' => 'recipes_to_tags',
            'tools' => 'recipes_to_tools',
            default => 'recipes_to_categories',
        };
        foreach ($sourceIds as $sourceId) {
            $source = Guid::hex($sourceId);
            if ($source === null || $source === $target) {
                continue;
            }
            MealieDb::table($pivot)->where($foreign, $source)->update([$foreign => $target]);
            MealieDb::table($table)->where('id', $source)->where('group_id', $user->group_id)->delete();
        }

        return $this->organizer(MealieDb::table($table)->where('id', $target)->first(), $table);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function food(object $user, string $id): ?array
    {
        $hex = Guid::hex($id);
        $row = $hex === null ? null : MealieDb::table('ingredient_foods')->where('id', $hex)->where('group_id', $user->group_id)->first();

        return $row === null ? null : [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'pluralName' => $row->plural_name,
            'description' => $row->description ?? '',
            'groupId' => Guid::dashed($row->group_id),
        ];
    }

    /**
     * @return array<string, mixed>|null
     */
    public function unit(object $user, string $id): ?array
    {
        $hex = Guid::hex($id);
        $row = $hex === null ? null : MealieDb::table('ingredient_units')->where('id', $hex)->where('group_id', $user->group_id)->first();

        return $row === null ? null : [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'abbreviation' => $row->abbreviation,
            'description' => $row->description ?? '',
            'groupId' => Guid::dashed($row->group_id),
        ];
    }

    /**
     * @param  list<string>  $sourceIds
     */
    public function mergeNamed(object $user, string $table, string $targetId, array $sourceIds, string $column): bool
    {
        $target = Guid::hex($targetId);
        if ($target === null || ! MealieDb::table($table)->where('id', $target)->where('group_id', $user->group_id)->exists()) {
            return false;
        }
        foreach ($sourceIds as $sourceId) {
            $source = Guid::hex($sourceId);
            if ($source === null || $source === $target) {
                continue;
            }
            MealieDb::table('recipes_ingredients')->where($column, $source)->update([$column => $target]);
            MealieDb::table($table)->where('id', $source)->where('group_id', $user->group_id)->delete();
        }

        return true;
    }

    public function deleteOrganizer(object $user, string $table, string $id): bool
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return false;
        }

        return MealieDb::table($table)->where('group_id', $user->group_id)->where('id', $hex)->delete() > 0;
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateOrganizer(object $user, string $table, string $id, array $payload): ?array
    {
        $hex = Guid::hex($id);
        $row = $hex ? MealieDb::table($table)->where('group_id', $user->group_id)->where('id', $hex)->first() : null;
        if ($row === null) {
            return null;
        }
        $name = trim((string) ($payload['name'] ?? $row->name));
        $fields = ['name' => $name, 'update_at' => MealieDb::now()];
        if ($name !== $row->name) {
            $fields['slug'] = $this->uniqueSlug($table, $user->group_id, Str::slug($name) ?: $row->slug);
        }
        MealieDb::table($table)->where('id', $hex)->update($fields);

        return $this->organizer(MealieDb::table($table)->where('id', $hex)->first(), $table);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createFood(object $user, array $payload): array
    {
        return $this->createNamed($user, 'ingredient_foods', $payload, [
            'plural_name' => $payload['pluralName'] ?? $payload['plural_name'] ?? null,
            'description' => $payload['description'] ?? '',
            'name_normalized' => Str::lower((string) ($payload['name'] ?? '')),
            'on_hand' => 0,
        ]);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createUnit(object $user, array $payload): array
    {
        return $this->createNamed($user, 'ingredient_units', $payload, [
            'plural_name' => $payload['pluralName'] ?? null,
            'description' => $payload['description'] ?? '',
            'abbreviation' => $payload['abbreviation'] ?? '',
            'fraction' => JsonShape::bool($payload['fraction'] ?? false) ? 1 : 0,
            'use_abbreviation' => JsonShape::bool($payload['useAbbreviation'] ?? false) ? 1 : 0,
            'name_normalized' => Str::lower((string) ($payload['name'] ?? '')),
        ]);
    }

    /**
     * @return array<string, mixed>
     */
    public function foods(object $user, Request $request): array
    {
        return $this->namedPage($user, $request, 'ingredient_foods', function ($row) {
            return [
                'id' => Guid::dashed($row->id),
                'groupId' => Guid::dashed($row->group_id),
                'name' => $row->name,
                'pluralName' => $row->plural_name,
                'description' => $row->description ?? '',
                'labelId' => Guid::dashed($row->label_id),
                'onHand' => (bool) $row->on_hand,
                'aliases' => [],
                'substitutions' => [],
                'householdsWithIngredientFood' => [],
                'extras' => new \stdClass,
            ];
        });
    }

    /**
     * @return array<string, mixed>
     */
    public function units(object $user, Request $request): array
    {
        return $this->namedPage($user, $request, 'ingredient_units', function ($row) {
            return [
                'id' => Guid::dashed($row->id),
                'groupId' => Guid::dashed($row->group_id),
                'name' => $row->name,
                'pluralName' => $row->plural_name,
                'description' => $row->description ?? '',
                'abbreviation' => $row->abbreviation,
                'pluralAbbreviation' => $row->plural_abbreviation,
                'fraction' => (bool) $row->fraction,
                'useAbbreviation' => (bool) $row->use_abbreviation,
                'extras' => new \stdClass,
            ];
        });
    }

    /**
     * @return array<string, mixed>
     */
    public function labels(object $user, Request $request): array
    {
        return $this->namedPage($user, $request, 'multi_purpose_labels', fn ($row) => [
            'id' => Guid::dashed($row->id),
            'groupId' => Guid::dashed($row->group_id),
            'name' => $row->name,
            'color' => $row->color,
        ]);
    }

    /**
     * @return array<string, mixed>
     */
    public function cookbooks(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('cookbooks')->where('household_id', $user->household_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('position')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->cookbookOut($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createCookbook(object $user, array $payload): array
    {
        $name = trim((string) ($payload['name'] ?? 'Cookbook'));
        $slug = $this->uniqueSlug('cookbooks', $user->group_id, $this->slug($name));
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('cookbooks')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'household_id' => $user->household_id,
            'name' => $name,
            'slug' => $slug,
            'description' => (string) ($payload['description'] ?? ''),
            'position' => (int) ($payload['position'] ?? 1),
            'public' => JsonShape::bool($payload['public'] ?? false) ? 1 : 0,
            'query_filter_string' => (string) ($payload['queryFilterString'] ?? $payload['query_filter_string'] ?? ''),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->cookbookOut(MealieDb::table('cookbooks')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateCookbook(object $user, string $id, array $payload): ?array
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table('cookbooks')->where('id', $hex)->where('household_id', $user->household_id)->first();
        if ($row === null) {
            return null;
        }
        $name = trim((string) ($payload['name'] ?? $row->name));
        MealieDb::table('cookbooks')->where('id', $hex)->update([
            'name' => $name,
            'slug' => $name === $row->name ? $row->slug : $this->uniqueSlug('cookbooks', $user->group_id, $this->slug($name)),
            'description' => (string) ($payload['description'] ?? $row->description),
            'position' => (int) ($payload['position'] ?? $row->position),
            'public' => array_key_exists('public', $payload) ? (JsonShape::bool($payload['public']) ? 1 : 0) : $row->public,
            'query_filter_string' => (string) ($payload['queryFilterString'] ?? $payload['query_filter_string'] ?? $row->query_filter_string),
            'update_at' => MealieDb::now(),
        ]);

        return $this->cookbookOut(MealieDb::table('cookbooks')->where('id', $hex)->first());
    }

    public function deleteCookbook(object $user, string $id): bool
    {
        $hex = Guid::hex($id);

        return $hex !== null && MealieDb::table('cookbooks')->where('id', $hex)->where('household_id', $user->household_id)->delete() > 0;
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createLabel(object $user, array $payload): array
    {
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('multi_purpose_labels')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'name' => trim((string) ($payload['name'] ?? 'Label')),
            'color' => (string) ($payload['color'] ?? '#959595'),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->labelOut(MealieDb::table('multi_purpose_labels')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateLabel(object $user, string $id, array $payload): ?array
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table('multi_purpose_labels')->where('id', $hex)->where('group_id', $user->group_id)->first();
        if ($row === null) {
            return null;
        }
        MealieDb::table('multi_purpose_labels')->where('id', $hex)->update([
            'name' => trim((string) ($payload['name'] ?? $row->name)),
            'color' => (string) ($payload['color'] ?? $row->color),
            'update_at' => MealieDb::now(),
        ]);

        return $this->labelOut(MealieDb::table('multi_purpose_labels')->where('id', $hex)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateFood(object $user, string $id, array $payload): ?array
    {
        return $this->updateNamed($user, 'ingredient_foods', $id, $payload, [
            'plural_name' => $payload['pluralName'] ?? null,
            'description' => $payload['description'] ?? '',
            'on_hand' => JsonShape::bool($payload['onHand'] ?? $payload['on_hand'] ?? false) ? 1 : 0,
        ]);
    }

    public function deleteFood(object $user, string $id): bool
    {
        return $this->deleteNamed($user, 'ingredient_foods', $id);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateUnit(object $user, string $id, array $payload): ?array
    {
        return $this->updateNamed($user, 'ingredient_units', $id, $payload, [
            'plural_name' => $payload['pluralName'] ?? null,
            'description' => $payload['description'] ?? '',
            'abbreviation' => $payload['abbreviation'] ?? '',
            'fraction' => JsonShape::bool($payload['fraction'] ?? false) ? 1 : 0,
            'use_abbreviation' => JsonShape::bool($payload['useAbbreviation'] ?? false) ? 1 : 0,
        ]);
    }

    public function deleteUnit(object $user, string $id): bool
    {
        return $this->deleteNamed($user, 'ingredient_units', $id);
    }

    public function deleteLabel(object $user, string $id): bool
    {
        $hex = Guid::hex($id);

        return $hex !== null && MealieDb::table('multi_purpose_labels')->where('id', $hex)->where('group_id', $user->group_id)->delete() > 0;
    }

    /**
     * @return array<string, mixed>
     */
    private function cookbookOut(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'slug' => $row->slug,
            'description' => $row->description ?? '',
            'position' => (int) $row->position,
            'public' => (bool) $row->public,
            'groupId' => Guid::dashed($row->group_id),
            'householdId' => Guid::dashed($row->household_id),
            'queryFilterString' => $row->query_filter_string ?? '',
            'queryFilter' => new \stdClass,
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function labelOut(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'groupId' => Guid::dashed($row->group_id),
            'name' => $row->name,
            'color' => $row->color,
        ];
    }

    private function slug(string $name): string
    {
        $slug = strtolower(trim(preg_replace('/[^a-z0-9]+/i', '-', $name) ?? 'item', '-'));

        return $slug !== '' ? $slug : 'item';
    }

    /**
     * @param  callable(object): array<string, mixed>  $map
     * @return array<string, mixed>
     */
    private function namedPage(object $user, Request $request, string $table, callable $map): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table($table)->where('group_id', $user->group_id);
        if (is_string($query['search']) && $query['search'] !== '') {
            $builder->where('name', 'like', '%'.$query['search'].'%');
        }
        $total = (clone $builder)->count();
        $perPage = $query['perPage'] < 0 ? max($total, 1) : $query['perPage'];
        $rows = $builder->orderBy('name')->forPage($query['page'], $perPage)->get();

        return Pages::make($rows->map($map)->all(), $query['page'], $perPage, $total);
    }

    /**
     * @return array<string, mixed>
     */
    private function organizer(object $row, string $table): array
    {
        $foreign = match ($table) {
            'tags' => 'tag_id',
            'tools' => 'tool_id',
            default => 'category_id',
        };
        $pivot = match ($table) {
            'tags' => 'recipes_to_tags',
            'tools' => 'recipes_to_tools',
            default => 'recipes_to_categories',
        };

        return [
            'id' => Guid::dashed($row->id),
            'groupId' => Guid::dashed($row->group_id),
            'name' => $row->name,
            'slug' => $row->slug,
            'recipeCount' => MealieDb::table($pivot)->where($foreign, $row->id)->count(),
        ];
    }

    /**
     * @param  array<string, mixed>  $payload
     * @param  array<string, mixed>  $extra
     * @return array<string, mixed>
     */
    private function createNamed(object $user, string $table, array $payload, array $extra): array
    {
        $name = trim((string) ($payload['name'] ?? ''));
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table($table)->insert(array_merge($extra, [
            'id' => $id,
            'group_id' => $user->group_id,
            'name' => $name,
            'created_at' => $now,
            'update_at' => $now,
        ]));
        $row = MealieDb::table($table)->where('id', $id)->first();

        return $table === 'ingredient_foods'
            ? ['id' => Guid::dashed($row->id), 'name' => $row->name, 'pluralName' => $row->plural_name, 'description' => $row->description ?? '', 'groupId' => Guid::dashed($row->group_id)]
            : ['id' => Guid::dashed($row->id), 'name' => $row->name, 'abbreviation' => $row->abbreviation, 'description' => $row->description ?? '', 'groupId' => Guid::dashed($row->group_id)];
    }

    /**
     * @param  array<string, mixed>  $payload
     * @param  array<string, mixed>  $extra
     * @return array<string, mixed>|null
     */
    private function updateNamed(object $user, string $table, string $id, array $payload, array $extra): ?array
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table($table)->where('id', $hex)->where('group_id', $user->group_id)->first();
        if ($row === null) {
            return null;
        }
        MealieDb::table($table)->where('id', $hex)->update(array_merge($extra, [
            'name' => trim((string) ($payload['name'] ?? $row->name)),
            'update_at' => MealieDb::now(),
        ]));
        $updated = MealieDb::table($table)->where('id', $hex)->first();

        return $table === 'ingredient_foods'
            ? ['id' => Guid::dashed($updated->id), 'name' => $updated->name, 'pluralName' => $updated->plural_name, 'description' => $updated->description ?? '', 'groupId' => Guid::dashed($updated->group_id)]
            : ['id' => Guid::dashed($updated->id), 'name' => $updated->name, 'abbreviation' => $updated->abbreviation, 'description' => $updated->description ?? '', 'groupId' => Guid::dashed($updated->group_id)];
    }

    private function deleteNamed(object $user, string $table, string $id): bool
    {
        $hex = Guid::hex($id);

        return $hex !== null && MealieDb::table($table)->where('id', $hex)->where('group_id', $user->group_id)->delete() > 0;
    }

    private function uniqueSlug(string $table, string $groupId, string $slug): string
    {
        $candidate = $slug;
        $i = 2;
        while (MealieDb::table($table)->where('group_id', $groupId)->where('slug', $candidate)->exists()) {
            $candidate = $slug.'-'.$i;
            $i++;
        }

        return $candidate;
    }
}
