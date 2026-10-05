<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;

final class PlanService
{
    public function __construct(private readonly RecipeService $recipes) {}

    /**
     * @return array<string, mixed>
     */
    public function mealPlans(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('group_meal_plans')->where('group_id', $user->group_id);
        $start = $request->query('start_date', $request->query('startDate'));
        $end = $request->query('end_date', $request->query('endDate'));
        if (is_string($start) && $start !== '') {
            $builder->where('date', '>=', $start);
        }
        if (is_string($end) && $end !== '') {
            $builder->where('date', '<=', $end);
        }
        $total = (clone $builder)->count();
        $perPage = $query['perPage'] < 0 ? max($total, 1) : $query['perPage'];
        $rows = $builder->orderBy('date')->forPage($query['page'], $perPage)->get();

        return Pages::make($rows->map(fn ($row) => $this->planEntry($user, $row))->all(), $query['page'], $perPage, $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createMealPlan(object $user, array $payload): array
    {
        $now = MealieDb::now();
        $id = MealieDb::table('group_meal_plans')->insertGetId([
            'date' => $payload['date'] ?? substr($now, 0, 10),
            'entry_type' => $payload['entryType'] ?? $payload['entry_type'] ?? 'dinner',
            'title' => $payload['title'] ?? '',
            'text' => $payload['text'] ?? '',
            'group_id' => $user->group_id,
            'user_id' => $user->id,
            'recipe_id' => Guid::hex($payload['recipeId'] ?? $payload['recipe_id'] ?? null),
            'created_at' => $now,
            'update_at' => $now,
        ]);
        $row = MealieDb::table('group_meal_plans')->where('id', $id)->first();

        return $this->planEntry($user, $row);
    }

    public function deleteMealPlan(object $user, int $id): bool
    {
        return MealieDb::table('group_meal_plans')->where('group_id', $user->group_id)->where('id', $id)->delete() > 0;
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateMealPlan(object $user, int $id, array $payload): ?array
    {
        $row = MealieDb::table('group_meal_plans')->where('group_id', $user->group_id)->where('id', $id)->first();
        if ($row === null) {
            return null;
        }

        $fields = ['update_at' => MealieDb::now()];
        foreach (['date', 'title', 'text'] as $column) {
            if (array_key_exists($column, $payload)) {
                $fields[$column] = $payload[$column];
            }
        }
        if (array_key_exists('entryType', $payload) || array_key_exists('entry_type', $payload)) {
            $fields['entry_type'] = $payload['entryType'] ?? $payload['entry_type'];
        }
        if (array_key_exists('recipeId', $payload) || array_key_exists('recipe_id', $payload)) {
            $fields['recipe_id'] = Guid::hex($payload['recipeId'] ?? $payload['recipe_id']);
        }
        MealieDb::table('group_meal_plans')->where('id', $id)->update($fields);

        return $this->planEntry($user, MealieDb::table('group_meal_plans')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateShoppingList(object $user, string $id, array $payload): ?array
    {
        $hex = Guid::hex($id);
        $row = $hex ? MealieDb::table('shopping_lists')->where('id', $hex)->where('group_id', $user->group_id)->first() : null;
        if ($row === null) {
            return null;
        }
        if (array_key_exists('name', $payload)) {
            MealieDb::table('shopping_lists')->where('id', $hex)->update([
                'name' => $payload['name'],
                'update_at' => MealieDb::now(),
            ]);
        }

        return $this->findShoppingList($user, $id);
    }

    public function deleteShoppingList(object $user, string $id): bool
    {
        $hex = Guid::hex($id);
        $row = $hex ? MealieDb::table('shopping_lists')->where('id', $hex)->where('group_id', $user->group_id)->first() : null;
        if ($row === null) {
            return false;
        }
        $itemIds = MealieDb::table('shopping_list_items')->where('shopping_list_id', $hex)->pluck('id');
        if ($itemIds->isNotEmpty()) {
            MealieDb::table('shopping_list_item_recipe_reference')->whereIn('shopping_list_item_id', $itemIds)->delete();
        }
        MealieDb::table('shopping_list_items')->where('shopping_list_id', $hex)->delete();
        MealieDb::table('shopping_lists')->where('id', $hex)->delete();

        return true;
    }

    /**
     * @param  list<array<string, mixed>>  $items
     * @return array{createdItems: list<array<string, mixed>>, updatedItems: list<array<string, mixed>>, deletedItems: list<array<string, mixed>>}
     */
    public function createItems(object $user, array $items): array
    {
        $created = [];
        foreach ($items as $payload) {
            $item = $this->insertItem($user, $payload);
            if ($item !== null) {
                $created[] = $item;
            }
        }

        return ['createdItems' => $created, 'updatedItems' => [], 'deletedItems' => []];
    }

    /**
     * @param  list<array<string, mixed>>  $items
     * @return array{createdItems: list<array<string, mixed>>, updatedItems: list<array<string, mixed>>, deletedItems: list<array<string, mixed>>}
     */
    public function updateItems(object $user, array $items): array
    {
        $updated = [];
        foreach ($items as $payload) {
            $id = Guid::hex($payload['id'] ?? null);
            if ($id === null) {
                continue;
            }
            $item = $this->updateItem($user, $id, $payload);
            if ($item !== null) {
                $updated[] = $item;
            }
        }

        return ['createdItems' => [], 'updatedItems' => $updated, 'deletedItems' => []];
    }

    /**
     * @param  list<string>  $ids
     */
    public function deleteItems(object $user, array $ids): bool
    {
        foreach ($ids as $id) {
            $hex = Guid::hex($id);
            if ($hex === null || $this->ownedItem($user, $hex) === null) {
                continue;
            }
            MealieDb::table('shopping_list_item_recipe_reference')->where('shopping_list_item_id', $hex)->delete();
            MealieDb::table('shopping_list_items')->where('id', $hex)->delete();
        }

        return true;
    }

    /**
     * @return array<string, mixed>
     */
    /**
     * @return array<string, mixed>
     */
    public function shoppingItems(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $listIds = MealieDb::table('shopping_lists')->where('group_id', $user->group_id)->pluck('id');
        $builder = MealieDb::table('shopping_list_items')->whereIn('shopping_list_id', $listIds);
        $listId = Guid::hex((string) $request->query('shopping_list_id', $request->query('shoppingListId', '')));
        if ($listId !== null) {
            $builder->where('shopping_list_id', $listId);
        }
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('position')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->shoppingItem($user, $row))->all(), $query['page'], $query['perPage'], $total);
    }

    public function shoppingLists(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('shopping_lists')->where('group_id', $user->group_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->shoppingList($user, $row, false))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function shoppingList(object $user, object $row, bool $withItems = true): ?array
    {
        if ($row->group_id !== $user->group_id) {
            return null;
        }

        $list = [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'groupId' => Guid::dashed($row->group_id),
            'userId' => Guid::dashed($row->user_id),
            'householdId' => Guid::dashed($user->household_id),
            'createdAt' => JsonShape::dateTime($row->created_at),
            'updatedAt' => JsonShape::dateTime($row->update_at),
            'listItems' => [],
            'recipeReferences' => MealieDb::table('shopping_list_recipe_reference')
                ->where('shopping_list_id', $row->id)
                ->get()
                ->map(fn ($ref) => [
                    'id' => Guid::dashed($ref->id),
                    'shoppingListId' => Guid::dashed($ref->shopping_list_id),
                    'recipeId' => Guid::dashed($ref->recipe_id),
                    'recipeQuantity' => (float) $ref->recipe_quantity,
                ])->all(),
            'labelSettings' => [],
        ];
        if ($withItems) {
            $list['listItems'] = MealieDb::table('shopping_list_items')
                ->where('shopping_list_id', $row->id)
                ->orderBy('position')
                ->get()
                ->map(fn ($item) => $this->shoppingItem($user, $item))
                ->all();
        }

        return $list;
    }

    public function findShoppingList(object $user, string $id): ?array
    {
        $row = MealieDb::table('shopping_lists')->where('id', Guid::hex($id))->where('group_id', $user->group_id)->first();

        return $row ? $this->shoppingList($user, $row) : null;
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createShoppingList(object $user, array $payload): array
    {
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('shopping_lists')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'user_id' => $user->id,
            'name' => $payload['name'] ?? 'Shopping List',
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->findShoppingList($user, $id) ?? [];
    }

    /**
     * @return array<string, mixed>
     */
    private function planEntry(object $user, object $row): array
    {
        $owner = $row->user_id ? MealieDb::table('users')->where('id', $row->user_id)->first() : null;
        $recipe = null;
        if ($row->recipe_id) {
            $recipeRow = MealieDb::table('recipes')->where('id', $row->recipe_id)->first();
            if ($recipeRow) {
                $recipe = $this->recipes->find($user, (string) $recipeRow->slug);
            }
        }

        return [
            'id' => (int) $row->id,
            'date' => JsonShape::date($row->date),
            'entryType' => $row->entry_type,
            'title' => $row->title ?? '',
            'text' => $row->text ?? '',
            'recipeId' => Guid::dashed($row->recipe_id),
            'groupId' => Guid::dashed($row->group_id),
            'userId' => Guid::dashed($row->user_id),
            'householdId' => Guid::dashed($owner->household_id ?? $user->household_id),
            'recipe' => $recipe,
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function shoppingItem(object $user, object $item): array
    {
        $food = $item->food_id ? MealieDb::table('ingredient_foods')->where('id', $item->food_id)->first() : null;
        $unit = $item->unit_id ? MealieDb::table('ingredient_units')->where('id', $item->unit_id)->first() : null;
        $label = $item->label_id ? MealieDb::table('multi_purpose_labels')->where('id', $item->label_id)->first() : null;

        return [
            'id' => Guid::dashed($item->id),
            'shoppingListId' => Guid::dashed($item->shopping_list_id),
            'checked' => JsonShape::bool($item->checked),
            'position' => (int) $item->position,
            'quantity' => (float) ($item->quantity ?? 0),
            'note' => $item->note ?? '',
            'display' => $item->note ?? '',
            'isFood' => JsonShape::bool($item->is_food),
            'foodId' => Guid::dashed($item->food_id),
            'unitId' => Guid::dashed($item->unit_id),
            'labelId' => Guid::dashed($item->label_id),
            'groupId' => Guid::dashed($user->group_id),
            'householdId' => Guid::dashed($user->household_id),
            'food' => $food ? ['id' => Guid::dashed($food->id), 'name' => $food->name, 'pluralName' => $food->plural_name] : null,
            'unit' => $unit ? ['id' => Guid::dashed($unit->id), 'name' => $unit->name, 'abbreviation' => $unit->abbreviation] : null,
            'label' => $label ? ['id' => Guid::dashed($label->id), 'name' => $label->name, 'color' => $label->color] : null,
            'recipeReferences' => MealieDb::table('shopping_list_item_recipe_reference')
                ->where('shopping_list_item_id', $item->id)
                ->get()
                ->map(fn ($ref) => [
                    'id' => Guid::dashed($ref->id),
                    'shoppingListItemId' => Guid::dashed($ref->shopping_list_item_id),
                    'recipeId' => Guid::dashed($ref->recipe_id),
                    'recipeQuantity' => (float) $ref->recipe_quantity,
                    'recipeScale' => (float) ($ref->recipe_scale ?? 1),
                    'recipeNote' => $ref->recipe_note,
                ])->all(),
            'extras' => new \stdClass,
            'createdAt' => JsonShape::dateTime($item->created_at),
            'updatedAt' => JsonShape::dateTime($item->update_at),
        ];
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    private function insertItem(object $user, array $payload): ?array
    {
        $listId = Guid::hex($payload['shoppingListId'] ?? $payload['shopping_list_id'] ?? null);
        if ($listId === null) {
            return null;
        }
        $list = MealieDb::table('shopping_lists')->where('id', $listId)->where('group_id', $user->group_id)->first();
        if ($list === null) {
            return null;
        }

        $id = Guid::hex($payload['id'] ?? null) ?? Guid::newHex();
        $now = MealieDb::now();
        $position = $payload['position'] ?? ((int) MealieDb::table('shopping_list_items')->where('shopping_list_id', $listId)->max('position')) + 1;
        MealieDb::table('shopping_list_items')->insert([
            'id' => $id,
            'shopping_list_id' => $listId,
            'is_ingredient' => JsonShape::bool($payload['isIngredient'] ?? $payload['is_ingredient'] ?? false) ? 1 : 0,
            'position' => (int) $position,
            'checked' => JsonShape::bool($payload['checked'] ?? false) ? 1 : 0,
            'quantity' => $payload['quantity'] ?? 1,
            'note' => $payload['note'] ?? '',
            'is_food' => JsonShape::bool($payload['isFood'] ?? $payload['is_food'] ?? false) ? 1 : 0,
            'unit_id' => Guid::hex(is_array($payload['unit'] ?? null) ? ($payload['unit']['id'] ?? null) : ($payload['unitId'] ?? $payload['unit_id'] ?? null)),
            'food_id' => Guid::hex(is_array($payload['food'] ?? null) ? ($payload['food']['id'] ?? null) : ($payload['foodId'] ?? $payload['food_id'] ?? null)),
            'label_id' => Guid::hex($payload['labelId'] ?? $payload['label_id'] ?? null),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->shoppingItem($user, MealieDb::table('shopping_list_items')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    private function updateItem(object $user, string $id, array $payload): ?array
    {
        if ($this->ownedItem($user, $id) === null) {
            return null;
        }

        $fields = ['update_at' => MealieDb::now()];
        if (array_key_exists('checked', $payload)) {
            $fields['checked'] = JsonShape::bool($payload['checked']) ? 1 : 0;
        }
        if (array_key_exists('note', $payload)) {
            $fields['note'] = $payload['note'];
        }
        if (array_key_exists('quantity', $payload)) {
            $fields['quantity'] = $payload['quantity'];
        }
        if (array_key_exists('position', $payload)) {
            $fields['position'] = (int) $payload['position'];
        }
        MealieDb::table('shopping_list_items')->where('id', $id)->update($fields);

        return $this->shoppingItem($user, MealieDb::table('shopping_list_items')->where('id', $id)->first());
    }

    private function ownedItem(object $user, string $id): ?object
    {
        $item = MealieDb::table('shopping_list_items')->where('id', $id)->first();
        if ($item === null) {
            return null;
        }
        $list = MealieDb::table('shopping_lists')->where('id', $item->shopping_list_id)->where('group_id', $user->group_id)->first();

        return $list ? $item : null;
    }

    /**
     * @param  list<array<string, mixed>>  $recipes
     * @return array<string, mixed>|null
     */
    public function addRecipes(object $user, string $listId, array $recipes): ?array
    {
        $list = $this->ownedList($user, $listId);
        if ($list === null) {
            return null;
        }

        foreach ($recipes as $recipe) {
            $recipeId = Guid::hex($recipe['recipeId'] ?? $recipe['recipe_id'] ?? null);
            $scale = (float) ($recipe['recipeIncrementQuantity'] ?? $recipe['recipe_increment_quantity'] ?? 1);
            $row = $recipeId ? MealieDb::table('recipes')->where('id', $recipeId)->where('group_id', $user->group_id)->first() : null;
            if ($row === null) {
                continue;
            }
            $ingredients = $recipe['recipeIngredients'] ?? $recipe['recipe_ingredients'] ?? null;
            if (! is_array($ingredients)) {
                $ingredients = MealieDb::table('recipes_ingredients')->where('recipe_id', $recipeId)->orderBy('position')->get()
                    ->map(fn ($item) => [
                        'quantity' => (float) ($item->quantity ?? 0),
                        'note' => $item->note,
                        'foodId' => Guid::dashed($item->food_id),
                        'unitId' => Guid::dashed($item->unit_id),
                    ])->all();
            }
            foreach ($ingredients as $ingredient) {
                $baseQty = (float) ($ingredient['quantity'] ?? 0);
                $created = $this->insertItem($user, [
                    'shoppingListId' => Guid::dashed($list->id),
                    'note' => $ingredient['note'] ?? '',
                    'quantity' => $baseQty * $scale,
                    'foodId' => is_array($ingredient['food'] ?? null) ? ($ingredient['food']['id'] ?? null) : ($ingredient['foodId'] ?? null),
                    'unitId' => is_array($ingredient['unit'] ?? null) ? ($ingredient['unit']['id'] ?? null) : ($ingredient['unitId'] ?? null),
                    'isIngredient' => true,
                ]);
                if ($created === null) {
                    continue;
                }
                $now = MealieDb::now();
                MealieDb::table('shopping_list_item_recipe_reference')->insert([
                    'id' => Guid::newHex(),
                    'shopping_list_item_id' => Guid::hex($created['id']),
                    'recipe_id' => $recipeId,
                    'recipe_quantity' => $baseQty,
                    'recipe_scale' => $scale,
                    'recipe_note' => $ingredient['note'] ?? '',
                    'created_at' => $now,
                    'update_at' => $now,
                ]);
            }
            $this->bumpListRecipe($list->id, $recipeId, $scale);
        }

        return $this->findShoppingList($user, Guid::dashed($list->id));
    }

    /**
     * @return array<string, mixed>|null
     */
    public function removeRecipe(object $user, string $listId, string $recipeId, float $decrement): ?array
    {
        $list = $this->ownedList($user, $listId);
        $hex = Guid::hex($recipeId);
        if ($list === null || $hex === null) {
            return null;
        }

        $refs = MealieDb::table('shopping_list_item_recipe_reference')->where('recipe_id', $hex)->get();
        foreach ($refs as $ref) {
            $item = $this->ownedItem($user, $ref->shopping_list_item_id);
            if ($item === null || $item->shopping_list_id !== $list->id) {
                continue;
            }
            $scale = (float) ($ref->recipe_scale ?? 1);
            $perRecipe = (float) $ref->recipe_quantity;
            $remove = min($scale, $decrement);
            $quantity = (float) $item->quantity - ($remove * $perRecipe);
            $remaining = $scale - $remove;
            if ($remaining <= 0) {
                MealieDb::table('shopping_list_item_recipe_reference')->where('id', $ref->id)->delete();
            } else {
                MealieDb::table('shopping_list_item_recipe_reference')->where('id', $ref->id)->update([
                    'recipe_scale' => $remaining,
                    'update_at' => MealieDb::now(),
                ]);
            }
            $still = MealieDb::table('shopping_list_item_recipe_reference')->where('shopping_list_item_id', $item->id)->exists();
            if ($quantity <= 0 && ! $still) {
                MealieDb::table('shopping_list_items')->where('id', $item->id)->delete();
            } else {
                MealieDb::table('shopping_list_items')->where('id', $item->id)->update([
                    'quantity' => max(0, $quantity),
                    'update_at' => MealieDb::now(),
                ]);
            }
        }
        $this->bumpListRecipe($list->id, $hex, -$decrement);

        return $this->findShoppingList($user, Guid::dashed($list->id));
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function todaysMeals(object $user): array
    {
        return MealieDb::table('group_meal_plans')
            ->where('group_id', $user->group_id)
            ->where('date', now()->toDateString())
            ->orderBy('id')
            ->get()
            ->map(fn ($row) => $this->planEntry($user, $row))
            ->all();
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function randomMeal(object $user, array $payload): ?array
    {
        $recipe = MealieDb::table('recipes')->where('group_id', $user->group_id)->inRandomOrder()->first();
        if ($recipe === null) {
            return null;
        }

        return $this->createMealPlan($user, [
            'date' => $payload['date'] ?? now()->toDateString(),
            'entryType' => $payload['entryType'] ?? $payload['entry_type'] ?? 'dinner',
            'title' => '',
            'text' => '',
            'recipeId' => Guid::dashed($recipe->id),
        ]);
    }

    private function ownedList(object $user, string $listId): ?object
    {
        $hex = Guid::hex($listId);

        return $hex ? MealieDb::table('shopping_lists')->where('id', $hex)->where('group_id', $user->group_id)->first() : null;
    }

    private function bumpListRecipe(string $listId, string $recipeId, float $delta): void
    {
        $existing = MealieDb::table('shopping_list_recipe_reference')
            ->where('shopping_list_id', $listId)
            ->where('recipe_id', $recipeId)
            ->first();
        $now = MealieDb::now();
        if ($existing === null) {
            if ($delta <= 0) {
                return;
            }
            MealieDb::table('shopping_list_recipe_reference')->insert([
                'id' => Guid::newHex(),
                'shopping_list_id' => $listId,
                'recipe_id' => $recipeId,
                'recipe_quantity' => $delta,
                'created_at' => $now,
                'update_at' => $now,
            ]);

            return;
        }
        $next = (float) $existing->recipe_quantity + $delta;
        if ($next <= 0) {
            MealieDb::table('shopping_list_recipe_reference')->where('id', $existing->id)->delete();

            return;
        }
        MealieDb::table('shopping_list_recipe_reference')->where('id', $existing->id)->update([
            'recipe_quantity' => $next,
            'update_at' => $now,
        ]);
    }

    /**
     * @return array<string, mixed>
     */
    public function rules(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('group_meal_plan_rules')->where('household_id', $user->household_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('day')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->ruleOut($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createRule(object $user, array $payload): array
    {
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('group_meal_plan_rules')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'household_id' => $user->household_id,
            'day' => (string) ($payload['day'] ?? 'unset'),
            'entry_type' => (string) ($payload['entryType'] ?? $payload['entry_type'] ?? 'unset'),
            'query_filter_string' => (string) ($payload['queryFilterString'] ?? $payload['query_filter_string'] ?? ''),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->ruleOut(MealieDb::table('group_meal_plan_rules')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateRule(object $user, string $id, array $payload): ?array
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table('group_meal_plan_rules')->where('id', $hex)->where('household_id', $user->household_id)->first();
        if ($row === null) {
            return null;
        }
        MealieDb::table('group_meal_plan_rules')->where('id', $hex)->update([
            'day' => (string) ($payload['day'] ?? $row->day),
            'entry_type' => (string) ($payload['entryType'] ?? $payload['entry_type'] ?? $row->entry_type),
            'query_filter_string' => (string) ($payload['queryFilterString'] ?? $payload['query_filter_string'] ?? $row->query_filter_string),
            'update_at' => MealieDb::now(),
        ]);

        return $this->ruleOut(MealieDb::table('group_meal_plan_rules')->where('id', $hex)->first());
    }

    public function deleteRule(object $user, string $id): bool
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return false;
        }

        return MealieDb::table('group_meal_plan_rules')->where('id', $hex)->where('household_id', $user->household_id)->delete() > 0;
    }

    /**
     * @return array<string, mixed>
     */
    private function ruleOut(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'groupId' => Guid::dashed($row->group_id),
            'householdId' => Guid::dashed($row->household_id),
            'day' => $row->day,
            'entryType' => $row->entry_type,
            'queryFilterString' => $row->query_filter_string ?? '',
            'queryFilter' => new \stdClass,
        ];
    }
}
