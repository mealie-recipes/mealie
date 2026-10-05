<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\Images;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

final class RecipeService
{
    /**
     * @return array<string, mixed>
     */
    public function page(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('recipes')->where('group_id', $user->group_id);
        if (is_string($query['search']) && $query['search'] !== '') {
            $builder->where('name', 'like', '%'.$query['search'].'%');
        }

        $order = in_array($query['orderBy'], ['name', 'slug', 'created_at', 'date_added', 'rating', 'last_made'], true)
            ? (string) $query['orderBy']
            : 'created_at';
        $total = (clone $builder)->count();
        $perPage = $query['perPage'] < 0 ? $total : $query['perPage'];
        $rows = $builder
            ->orderBy($order, $query['direction'])
            ->when($perPage > 0, fn ($q) => $q->forPage($query['page'], $perPage))
            ->get()
            ->all();

        return Pages::make(
            array_map(fn ($row) => $this->summary($row), $rows),
            $query['page'],
            $perPage > 0 ? $perPage : $total,
            $total,
        );
    }

    /**
     * @return array<string, mixed>|null
     */
    public function find(object $user, string $slug): ?array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return null;
        }

        return $this->detailRow($row);
    }

    /**
     * @return array<string, mixed>
     */
    public function card(object $row): array
    {
        return $this->summary($row);
    }

    /**
     * @return array<string, mixed>
     */
    public function detailRow(object $row): array
    {
        $summary = $this->summary($row);
        $id = $row->id;
        $summary['recipeIngredient'] = $this->ingredients($id);
        $summary['recipeInstructions'] = $this->instructions($id);
        $summary['nutrition'] = $this->nutrition($id);
        $summary['settings'] = $this->settings($id);
        $summary['assets'] = [];
        $summary['notes'] = $this->notes($id);
        $summary['extras'] = new \stdClass;
        $summary['comments'] = $this->comments($id);

        return $summary;
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function create(object $user, array $payload): array
    {
        $name = trim((string) ($payload['name'] ?? ''));
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('recipes')->insert([
            'id' => $id,
            'slug' => $this->uniqueSlug($user, Str::slug($name) ?: 'recipe'),
            'group_id' => $user->group_id,
            'user_id' => $user->id,
            'name' => $name,
            'name_normalized' => Str::lower($name),
            'description' => '',
            'recipe_servings' => 0,
            'recipe_yield_quantity' => 0,
            'date_added' => substr($now, 0, 10),
            'created_at' => $now,
            'update_at' => $now,
        ]);
        MealieDb::table('recipe_settings')->insert([
            'recipe_id' => $id,
            'public' => 0,
            'show_nutrition' => 0,
            'show_assets' => 0,
            'landscape_view' => 0,
            'disable_amount' => 1,
            'disable_comments' => 0,
            'locked' => 0,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        $row = MealieDb::table('recipes')->where('id', $id)->first();

        return $this->find($user, (string) $row->slug) ?? [];
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function update(object $user, string $slug, array $payload): ?array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return null;
        }

        $fields = [];
        foreach (['name', 'description', 'recipe_yield', 'total_time', 'prep_time', 'cook_time', 'perform_time', 'org_url'] as $column) {
            $camel = JsonShape::key($column);
            if (array_key_exists($column, $payload) || array_key_exists($camel, $payload)) {
                $fields[$column] = $payload[$column] ?? $payload[$camel];
            }
        }
        foreach (['recipe_servings', 'recipe_yield_quantity'] as $column) {
            $camel = JsonShape::key($column);
            if (array_key_exists($column, $payload) || array_key_exists($camel, $payload)) {
                $fields[$column] = $payload[$column] ?? $payload[$camel] ?? 0;
            }
        }
        if (isset($fields['name'])) {
            $fields['name_normalized'] = Str::lower((string) $fields['name']);
            $fields['slug'] = $this->uniqueSlug($user, Str::slug((string) $fields['name']) ?: $row->slug, $row->id);
        }
        $fields['update_at'] = MealieDb::now();
        $fields['date_updated'] = MealieDb::now();
        MealieDb::table('recipes')->where('id', $row->id)->update($fields);

        $ingredients = $payload['recipeIngredient'] ?? $payload['recipe_ingredient'] ?? null;
        if (is_array($ingredients)) {
            $this->replaceIngredients($row->id, $ingredients);
        }
        $instructions = $payload['recipeInstructions'] ?? $payload['recipe_instructions'] ?? null;
        if (is_array($instructions)) {
            $this->replaceInstructions($row->id, $instructions);
        }

        $updated = MealieDb::table('recipes')->where('id', $row->id)->first();

        return $this->find($user, (string) $updated->slug);
    }

    public function delete(object $user, string $slug): bool
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return false;
        }

        foreach (['recipes_ingredients', 'recipe_instructions', 'recipe_nutrition', 'recipe_settings', 'notes', 'recipe_comments'] as $table) {
            MealieDb::table($table)->where('recipe_id', $row->id)->delete();
        }
        foreach (['recipes_to_categories', 'recipes_to_tags', 'recipes_to_tools'] as $table) {
            MealieDb::table($table)->where('recipe_id', $row->id)->delete();
        }
        MealieDb::table('recipes')->where('id', $row->id)->delete();

        return true;
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function comments(string $recipeId): array
    {
        return MealieDb::table('recipe_comments')->where('recipe_id', $recipeId)->orderBy('created_at')->get()
            ->map(fn ($row) => $this->commentOut($row))->all();
    }

    /**
     * @return array<string, mixed>
     */
    public function commentPage(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $recipeIds = MealieDb::table('recipes')->where('group_id', $user->group_id)->pluck('id');
        $builder = MealieDb::table('recipe_comments')->whereIn('recipe_id', $recipeIds);
        $total = (clone $builder)->count();
        $rows = $builder->orderByDesc('created_at')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->commentOut($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function updateComment(object $user, string $id, string $text): ?array
    {
        $row = $this->ownedComment($user, $id);
        if ($row === null || trim($text) === '') {
            return null;
        }
        MealieDb::table('recipe_comments')->where('id', $row->id)->update([
            'text' => trim($text),
            'update_at' => MealieDb::now(),
        ]);

        return $this->commentOut(MealieDb::table('recipe_comments')->where('id', $row->id)->first());
    }

    public function deleteComment(object $user, string $id): bool
    {
        $row = $this->ownedComment($user, $id);
        if ($row === null) {
            return false;
        }
        MealieDb::table('recipe_comments')->where('id', $row->id)->delete();

        return true;
    }

    /**
     * @return array<string, mixed>
     */
    public function shares(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('recipe_share_tokens')->where('group_id', $user->group_id);
        $recipeId = Guid::hex((string) $request->query('recipe_id', $request->query('recipeId', '')));
        if ($recipeId !== null) {
            $builder->where('recipe_id', $recipeId);
        }
        $total = (clone $builder)->count();
        $rows = $builder->orderByDesc('created_at')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->shareOut($row, false))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function createShare(object $user, array $payload): ?array
    {
        $recipeId = Guid::hex((string) ($payload['recipeId'] ?? $payload['recipe_id'] ?? ''));
        if ($recipeId === null) {
            return null;
        }
        $recipe = MealieDb::table('recipes')->where('id', $recipeId)->where('group_id', $user->group_id)->first();
        if ($recipe === null) {
            return null;
        }
        $id = Guid::newHex();
        $now = MealieDb::now();
        $expires = $payload['expiresAt'] ?? $payload['expires_at'] ?? gmdate('Y-m-d H:i:s', time() + 30 * 86400);
        MealieDb::table('recipe_share_tokens')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'recipe_id' => $recipeId,
            'expires_at' => is_string($expires) ? str_replace('T', ' ', substr($expires, 0, 19)) : $now,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->shareOut(MealieDb::table('recipe_share_tokens')->where('id', $id)->first(), true);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function share(object $user, string $id): ?array
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table('recipe_share_tokens')->where('id', $hex)->where('group_id', $user->group_id)->first();

        return $row === null ? null : $this->shareOut($row, true);
    }

    public function deleteShare(object $user, string $id): bool
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return false;
        }

        return MealieDb::table('recipe_share_tokens')->where('id', $hex)->where('group_id', $user->group_id)->delete() > 0;
    }

    /**
     * @return array<string, mixed>|null
     */
    public function sharedRecipe(string $token): ?array
    {
        $hex = Guid::hex($token);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table('recipe_share_tokens')->where('id', $hex)->first();
        if ($row === null || strtotime((string) $row->expires_at) < time()) {
            return null;
        }
        $recipe = MealieDb::table('recipes')->where('id', $row->recipe_id)->first();

        return $recipe === null ? null : $this->detailRow($recipe);
    }

    /**
     * @return array<string, mixed>
     */
    /**
     * @return array{image: string}|null
     */
    public function saveImage(object $user, string $slug, string $bytes): ?array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null || $bytes === '') {
            return null;
        }
        $key = bin2hex(random_bytes(6));
        Images::writeSet($this->imageDir($row->id), $bytes);
        MealieDb::table('recipes')->where('id', $row->id)->update([
            'image' => $key,
            'update_at' => MealieDb::now(),
        ]);

        return ['image' => $key];
    }

    public function deleteImage(object $user, string $slug): bool
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return false;
        }
        Images::removeSet($this->imageDir($row->id));
        MealieDb::table('recipes')->where('id', $row->id)->update([
            'image' => null,
            'update_at' => MealieDb::now(),
        ]);

        return true;
    }

    /**
     * @return list<array<string, mixed>>|null
     */
    public function assets(object $user, string $slug): ?array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return null;
        }

        return MealieDb::table('recipe_assets')->where('recipe_id', $row->id)->orderBy('name')->get()
            ->map(fn ($asset) => [
                'id' => (int) $asset->id,
                'name' => $asset->name,
                'icon' => $asset->icon,
                'fileName' => $asset->file_name,
            ])->all();
    }

    /**
     * @return array<string, mixed>|null
     */
    public function storeAsset(object $user, string $slug, string $name, string $bytes): ?array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null || $bytes === '') {
            return null;
        }
        $safe = preg_replace('/[^A-Za-z0-9._-]/', '', $name) ?: 'asset.bin';
        $dir = rtrim((string) config('mealie.data_dir'), '/').'/recipes/'.Guid::dashed($row->id).'/assets';
        if (! is_dir($dir) && ! mkdir($dir, 0775, true) && ! is_dir($dir)) {
            return null;
        }
        file_put_contents($dir.'/'.$safe, $bytes);
        $id = MealieDb::table('recipe_assets')->insertGetId([
            'recipe_id' => $row->id,
            'name' => $safe,
            'icon' => 'mdi-file',
            'file_name' => $safe,
            'created_at' => MealieDb::now(),
            'update_at' => MealieDb::now(),
        ]);

        return ['id' => (int) $id, 'name' => $safe, 'icon' => 'mdi-file', 'fileName' => $safe];
    }

    public function addComment(object $user, string $slug, string $text): array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return [];
        }
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('recipe_comments')->insert([
            'id' => $id,
            'text' => $text,
            'recipe_id' => $row->id,
            'user_id' => $user->id,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->commentOut(MealieDb::table('recipe_comments')->where('id', $id)->first());
    }

    /**
     * @return array<string, mixed>
     */
    private function commentOut(object $row): array
    {
        $author = MealieDb::table('users')->where('id', $row->user_id)->first();

        return [
            'id' => Guid::dashed($row->id),
            'text' => $row->text,
            'recipeId' => Guid::dashed($row->recipe_id),
            'userId' => Guid::dashed($row->user_id),
            'createdAt' => JsonShape::dateTime($row->created_at),
            'updatedAt' => JsonShape::dateTime($row->update_at),
            'user' => [
                'id' => Guid::dashed($row->user_id),
                'username' => $author->username ?? null,
                'admin' => JsonShape::bool($author->admin ?? false),
                'fullName' => $author->full_name ?? null,
            ],
        ];
    }

    private function ownedComment(object $user, string $id): ?object
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table('recipe_comments')->where('id', $hex)->first();
        if ($row === null) {
            return null;
        }
        $recipe = MealieDb::table('recipes')->where('id', $row->recipe_id)->where('group_id', $user->group_id)->first();

        return $recipe === null ? null : $row;
    }

    /**
     * @return array<string, mixed>
     */
    private function shareOut(object $row, bool $withRecipe): array
    {
        $out = [
            'id' => Guid::dashed($row->id),
            'groupId' => Guid::dashed($row->group_id),
            'recipeId' => Guid::dashed($row->recipe_id),
            'createdAt' => JsonShape::dateTime($row->created_at),
            'expiresAt' => JsonShape::dateTime($row->expires_at),
        ];
        if ($withRecipe) {
            $recipe = MealieDb::table('recipes')->where('id', $row->recipe_id)->first();
            $out['recipe'] = $recipe === null ? null : $this->detailRow($recipe);
        }

        return $out;
    }

    private function findRow(object $user, string $slug): ?object
    {
        $query = MealieDb::table('recipes')->where('group_id', $user->group_id);
        $hex = Guid::hex($slug);

        return (clone $query)->where('slug', $slug)->first()
            ?? ($hex ? (clone $query)->where('id', $hex)->first() : null);
    }

    /**
     * @return array<string, mixed>
     */
    private function summary(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'userId' => Guid::dashed($row->user_id),
            'householdId' => Guid::dashed($this->householdId($row->user_id)),
            'groupId' => Guid::dashed($row->group_id),
            'name' => $row->name,
            'slug' => $row->slug,
            'image' => $row->image,
            'recipeServings' => (float) ($row->recipe_servings ?? 0),
            'recipeYieldQuantity' => (float) ($row->recipe_yield_quantity ?? 0),
            'recipeYield' => $row->recipe_yield,
            'totalTime' => $row->total_time,
            'prepTime' => $row->prep_time,
            'cookTime' => $row->cook_time,
            'performTime' => $row->perform_time,
            'description' => $row->description ?? '',
            'recipeCategory' => $this->linked($row->id, 'recipes_to_categories', 'category_id', 'categories'),
            'tags' => $this->linked($row->id, 'recipes_to_tags', 'tag_id', 'tags'),
            'tools' => $this->linked($row->id, 'recipes_to_tools', 'tool_id', 'tools'),
            'rating' => $row->rating === null ? null : (float) $row->rating,
            'orgURL' => $row->org_url,
            'dateAdded' => JsonShape::date($row->date_added),
            'dateUpdated' => JsonShape::dateTime($row->date_updated),
            'createdAt' => JsonShape::dateTime($row->created_at),
            'updatedAt' => JsonShape::dateTime($row->update_at),
            'lastMade' => JsonShape::dateTime($row->last_made),
        ];
    }

    private function householdId(?string $userId): ?string
    {
        if ($userId === null) {
            return null;
        }

        return MealieDb::table('users')->where('id', $userId)->value('household_id');
    }

    /**
     * @return list<array<string, mixed>>
     */
    private function linked(string $recipeId, string $pivot, string $foreign, string $table): array
    {
        $ids = MealieDb::table($pivot)->where('recipe_id', $recipeId)->pluck($foreign);
        if ($ids->isEmpty()) {
            return [];
        }

        return MealieDb::table($table)->whereIn('id', $ids)->get()->map(function ($item) use ($table) {
            $count = MealieDb::table($table === 'categories' ? 'recipes_to_categories' : ($table === 'tags' ? 'recipes_to_tags' : 'recipes_to_tools'))
                ->where($table === 'tools' ? 'tool_id' : ($table === 'tags' ? 'tag_id' : 'category_id'), $item->id)
                ->count();

            return [
                'id' => Guid::dashed($item->id),
                'groupId' => Guid::dashed($item->group_id),
                'name' => $item->name,
                'slug' => $item->slug,
                'recipeCount' => $count,
            ];
        })->all();
    }

    /**
     * @return list<array<string, mixed>>
     */
    private function ingredients(string $recipeId): array
    {
        return MealieDb::table('recipes_ingredients')->where('recipe_id', $recipeId)->orderBy('position')->get()
            ->map(function ($row) {
                $food = $row->food_id ? MealieDb::table('ingredient_foods')->where('id', $row->food_id)->first() : null;
                $unit = $row->unit_id ? MealieDb::table('ingredient_units')->where('id', $row->unit_id)->first() : null;
                $quantity = $row->quantity === null ? 0 : (float) $row->quantity;
                $display = trim(implode(' ', array_filter([
                    $quantity ? rtrim(rtrim(number_format($quantity, 3, '.', ''), '0'), '.') : null,
                    $unit->name ?? null,
                    $food->name ?? null,
                    $row->note,
                ])));

                return [
                    'quantity' => $quantity,
                    'unit' => $unit ? ['id' => Guid::dashed($unit->id), 'name' => $unit->name, 'pluralName' => $unit->plural_name, 'description' => $unit->description ?? '', 'abbreviation' => $unit->abbreviation, 'useAbbreviation' => JsonShape::bool($unit->use_abbreviation), 'fraction' => JsonShape::bool($unit->fraction)] : null,
                    'food' => $food ? ['id' => Guid::dashed($food->id), 'name' => $food->name, 'pluralName' => $food->plural_name, 'description' => $food->description ?? ''] : null,
                    'note' => $row->note ?? '',
                    'display' => $row->original_text ?: $display,
                    'title' => $row->title,
                    'originalText' => $row->original_text,
                    'referenceId' => Guid::dashed($row->reference_id) ?? Guid::dashed(Guid::newHex()),
                    'substitutions' => [],
                ];
            })->all();
    }

    /**
     * @return list<array<string, mixed>>
     */
    private function instructions(string $recipeId): array
    {
        return MealieDb::table('recipe_instructions')->where('recipe_id', $recipeId)->orderBy('position')->get()
            ->map(fn ($row) => [
                'id' => Guid::dashed($row->id),
                'title' => $row->title ?? '',
                'summary' => $row->summary ?? '',
                'text' => $row->text ?? '',
                'ingredientReferences' => [],
                'noteReferences' => [],
            ])->all();
    }

    /**
     * @return array<string, mixed>|null
     */
    private function nutrition(string $recipeId): ?array
    {
        $row = MealieDb::table('recipe_nutrition')->where('recipe_id', $recipeId)->first();
        if ($row === null) {
            return null;
        }

        return [
            'calories' => $row->calories,
            'carbohydrateContent' => $row->carbohydrate_content,
            'cholesterolContent' => $row->cholesterol_content,
            'fatContent' => $row->fat_content,
            'fiberContent' => $row->fiber_content,
            'proteinContent' => $row->protein_content,
            'saturatedFatContent' => $row->saturated_fat_content,
            'sodiumContent' => $row->sodium_content,
            'sugarContent' => $row->sugar_content,
            'transFatContent' => $row->trans_fat_content,
            'unsaturatedFatContent' => $row->unsaturated_fat_content,
        ];
    }

    /**
     * @return array<string, mixed>|null
     */
    private function settings(string $recipeId): ?array
    {
        $row = MealieDb::table('recipe_settings')->where('recipe_id', $recipeId)->first();
        if ($row === null) {
            return null;
        }

        return [
            'public' => JsonShape::bool($row->public),
            'showNutrition' => JsonShape::bool($row->show_nutrition),
            'showAssets' => JsonShape::bool($row->show_assets),
            'landscapeView' => JsonShape::bool($row->landscape_view),
            'disableComments' => JsonShape::bool($row->disable_comments),
            'locked' => JsonShape::bool($row->locked),
        ];
    }

    /**
     * @return list<array<string, mixed>>
     */
    private function notes(string $recipeId): array
    {
        return MealieDb::table('notes')->where('recipe_id', $recipeId)->get()->map(fn ($row) => [
            'id' => (int) $row->id,
            'title' => $row->title ?? '',
            'text' => $row->text ?? '',
            'referenceId' => Guid::dashed($row->reference_id),
        ])->all();
    }

    /**
     * @param  list<array<string, mixed>>  $ingredients
     */
    private function replaceIngredients(string $recipeId, array $ingredients): void
    {
        MealieDb::table('recipes_ingredients')->where('recipe_id', $recipeId)->delete();
        $now = MealieDb::now();
        foreach (array_values($ingredients) as $position => $ingredient) {
            $food = $ingredient['food'] ?? null;
            $unit = $ingredient['unit'] ?? null;
            MealieDb::table('recipes_ingredients')->insert([
                'position' => $position,
                'recipe_id' => $recipeId,
                'title' => $ingredient['title'] ?? null,
                'note' => $ingredient['note'] ?? '',
                'food_id' => is_array($food) ? Guid::hex($food['id'] ?? null) : null,
                'unit_id' => is_array($unit) ? Guid::hex($unit['id'] ?? null) : null,
                'quantity' => $ingredient['quantity'] ?? 0,
                'original_text' => $ingredient['originalText'] ?? $ingredient['original_text'] ?? null,
                'reference_id' => Guid::hex($ingredient['referenceId'] ?? $ingredient['reference_id'] ?? null) ?? Guid::newHex(),
                'created_at' => $now,
                'update_at' => $now,
            ]);
        }
    }

    /**
     * @param  list<array<string, mixed>>  $instructions
     */
    private function replaceInstructions(string $recipeId, array $instructions): void
    {
        MealieDb::table('recipe_instructions')->where('recipe_id', $recipeId)->delete();
        $now = MealieDb::now();
        foreach (array_values($instructions) as $position => $step) {
            MealieDb::table('recipe_instructions')->insert([
                'id' => Guid::hex($step['id'] ?? null) ?? Guid::newHex(),
                'recipe_id' => $recipeId,
                'position' => $position,
                'title' => $step['title'] ?? '',
                'text' => $step['text'] ?? '',
                'summary' => $step['summary'] ?? '',
                'created_at' => $now,
                'update_at' => $now,
            ]);
        }
    }

    /**
     * @return array<string, mixed>|null
     */
    public function touchLastMade(object $user, string $slug): ?array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return null;
        }
        MealieDb::table('recipes')->where('id', $row->id)->update([
            'last_made' => MealieDb::now(),
            'update_at' => MealieDb::now(),
        ]);

        return $this->find($user, (string) $row->slug);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function duplicate(object $user, string $slug): ?array
    {
        $row = $this->findRow($user, $slug);
        if ($row === null) {
            return null;
        }
        $copy = (array) $row;
        $copy['id'] = Guid::newHex();
        $copy['slug'] = $this->uniqueSlug($user, $row->slug.'-copy');
        $copy['name'] = $row->name.' Copy';
        $copy['name_normalized'] = Str::lower($copy['name']);
        $copy['created_at'] = MealieDb::now();
        $copy['update_at'] = MealieDb::now();
        $copy['date_added'] = substr(MealieDb::now(), 0, 10);
        unset($copy['update_at']);
        $copy['update_at'] = MealieDb::now();
        MealieDb::table('recipes')->insert($copy);
        foreach (['recipes_ingredients', 'recipe_instructions', 'recipe_nutrition', 'recipe_settings', 'notes'] as $table) {
            foreach (MealieDb::table($table)->where('recipe_id', $row->id)->get() as $child) {
                $data = (array) $child;
                $data['recipe_id'] = $copy['id'];
                if ($table === 'recipe_instructions') {
                    $data['id'] = Guid::newHex();
                } else {
                    unset($data['id']);
                }
                MealieDb::table($table)->insert($data);
            }
        }

        return $this->find($user, $copy['slug']);
    }

    /**
     * @return array{items: list<array<string, mixed>>}
     */
    public function suggestions(object $user, int $limit = 5): array
    {
        $rows = MealieDb::table('recipes')->where('group_id', $user->group_id)->inRandomOrder()->limit(max(1, $limit))->get();

        return [
            'items' => $rows->map(fn ($row) => [
                'recipe' => $this->card($row),
                'missingFoods' => [],
                'substitutedFoods' => [],
                'missingTools' => [],
            ])->all(),
        ];
    }

    /**
     * @param  array<string, mixed>  $payload
     */
    public function bulk(object $user, string $action, array $payload): void
    {
        $slugs = $payload['recipes'] ?? [];
        if (! is_array($slugs)) {
            return;
        }
        foreach ($slugs as $slug) {
            $row = $this->findRow($user, (string) $slug);
            if ($row === null) {
                continue;
            }
            match ($action) {
                'delete' => $this->delete($user, (string) $row->slug),
                'tag' => $this->linkMany($row->id, $payload['tags'] ?? [], 'recipes_to_tags', 'tag_id'),
                'categorize' => $this->linkMany($row->id, $payload['categories'] ?? [], 'recipes_to_categories', 'category_id'),
                'settings' => $this->applySettings($row->id, $payload['settings'] ?? []),
                default => null,
            };
        }
    }

    /**
     * @param  list<array<string, mixed>|string>  $items
     */
    private function linkMany(string $recipeId, array $items, string $pivot, string $column): void
    {
        foreach ($items as $item) {
            $id = Guid::hex(is_array($item) ? ($item['id'] ?? null) : $item);
            if ($id === null) {
                continue;
            }
            $exists = MealieDb::table($pivot)->where('recipe_id', $recipeId)->where($column, $id)->exists();
            if (! $exists) {
                MealieDb::table($pivot)->insert(['recipe_id' => $recipeId, $column => $id]);
            }
        }
    }

    /**
     * @param  array<string, mixed>  $settings
     */
    private function applySettings(string $recipeId, array $settings): void
    {
        $map = [
            'public' => 'public',
            'showNutrition' => 'show_nutrition',
            'showAssets' => 'show_assets',
            'landscapeView' => 'landscape_view',
            'disableComments' => 'disable_comments',
            'locked' => 'locked',
        ];
        $fields = ['update_at' => MealieDb::now()];
        foreach ($map as $key => $column) {
            if (array_key_exists($key, $settings)) {
                $fields[$column] = JsonShape::bool($settings[$key]) ? 1 : 0;
            }
        }
        MealieDb::table('recipe_settings')->where('recipe_id', $recipeId)->update($fields);
    }

    private function imageDir(string $recipeId): string
    {
        return rtrim((string) config('mealie.data_dir'), '/').'/recipes/'.Guid::dashed($recipeId).'/images';
    }

    private function uniqueSlug(object $user, string $slug, ?string $ignoreId = null): string
    {
        $base = $slug !== '' ? $slug : 'recipe';
        $candidate = $base;
        $i = 2;
        while (MealieDb::table('recipes')
            ->where('group_id', $user->group_id)
            ->where('slug', $candidate)
            ->when($ignoreId, fn ($q) => $q->where('id', '!=', $ignoreId))
            ->exists()) {
            $candidate = $base.'-'.$i;
            $i++;
        }

        return $candidate;
    }
}
