<?php

namespace App\Areas\Recipes\Support;

use Illuminate\Database\Query\Builder;

/**
 * RecipeSummary / Recipe (mealie/schema/recipe/recipe.py) from SQLite rows.
 * recipes.household_id is an association proxy through recipes.user_id -> users.household_id.
 */
class RecipeMap
{
    /** recipes rows with the user's household id, limited to recipes that have one (page_all filter). */
    public static function query(?string $groupId): Builder
    {
        $q = Db::table('recipes')
            ->join('users as ru', 'ru.id', '=', 'recipes.user_id')
            ->whereNotNull('ru.household_id')
            ->select('recipes.*', 'ru.household_id as r_household_id');
        if ($groupId !== null) {
            $q->where('recipes.group_id', $groupId);
        }

        return $q;
    }

    /** Same, but without the household filter (get_one uses filter_by(group_id=..)). */
    public static function anyQuery(?string $groupId): Builder
    {
        $q = Db::table('recipes')
            ->leftJoin('users as ru', 'ru.id', '=', 'recipes.user_id')
            ->select('recipes.*', 'ru.household_id as r_household_id');
        if ($groupId !== null) {
            $q->where('recipes.group_id', $groupId);
        }

        return $q;
    }

    /** Organizers of many recipes: [recipe_id => ['categories' => [...], 'tags' => [...], 'tools' => [...]]] */
    private static function organizers(array $ids): array
    {
        $out = [];
        if ($ids === []) {
            return $out;
        }
        foreach ([['recipes_to_categories', 'categories', 'category_id', 'recipeCategory'], ['recipes_to_tags', 'tags', 'tag_id', 'tags']] as [$link, $table, $fk, $key]) {
            $rows = Db::table($link)->join($table, "{$table}.id", '=', "{$link}.{$fk}")
                ->whereIn("{$link}.recipe_id", $ids)->orderBy("{$link}.rowid")
                ->get(["{$link}.recipe_id", "{$table}.*"]);
            foreach ($rows as $r) {
                $r->recipe_count = 0;
                $out[$r->recipe_id][$key][] = Map::recipeTag($r);
            }
        }
        $rows = Db::table('recipes_to_tools')->join('tools', 'tools.id', '=', 'recipes_to_tools.tool_id')
            ->whereIn('recipes_to_tools.recipe_id', $ids)->orderBy('recipes_to_tools.rowid')
            ->get(['recipes_to_tools.recipe_id', 'tools.*']);
        $households = Map::toolHouseholds($rows->pluck('id')->unique()->values()->all());
        foreach ($rows as $r) {
            $out[$r->recipe_id]['tools'][] = Map::recipeTool($r, $households);
        }

        return $out;
    }

    private static function num(mixed $v): float
    {
        return $v === null ? 0.0 : (float) $v;
    }

    private static function strish(mixed $v): ?string
    {
        if ($v === null) {
            return null;
        }
        if (is_int($v) || is_float($v)) {
            return (string) $v;
        }

        return (string) $v;
    }

    /** @return array<int,array> RecipeSummary items */
    public static function summaries(iterable $rows, bool $orjson = false): array
    {
        $rows = collect($rows)->values();
        $org = self::organizers($rows->pluck('id')->all());
        $dt = fn ($v) => $orjson ? Out::dtOrjson($v) : Out::dt($v);

        return $rows->map(function ($r) use ($org, $dt) {
            $o = $org[$r->id] ?? [];

            return [
                'id' => Out::id($r->id),
                'userId' => Out::id($r->user_id),
                'householdId' => Out::id($r->r_household_id),
                'groupId' => Out::id($r->group_id),
                'name' => $r->name,
                'slug' => $r->slug ?? '',
                'image' => $r->image,
                'recipeServings' => self::num($r->recipe_servings),
                'recipeYieldQuantity' => self::num($r->recipe_yield_quantity),
                'recipeYield' => self::strish($r->recipe_yield),
                'totalTime' => self::strish($r->total_time),
                'prepTime' => self::strish($r->prep_time),
                'cookTime' => self::strish($r->cook_time),
                'performTime' => self::strish($r->perform_time),
                'description' => $r->description,
                'recipeCategory' => $o['recipeCategory'] ?? [],
                'tags' => $o['tags'] ?? [],
                'tools' => $o['tools'] ?? [],
                'rating' => $r->rating === null ? null : (float) $r->rating,
                'orgURL' => $r->org_url,
                'dateAdded' => $r->date_added === null ? null : substr($r->date_added, 0, 10),
                'dateUpdated' => $dt($r->date_updated),
                'createdAt' => $dt($r->created_at),
                'updatedAt' => $dt($r->update_at),
                'lastMade' => $dt($r->last_made),
            ];
        })->all();
    }

    // ---------------------------------------------------------------- full recipe

    private const SUP = ['1' => '¹', '2' => '²', '3' => '³', '4' => '⁴', '5' => '⁵', '6' => '⁶', '7' => '⁷', '8' => '⁸', '9' => '⁹', '0' => '⁰'];

    private const SUB = ['1' => '₁', '2' => '₂', '3' => '₃', '4' => '₄', '5' => '₅', '6' => '₆', '7' => '₇', '8' => '₈', '9' => '₉', '0' => '₀'];

    /** Fraction(x).limit_denominator(32) */
    private static function fraction(float $x, int $max = 32): array
    {
        // exact rational of the float, then Python's limit_denominator algorithm
        [$n, $d] = self::floatToRatio($x);
        if ($d <= $max) {
            return [$n, $d];
        }
        $p0 = 0; $q0 = 1; $p1 = 1; $q1 = 0;
        $nn = $n; $dd = $d;
        while (true) {
            $a = intdiv($nn, $dd);
            if ($nn < 0 && $nn % $dd !== 0) {
                $a--;
            }
            $q2 = $q0 + $a * $q1;
            if ($q2 > $max) {
                break;
            }
            [$p0, $q0, $p1, $q1] = [$p1, $q1, $p0 + $a * $p1, $q2];
            [$nn, $dd] = [$dd, $nn - $a * $dd];
            if ($dd === 0) {
                break;
            }
        }
        if ($dd === 0) {
            return self::reduce($p1, $q1);
        }
        $k = intdiv($max - $q0, $q1);
        $b1 = [$p0 + $k * $p1, $q0 + $k * $q1];
        $b2 = [$p1, $q1];
        // choose the closer bound
        $d1 = abs($b2[0] * $d - $n * $b2[1]) * $b1[1];
        $d2 = abs($b1[0] * $d - $n * $b1[1]) * $b2[1];

        return $d1 <= $d2 ? self::reduce($b2[0], $b2[1]) : self::reduce($b1[0], $b1[1]);
    }

    private static function reduce(int $n, int $d): array
    {
        $g = self::gcd(abs($n), abs($d)) ?: 1;

        return [intdiv($n, $g), intdiv($d, $g)];
    }

    private static function gcd(int $a, int $b): int
    {
        while ($b !== 0) {
            [$a, $b] = [$b, $a % $b];
        }

        return $a;
    }

    /** Approximate the float as a ratio with a power-of-two-ish denominator small enough for PHP ints. */
    private static function floatToRatio(float $x): array
    {
        $d = 1;
        while (abs($x * $d - round($x * $d)) > 1e-12 && $d < (1 << 40)) {
            $d *= 2;
        }

        return self::reduce((int) round($x * $d), $d);
    }

    private static function displayFraction(int $n, int $d): string
    {
        return strtr((string) $n, self::SUP).'/'.strtr((string) $d, self::SUB);
    }

    private static function pyFloatStr(float $v): string
    {
        $s = (string) $v;
        if (! str_contains($s, '.') && ! str_contains($s, 'E') && ! str_contains($s, 'e')) {
            $s .= '.0';
        }

        return $s;
    }

    /** RecipeIngredientBase._format_display with LocalePluralFoodHandling.WITHOUT_UNIT (en-US). */
    private static function display(?float $qty, ?array $unit, ?array $food, ?string $note): string
    {
        $parts = [];
        if ($qty) {
            if ($unit && ! $unit['fraction']) {
                $q = round($qty, 3);
                $parts[] = floor($q) == $q ? (string) (int) $q : self::pyFloatStr($q);
            } else {
                [$n, $d] = self::fraction($qty);
                if ($d === 1) {
                    $parts[] = (string) $n;
                } elseif ($n <= $d) {
                    $parts[] = self::displayFraction($n, $d);
                } else {
                    $whole = 0;
                    while ($n > $d) {
                        $whole++;
                        $n -= $d;
                    }
                    $parts[] = $whole.' '.self::displayFraction($n, $d);
                }
            }
        }
        if ($qty && $unit) {
            $plural = $qty > 1;
            $val = '';
            if ($unit['useAbbreviation']) {
                $val = $plural ? ($unit['pluralAbbreviation'] ?: $unit['abbreviation']) : $unit['abbreviation'];
            }
            if (! $val) {
                $val = $plural ? ($unit['pluralName'] ?: $unit['name']) : $unit['name'];
            }
            $parts[] = $val;
        }
        if ($food) {
            $usePlural = ($qty && $qty <= 1) ? false : ! ($qty && $unit);
            $parts[] = $usePlural ? ($food['pluralName'] ?: $food['name']) : $food['name'];
        }
        if ($note) {
            $parts[] = $note;
        }

        return trim(implode(' ', $parts));
    }

    /** Full Recipe for one recipes row (from query()/anyQuery()). */
    public static function full(object $r, int $depth = 0): array
    {
        $id = $r->id;
        $base = self::summaries([$r])[0];

        // ingredients
        $ingRows = Db::table('recipes_ingredients')->where('recipe_id', $id)->orderBy('position')->get();
        $unitIds = $ingRows->pluck('unit_id')->filter()->unique()->values()->all();
        $foodIds = $ingRows->pluck('food_id')->filter()->unique()->values()->all();
        $units = [];
        if ($unitIds !== []) {
            foreach (Map::units(Db::table('ingredient_units')->whereIn('id', $unitIds)->get()) as $u) {
                $units[str_replace('-', '', $u['id'])] = $u;
            }
        }
        $foods = [];
        if ($foodIds !== []) {
            foreach (Map::foods(Db::table('ingredient_foods')->whereIn('id', $foodIds)->get()) as $f) {
                $foods[str_replace('-', '', $f['id'])] = $f;
            }
        }
        $subs = [];
        $ingIds = $ingRows->pluck('id')->all();
        if ($ingIds !== []) {
            $subRows = Db::table('recipes_ingredients_substitutions as s')
                ->leftJoin('ingredient_foods as f', 'f.id', '=', 's.substitute_food_id')
                ->whereIn('s.ingredient_id', $ingIds)->orderBy('s.position')
                ->get(['s.ingredient_id', 's.substitute_food_id', 's.note', 'f.id as fid', 'f.name as fname', 'f.plural_name as fplural']);
            foreach ($subRows as $s) {
                $subs[$s->ingredient_id][] = [
                    'substituteFoodId' => Out::id($s->substitute_food_id),
                    'note' => $s->note,
                    'substituteFood' => $s->fid === null ? null : ['id' => Out::id($s->fid), 'name' => $s->fname, 'pluralName' => $s->fplural],
                ];
            }
        }
        $ingredients = [];
        foreach ($ingRows as $i) {
            $qty = $i->quantity === null ? null : round((float) $i->quantity, 3);
            $unit = $i->unit_id ? ($units[$i->unit_id] ?? null) : null;
            $food = $i->food_id ? ($foods[$i->food_id] ?? null) : null;
            $ref = null;
            if ($i->referenced_recipe_id && $depth < 3) {
                $refRow = self::anyQuery(null)->where('recipes.id', $i->referenced_recipe_id)->first();
                $ref = $refRow ? self::full($refRow, $depth + 1) : null;
            }
            $ingredients[] = [
                'quantity' => $qty,
                'unit' => $unit,
                'food' => $food,
                'referencedRecipe' => $ref,
                'note' => $i->note,
                'display' => self::display($qty, $unit, $food, $i->note),
                'title' => $i->title,
                'originalText' => $i->original_text,
                'substitutions' => $subs[$i->id] ?? [],
                'referenceId' => Out::id($i->reference_id) ?? \App\Support\Guid::fromDb(\App\Support\Guid::new()),
            ];
        }

        // instructions
        $steps = Db::table('recipe_instructions')->where('recipe_id', $id)->orderBy('position')->get();
        $stepIds = $steps->pluck('id')->all();
        $ingRefs = [];
        $noteRefs = [];
        if ($stepIds !== []) {
            foreach (Db::table('recipe_ingredient_ref_link')->whereIn('instruction_id', $stepIds)->orderBy('id')->get() as $l) {
                $ingRefs[$l->instruction_id][] = ['referenceId' => Out::id($l->reference_id)];
            }
            foreach (Db::table('recipe_note_ref_link')->whereIn('instruction_id', $stepIds)->orderBy('id')->get() as $l) {
                $noteRefs[$l->instruction_id][] = ['referenceId' => Out::id($l->reference_id)];
            }
        }
        $instructions = $steps->map(fn ($s) => [
            'id' => Out::id($s->id),
            'title' => $s->title,
            'summary' => $s->summary,
            'text' => $s->text,
            'ingredientReferences' => $ingRefs[$s->id] ?? [],
            'noteReferences' => $noteRefs[$s->id] ?? [],
        ])->all();

        $n = Db::table('recipe_nutrition')->where('recipe_id', $id)->first();
        $nutrition = $n === null ? null : [
            'calories' => $n->calories,
            'carbohydrateContent' => $n->carbohydrate_content,
            'cholesterolContent' => $n->cholesterol_content,
            'fatContent' => $n->fat_content,
            'fiberContent' => $n->fiber_content,
            'proteinContent' => $n->protein_content,
            'saturatedFatContent' => $n->saturated_fat_content,
            'sodiumContent' => $n->sodium_content,
            'sugarContent' => $n->sugar_content,
            'transFatContent' => $n->trans_fat_content,
            'unsaturatedFatContent' => $n->unsaturated_fat_content,
        ];

        $s = Db::table('recipe_settings')->where('recipe_id', $id)->first();
        $settings = $s === null ? null : [
            'public' => (bool) $s->public,
            'showNutrition' => (bool) $s->show_nutrition,
            'showAssets' => (bool) $s->show_assets,
            'landscapeView' => (bool) $s->landscape_view,
            'disableComments' => (bool) $s->disable_comments,
            'locked' => (bool) $s->locked,
        ];

        $assets = Db::table('recipe_assets')->where('recipe_id', $id)->orderBy('id')->get()
            ->map(fn ($a) => ['name' => $a->name, 'icon' => $a->icon, 'fileName' => $a->file_name])->all();
        $notes = Db::table('notes')->where('recipe_id', $id)->orderBy('id')->get()
            ->map(fn ($a) => ['title' => $a->title, 'text' => $a->text, 'referenceId' => Out::id($a->reference_id) ?? \App\Support\Guid::fromDb(\App\Support\Guid::new())])->all();
        $extras = Map::extras('api_extras', 'recipee_id', [$id])[$id] ?? [];
        $comments = Map::commentQuery(null)->where('recipe_comments.recipe_id', $id)->orderBy('recipe_comments.rowid')->get()
            ->map(fn ($c) => Map::comment($c))->all();

        return $base + [
            'recipeIngredient' => $ingredients,
            'recipeInstructions' => $instructions,
            'nutrition' => $nutrition,
            'settings' => $settings,
            'assets' => $assets,
            'notes' => $notes,
            'extras' => (object) $extras,
            'comments' => $comments,
        ];
    }
}
