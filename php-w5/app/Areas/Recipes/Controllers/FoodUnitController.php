<?php

namespace App\Areas\Recipes\Controllers;

use App\Areas\Recipes\Support\Db;
use App\Areas\Recipes\Support\Input;
use App\Areas\Recipes\Support\Map;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Pagination;
use App\Support\Text;
use Illuminate\Http\Request;

/**
 * mealie/routes/unit_and_foods/foods.py and units.py
 */
class FoodUnitController extends Base
{
    private const FOOD_COLUMNS = [
        'created_at' => false, 'update_at' => false, 'id' => false, 'group_id' => false, 'name' => true,
        'description' => true, 'label_id' => false, 'name_normalized' => true, 'plural_name' => true,
        'plural_name_normalized' => true, 'on_hand' => false,
    ];

    private const UNIT_COLUMNS = [
        'created_at' => false, 'update_at' => false, 'id' => false, 'group_id' => false, 'name' => true,
        'description' => true, 'abbreviation' => true, 'fraction' => false, 'use_abbreviation' => false,
        'name_normalized' => true, 'abbreviation_normalized' => true, 'plural_name' => true,
        'plural_name_normalized' => true, 'plural_abbreviation' => true, 'plural_abbreviation_normalized' => true,
        'standard_quantity' => false, 'standard_unit' => true,
    ];

    /** en-US units seed (mealie/repos/seed/resources/units/locales/en-US.json): value -> unit key */
    private const STANDARD_MAP = [
        'teaspoon' => 'teaspoon', 'teaspoons' => 'teaspoon', 'tsp' => 'teaspoon',
        'tablespoon' => 'tablespoon', 'tablespoons' => 'tablespoon', 'tbsp' => 'tablespoon',
        'cup' => 'cup', 'cups' => 'cup', 'c' => 'cup',
        'fluid ounce' => 'fluid-ounce', 'fluid ounces' => 'fluid-ounce', 'fl oz' => 'fluid-ounce',
        'pint' => 'pint', 'pints' => 'pint', 'pt' => 'pint',
        'quart' => 'quart', 'quarts' => 'quart', 'qt' => 'quart',
        'gallon' => 'gallon', 'gallons' => 'gallon', 'gal' => 'gallon',
        'milliliter' => 'milliliter', 'milliliters' => 'milliliter', 'ml' => 'milliliter',
        'liter' => 'liter', 'liters' => 'liter', 'l' => 'liter',
        'pound' => 'pound', 'pounds' => 'pound', 'lb' => 'pound',
        'ounce' => 'ounce', 'ounces' => 'ounce', 'oz' => 'ounce',
        'gram' => 'gram', 'grams' => 'gram', 'g' => 'gram',
        'kilogram' => 'kilogram', 'kilograms' => 'kilogram', 'kg' => 'kilogram',
        'milligram' => 'milligram', 'milligrams' => 'milligram', 'mg' => 'milligram',
        'splash' => 'splash', 'splashes' => 'splash', 'dash' => 'dash', 'dashes' => 'dash',
        'serving' => 'serving', 'servings' => 'serving', 'head' => 'head', 'heads' => 'head',
        'clove' => 'clove', 'cloves' => 'clove', 'can' => 'can', 'cans' => 'can', 'bunch' => 'bunch',
        'bunches' => 'bunch', 'pack' => 'pack', 'packs' => 'pack', 'pinch' => 'pinch', 'pinches' => 'pinch',
        'sprig' => 'sprig', 'sprigs' => 'sprig',
    ];

    /** RepositoryUnit._add_standardized_unit match arms */
    private const STANDARDS = [
        'teaspoon' => [1 / 6, 'fluid_ounce'], 'tablespoon' => [1 / 2, 'fluid_ounce'], 'cup' => [1, 'cup'],
        'fluid-ounce' => [1, 'fluid_ounce'], 'pint' => [2, 'cup'], 'quart' => [4, 'cup'], 'gallon' => [16, 'cup'],
        'milliliter' => [1, 'milliliter'], 'liter' => [1, 'liter'], 'pound' => [1, 'pound'], 'ounce' => [1, 'ounce'],
        'gram' => [1, 'gram'], 'kilogram' => [1, 'kilogram'], 'milligram' => [1 / 1000, 'gram'],
    ];

    private function findFood(string $id): ?object
    {
        return Db::table('ingredient_foods')->where('group_id', $this->groupId())->where('id', $id)->first();
    }

    private function findUnit(string $id): ?object
    {
        return Db::table('ingredient_units')->where('group_id', $this->groupId())->where('id', $id)->first();
    }

    // ===================================================================== foods

    public function foodsIndex(Request $request)
    {
        $query = Db::table('ingredient_foods')->select('ingredient_foods.*')->where('ingredient_foods.group_id', $this->groupId());
        $result = Pagination::page($request, $query, fn ($rows) => $rows, '/foods', [
            'table' => 'ingredient_foods',
            'columns' => self::FOOD_COLUMNS,
            'search' => ['ingredient_foods.name_normalized', 'ingredient_foods.plural_name_normalized'],
            'normalizeSearch' => true,
        ]);
        $result['items'] = Map::foods($result['items']);

        return $this->json($result);
    }

    /** CreateIngredientFood (mealie/schema/recipe/recipe_ingredient.py:198) */
    private function readFood(Request $request): array
    {
        $in = Input::fromRequest($request);
        $rawId = $in->raw('id');
        $id = $rawId ? $in->uuid4('id', false, true) : null;
        $data = [
            'id' => $id,
            'name' => $in->str('name'),
            'plural_name' => $in->str('plural_name', false, null, true),
            'description' => $in->has('description') && $in->raw('description') === null ? '' : $in->str('description', false, ''),
            'label_id' => $in->uuid4('label_id', false, true),
            'aliases' => [],
            'substitutions' => [],
            'households' => $in->strList('households_with_ingredient_food'),
            'extras' => [],
        ];
        $extras = $in->raw('extras');
        if (is_array($extras) && ! array_is_list($extras)) {
            $data['extras'] = $extras;
        }
        foreach ($in->objList('aliases') as $a) {
            if (! isset($a['name']) || ! is_string($a['name'])) {
                $in->error('aliases', 'missing', 'Field required');
                continue;
            }
            $data['aliases'][] = $a['name'];
        }
        // SubstitutionBase.prune: drop empty rows, de-dupe by substitute food (keep first)
        $seen = [];
        foreach ($in->objList('substitutions') as $s) {
            $fid = $s['substituteFoodId'] ?? ($s['substitute_food_id'] ?? null);
            $note = $s['note'] ?? null;
            if (is_string($note)) {
                $note = trim($note);
            }
            if (! $fid && ! $note) {
                continue;
            }
            if ($fid) {
                if (! is_string($fid) || ! Guid::isUuid4($fid)) {
                    $in->error('substitutions', 'uuid_parsing', 'Input should be a valid UUID');
                    continue;
                }
                $fid = Guid::toDb($fid);
                if (isset($seen[$fid])) {
                    continue;
                }
                $seen[$fid] = true;
            }
            $data['substitutions'][] = ['food' => $fid ?: null, 'note' => ($note === '' ? null : $note)];
        }
        if ($id && isset($seen[$id])) {
            $in->error('substitutions', 'value_error', 'Value error, a food cannot be substituted with itself');
        }
        $in->check();

        return $data;
    }

    /** IngredientFoodModel.__init__ (mealie/db/models/recipe/ingredient.py:314) */
    private function writeFood(array $d, ?string $id): string
    {
        $gid = $this->groupId();
        $now = $this->now();
        $values = [
            'name' => $d['name'],
            'plural_name' => $d['plural_name'],
            'description' => $d['description'],
            'label_id' => $d['label_id'],
            'name_normalized' => Text::normalize($d['name']),
            'plural_name_normalized' => $d['plural_name'] === null ? null : Text::normalize($d['plural_name']),
        ];
        if ($id === null) {
            $id = $d['id'] ?? Guid::new();
            Db::table('ingredient_foods')->insert(['created_at' => $now, 'update_at' => $this->now(), 'id' => $id, 'group_id' => $gid, 'on_hand' => 0] + $values);
        } else {
            Db::table('ingredient_foods')->where('id', $id)->update($values + ['update_at' => $now]);
            Db::table('ingredient_foods_aliases')->where('food_id', $id)->delete();
            Db::table('ingredient_food_extras')->where('ingredient_food_id', $id)->delete();
            Db::table('households_to_ingredient_foods')->where('food_id', $id)->delete();
        }
        foreach ($d['aliases'] as $name) {
            Db::table('ingredient_foods_aliases')->insert([
                'id' => Guid::new(), 'food_id' => $id, 'name' => $name, 'name_normalized' => Text::normalize($name),
                'created_at' => $now, 'update_at' => $now,
            ]);
        }
        foreach ($d['extras'] as $k => $v) {
            Db::table('ingredient_food_extras')->insert([
                'created_at' => $now, 'update_at' => $now, 'key_name' => (string) $k,
                'value' => is_scalar($v) || $v === null ? $v : json_encode($v), 'ingredient_food_id' => $id,
            ]);
        }
        if ($d['households'] !== []) {
            foreach (Db::table('households')->where('group_id', $gid)->whereIn('slug', $d['households'])->orderBy('rowid')->pluck('id') as $hid) {
                Db::table('households_to_ingredient_foods')->insert(['household_id' => $hid, 'food_id' => $id]);
            }
        }

        // _set_substitutions / resolve_substitutions: ids must resolve within the group and not be the food itself
        $wanted = array_values(array_filter(array_column($d['substitutions'], 'food')));
        $valid = $wanted === [] ? [] : Db::table('ingredient_foods')->where('group_id', $gid)->whereIn('id', $wanted)->pluck('id')->flip()->all();
        $existing = Db::table('ingredient_foods_substitutions')->where('food_id', $id)->get();
        $byFood = $existing->filter(fn ($r) => $r->substitute_food_id)->keyBy('substitute_food_id');
        $noteOnly = $existing->filter(fn ($r) => ! $r->substitute_food_id)->values()->all();
        $keep = [];
        $pos = 0;
        foreach ($d['substitutions'] as $s) {
            if ($s['food'] === null) {
                if (! $s['note']) {
                    continue;
                }
                $row = array_shift($noteOnly);
            } else {
                if (! isset($valid[$s['food']]) || $s['food'] === $id) {
                    continue;
                }
                $row = $byFood[$s['food']] ?? null;
            }
            if ($row) {
                Db::table('ingredient_foods_substitutions')->where('id', $row->id)->update(['substitute_food_id' => $s['food'], 'note' => $s['note'], 'position' => $pos, 'update_at' => $now]);
                $keep[] = $row->id;
            } else {
                $sid = Guid::new();
                Db::table('ingredient_foods_substitutions')->insert([
                    'id' => $sid, 'food_id' => $id, 'substitute_food_id' => $s['food'], 'note' => $s['note'],
                    'position' => $pos, 'created_at' => $now, 'update_at' => $now,
                ]);
                $keep[] = $sid;
            }
            $pos++;
        }
        Db::table('ingredient_foods_substitutions')->where('food_id', $id)->whereNotIn('id', $keep)->delete();

        return $id;
    }

    public function foodsStore(Request $request)
    {
        $d = $this->readFood($request);
        $this->canOrganize();
        $id = $this->write(fn () => $this->writeFood($d, null), self::SERVER_ERROR_MSG, 'Database integrity error');

        return $this->json(Map::food($this->findFood($id)), 201);
    }

    public function foodsShow(string $item_id)
    {
        $id = Input::pathUuid4($item_id);

        return $this->json(Map::food($this->findFood($id) ?? Errors::notFound()));
    }

    public function foodsUpdate(Request $request, string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $d = $this->readFood($request);
        $this->canOrganize();
        if (! $this->findFood($id)) {
            Errors::notFound();
        }
        $this->write(fn () => $this->writeFood($d, $id), self::SERVER_ERROR_MSG, 'Database integrity error');

        return $this->json(Map::food($this->findFood($id)));
    }

    private function deleteFoodRows(string $id): void
    {
        Db::table('ingredient_foods_aliases')->where('food_id', $id)->delete();
        Db::table('ingredient_food_extras')->where('ingredient_food_id', $id)->delete();
        Db::table('households_to_ingredient_foods')->where('food_id', $id)->delete();
        Db::table('ingredient_foods_substitutions')->where('food_id', $id)->orWhere('substitute_food_id', $id)->delete();
        Db::table('recipes_ingredients_substitutions')->where('substitute_food_id', $id)->delete();
        Db::table('recipes_ingredients')->where('food_id', $id)->update(['food_id' => null]);
        Db::table('ingredient_foods')->where('id', $id)->delete();
    }

    public function foodsDestroy(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $this->canOrganize();
        $row = $this->findFood($id);
        if (! $row) {
            Errors::errorResponse(404, self::SERVER_ERROR_MSG, self::NO_RESULT);
        }
        $out = Map::food($row);
        Db::conn()->transaction(fn () => $this->deleteFoodRows($id));

        return $this->json($out);
    }

    /** RepositoryFood.merge (mealie/repos/repository_foods.py:97) */
    public function foodsMerge(Request $request)
    {
        $in = Input::fromRequest($request);
        $from = $in->uuid4('from_food');
        $to = $in->uuid4('to_food');
        $in->check();
        $this->canOrganize();
        if (! $this->findFood($from) || ! $this->findFood($to)) {
            Errors::http(500, 'Failed to merge foods');
        }

        try {
            Db::conn()->transaction(function () use ($from, $to) {
                $now = $this->now();
                $toSubs = Db::table('ingredient_foods_substitutions')->where('food_id', $to)->get();
                $existingSub = $toSubs->pluck('substitute_food_id')->filter()->flip()->all();
                $existingSrc = Db::table('ingredient_foods_substitutions')->where('substitute_food_id', $to)->pluck('food_id')->flip()->all();
                $pos = (int) ($toSubs->max('position') ?? -1) + 1;

                // capture the recipe-tier rows before the ingredient move
                $recipeSubs = Db::table('recipes_ingredients_substitutions as s')
                    ->join('recipes_ingredients as i', 'i.id', '=', 's.ingredient_id')
                    ->whereIn('s.substitute_food_id', [$from, $to])
                    ->orderBy('s.ingredient_id')->orderBy('s.position')
                    ->get(['s.id', 's.ingredient_id', 'i.food_id']);

                Db::table('recipes_ingredients')->where('food_id', $from)->update(['food_id' => $to]);

                foreach (Db::table('ingredient_foods_substitutions')->where('food_id', $from)->orderBy('position')->get() as $row) {
                    if ($row->substitute_food_id !== null) {
                        if ($row->substitute_food_id === $to || isset($existingSub[$row->substitute_food_id])) {
                            continue;
                        }
                        $existingSub[$row->substitute_food_id] = true;
                    }
                    Db::table('ingredient_foods_substitutions')->where('id', $row->id)->update(['food_id' => $to, 'position' => $pos++, 'update_at' => $now]);
                }
                foreach (Db::table('ingredient_foods_substitutions')->where('substitute_food_id', $from)->get() as $row) {
                    if ($row->food_id === $to || isset($existingSrc[$row->food_id])) {
                        continue;
                    }
                    $existingSrc[$row->food_id] = true;
                    Db::table('ingredient_foods_substitutions')->where('id', $row->id)->update(['substitute_food_id' => $to, 'update_at' => $now]);
                }

                $seen = [];
                foreach ($recipeSubs as $row) {
                    if (in_array($row->food_id, [$from, $to], true) || isset($seen[$row->ingredient_id])) {
                        Db::table('recipes_ingredients_substitutions')->where('id', $row->id)->delete();
                        continue;
                    }
                    $seen[$row->ingredient_id] = true;
                    Db::table('recipes_ingredients_substitutions')->where('id', $row->id)->update(['substitute_food_id' => $to, 'update_at' => $now]);
                }

                Db::table('shopping_list_items')->where('food_id', $from)->update(['food_id' => $to]);
                $this->deleteFoodRows($from);
            });
        } catch (\Throwable $e) {
            Errors::http(500, 'Failed to merge foods');
        }

        return $this->json(['message' => 'Successfully merged foods', 'error' => false]);
    }

    // ===================================================================== units

    public function unitsIndex(Request $request)
    {
        $query = Db::table('ingredient_units')->select('ingredient_units.*')->where('ingredient_units.group_id', $this->groupId());
        $result = Pagination::page($request, $query, fn ($rows) => $rows, '/units', [
            'table' => 'ingredient_units',
            'columns' => self::UNIT_COLUMNS,
            'search' => [
                'ingredient_units.name_normalized', 'ingredient_units.plural_name_normalized',
                'ingredient_units.abbreviation_normalized', 'ingredient_units.plural_abbreviation_normalized',
            ],
            'normalizeSearch' => true,
        ]);
        $result['items'] = Map::units($result['items']);

        return $this->json($result);
    }

    /** CreateIngredientUnit (recipe_ingredient.py:268) incl. validate_standardization_fields */
    private function readUnit(Request $request): array
    {
        $in = Input::fromRequest($request);
        $d = [
            'name' => $in->str('name'),
            'plural_name' => $in->str('plural_name', false, null, true),
            'description' => $in->has('description') && $in->raw('description') === null ? '' : $in->str('description', false, ''),
            'fraction' => $in->bool('fraction', true),
            'abbreviation' => $in->str('abbreviation', false, ''),
            'plural_abbreviation' => $in->str('plural_abbreviation', false, '', true),
            'use_abbreviation' => $in->bool('use_abbreviation', false),
            'standard_quantity' => $in->float('standard_quantity', null),
            'standard_unit' => $in->str('standard_unit', false, null, true),
            'aliases' => [],
            'present' => array_keys($in->data),
        ];
        foreach ($in->objList('aliases') as $a) {
            if (! isset($a['name']) || ! is_string($a['name'])) {
                $in->error('aliases', 'missing', 'Field required');
                continue;
            }
            $d['aliases'][] = $a['name'];
        }
        $in->check();
        if (! $d['standard_unit'] || ! (($d['standard_quantity'] ?? 0) > 0)) {
            $d['standard_quantity'] = $d['standard_unit'] = null;
        }

        return $d;
    }

    private function standardize(array $d): array
    {
        if ($d['standard_quantity'] !== null || $d['standard_unit'] !== null) {
            return $d;
        }
        foreach (['name', 'plural_name', 'abbreviation', 'plural_abbreviation'] as $prop) {
            $val = $d[$prop];
            if (! (is_string($val) && $val !== '')) {
                continue;
            }
            $key = self::STANDARD_MAP[strtolower(trim($val))] ?? null;
            if ($key === null || ! isset(self::STANDARDS[$key])) {
                continue;
            }
            [$d['standard_quantity'], $d['standard_unit']] = self::STANDARDS[$key];
        }

        return $d;
    }

    private function writeUnit(array $d, ?string $id): string
    {
        $now = $this->now();
        $norm = fn ($v) => $v === null ? null : Text::normalize($v);
        $values = [
            'name' => $d['name'], 'plural_name' => $d['plural_name'], 'description' => $d['description'],
            'abbreviation' => $d['abbreviation'], 'plural_abbreviation' => $d['plural_abbreviation'],
            'fraction' => $d['fraction'] ? 1 : 0, 'use_abbreviation' => $d['use_abbreviation'] ? 1 : 0,
            'standard_quantity' => $d['standard_quantity'] === null ? null : (float) $d['standard_quantity'],
            'standard_unit' => $d['standard_unit'],
            'name_normalized' => $norm($d['name']), 'plural_name_normalized' => $norm($d['plural_name']),
            'abbreviation_normalized' => $norm($d['abbreviation']), 'plural_abbreviation_normalized' => $norm($d['plural_abbreviation']),
        ];
        if ($id === null) {
            $id = Guid::new();
            Db::table('ingredient_units')->insert(['created_at' => $now, 'update_at' => $this->now(), 'id' => $id, 'group_id' => $this->groupId()] + $values);
        } else {
            Db::table('ingredient_units')->where('id', $id)->update($values + ['update_at' => $now]);
            Db::table('ingredient_units_aliases')->where('unit_id', $id)->delete();
        }
        foreach ($d['aliases'] as $name) {
            Db::table('ingredient_units_aliases')->insert([
                'id' => Guid::new(), 'unit_id' => $id, 'name' => $name, 'name_normalized' => Text::normalize($name),
                'created_at' => $now, 'update_at' => $now,
            ]);
        }

        return $id;
    }

    public function unitsStore(Request $request)
    {
        $d = $this->standardize($this->readUnit($request));
        $id = $this->write(fn () => $this->writeUnit($d, null), self::SERVER_ERROR_MSG, 'Database integrity error');

        return $this->json(Map::unit($this->findUnit($id)), 201);
    }

    public function unitsShow(string $item_id)
    {
        $id = Input::pathUuid4($item_id);

        return $this->json(Map::unit($this->findUnit($id) ?? Errors::notFound()));
    }

    public function unitsUpdate(Request $request, string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $d = $this->readUnit($request);
        if (! $this->findUnit($id)) {
            Errors::notFound();
        }
        $this->write(fn () => $this->writeUnit($d, $id), self::SERVER_ERROR_MSG, 'Database integrity error');

        return $this->json(Map::unit($this->findUnit($id)));
    }

    private function deleteUnitRows(string $id): void
    {
        Db::table('ingredient_units_aliases')->where('unit_id', $id)->delete();
        Db::table('recipes_ingredients')->where('unit_id', $id)->update(['unit_id' => null]);
        Db::table('ingredient_units')->where('id', $id)->delete();
    }

    public function unitsDestroy(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $row = $this->findUnit($id);
        if (! $row) {
            Errors::errorResponse(404, self::SERVER_ERROR_MSG, self::NO_RESULT);
        }
        $out = Map::unit($row);
        Db::conn()->transaction(fn () => $this->deleteUnitRows($id));

        return $this->json($out);
    }

    /** RepositoryUnit.merge (mealie/repos/repository_units.py:118) */
    public function unitsMerge(Request $request)
    {
        $in = Input::fromRequest($request);
        $from = $in->uuid4('from_unit');
        $to = $in->uuid4('to_unit');
        $in->check();
        if (! $this->findUnit($from) || ! $this->findUnit($to)) {
            Errors::http(500, 'Failed to merge units');
        }
        try {
            Db::conn()->transaction(function () use ($from, $to) {
                Db::table('recipes_ingredients')->where('unit_id', $from)->update(['unit_id' => $to]);
                Db::table('shopping_list_items')->where('unit_id', $from)->update(['unit_id' => $to]);
                $this->deleteUnitRows($from);
            });
        } catch (\Throwable $e) {
            Errors::http(500, 'Failed to merge units');
        }

        return $this->json(['message' => 'Successfully merged units', 'error' => false]);
    }
}
