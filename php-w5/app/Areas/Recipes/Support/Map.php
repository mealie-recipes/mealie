<?php

namespace App\Areas\Recipes\Support;

use App\Support\Guid;

/**
 * Row -> JSON shapes for the Pydantic schemas of this area.
 * Key order follows the Pydantic field order (parents first).
 */
class Map
{
    // ---------------------------------------------------------------- organizers

    /** RecipeTag / RecipeCategory (mealie/schema/recipe/recipe.py) */
    public static function recipeTag(object $r): array
    {
        return [
            'id' => Out::id($r->id),
            'groupId' => Out::id($r->group_id),
            'name' => $r->name,
            'slug' => $r->slug,
            'recipeCount' => (int) ($r->recipe_count ?? 0),
        ];
    }

    /** TagOut: name, groupId, id, slug, recipeCount */
    public static function tagOut(object $r): array
    {
        return [
            'name' => $r->name,
            'groupId' => Out::id($r->group_id),
            'id' => Out::id($r->id),
            'slug' => $r->slug,
            'recipeCount' => (int) ($r->recipe_count ?? 0),
        ];
    }

    /** CategoryBase: name, id, groupId, slug */
    public static function categoryBase(object $r): array
    {
        return [
            'name' => $r->name,
            'id' => Out::id($r->id),
            'groupId' => Out::id($r->group_id),
            'slug' => $r->slug,
        ];
    }

    /** CategoryOut: CategoryBase fields + recipeCount */
    public static function categoryOut(object $r): array
    {
        return self::categoryBase($r) + ['recipeCount' => (int) ($r->recipe_count ?? 0)];
    }

    /** households_with_tool -> slugs, keyed by tool id */
    public static function toolHouseholds(array $toolIds): array
    {
        if ($toolIds === []) {
            return [];
        }
        $out = [];
        $rows = Db::table('households_to_tools')
            ->join('households', 'households.id', '=', 'households_to_tools.household_id')
            ->whereIn('households_to_tools.tool_id', $toolIds)
            ->orderBy('households_to_tools.rowid')
            ->get(['households_to_tools.tool_id', 'households.slug']);
        foreach ($rows as $row) {
            $out[$row->tool_id][] = $row->slug;
        }

        return $out;
    }

    /** RecipeTool: id, groupId, name, slug, recipeCount, householdsWithTool */
    public static function recipeTool(object $r, array $households): array
    {
        return [
            'id' => Out::id($r->id),
            'groupId' => Out::id($r->group_id),
            'name' => $r->name,
            'slug' => $r->slug,
            'recipeCount' => 0,
            'householdsWithTool' => $households[$r->id] ?? [],
        ];
    }

    // ---------------------------------------------------------------- foods / units

    public static function extras(string $table, string $fk, array $ids): array
    {
        if ($ids === []) {
            return [];
        }
        $out = [];
        foreach (Db::table($table)->whereIn($fk, $ids)->orderBy('id')->get() as $row) {
            $out[$row->{$fk}][$row->key_name] = $row->value;
        }

        return $out;
    }

    /** IngredientFood for a list of ingredient_foods rows (batch-loaded relations). */
    public static function foods(iterable $rows): array
    {
        $rows = collect($rows)->values();
        $ids = $rows->pluck('id')->all();
        if ($ids === []) {
            return [];
        }

        $aliases = [];
        foreach (Db::table('ingredient_foods_aliases')->whereIn('food_id', $ids)->orderBy('rowid')->get() as $a) {
            $aliases[$a->food_id][] = ['name' => $a->name];
        }

        $subs = [];
        $subRows = Db::table('ingredient_foods_substitutions as s')
            ->leftJoin('ingredient_foods as f', 'f.id', '=', 's.substitute_food_id')
            ->whereIn('s.food_id', $ids)
            ->orderBy('s.position')
            ->get(['s.food_id', 's.substitute_food_id', 's.note', 'f.id as fid', 'f.name as fname', 'f.plural_name as fplural']);
        foreach ($subRows as $s) {
            $subs[$s->food_id][] = [
                'substituteFoodId' => Out::id($s->substitute_food_id),
                'note' => $s->note,
                'substituteFood' => $s->fid === null ? null : [
                    'id' => Out::id($s->fid),
                    'name' => $s->fname,
                    'pluralName' => $s->fplural,
                ],
            ];
        }

        $households = [];
        $hRows = Db::table('households_to_ingredient_foods as h')
            ->join('households', 'households.id', '=', 'h.household_id')
            ->whereIn('h.food_id', $ids)
            ->orderBy('h.rowid')
            ->get(['h.food_id', 'households.slug']);
        foreach ($hRows as $h) {
            $households[$h->food_id][] = $h->slug;
        }

        $labelIds = $rows->pluck('label_id')->filter()->unique()->values()->all();
        $labels = [];
        if ($labelIds !== []) {
            foreach (Db::table('multi_purpose_labels')->whereIn('id', $labelIds)->get() as $l) {
                $labels[$l->id] = [
                    'name' => $l->name,
                    'color' => $l->color,
                    'groupId' => Out::id($l->group_id),
                    'id' => Out::id($l->id),
                ];
            }
        }

        $extras = self::extras('ingredient_food_extras', 'ingredient_food_id', $ids);

        return $rows->map(fn ($r) => [
            'id' => Out::id($r->id),
            'name' => $r->name,
            'pluralName' => $r->plural_name,
            'description' => $r->description ?? '',
            'extras' => (object) ($extras[$r->id] ?? []),
            'labelId' => Out::id($r->label_id),
            'aliases' => $aliases[$r->id] ?? [],
            'substitutions' => $subs[$r->id] ?? [],
            'householdsWithIngredientFood' => $households[$r->id] ?? [],
            'label' => $r->label_id !== null ? ($labels[$r->label_id] ?? null) : null,
            'createdAt' => Out::dt($r->created_at),
            'updatedAt' => Out::dt($r->update_at),
        ])->all();
    }

    public static function food(object $row): array
    {
        return self::foods([$row])[0];
    }

    /** IngredientUnit */
    public static function units(iterable $rows): array
    {
        $rows = collect($rows)->values();
        $ids = $rows->pluck('id')->all();
        $aliases = [];
        if ($ids !== []) {
            foreach (Db::table('ingredient_units_aliases')->whereIn('unit_id', $ids)->orderBy('rowid')->get() as $a) {
                $aliases[$a->unit_id][] = ['name' => $a->name];
            }
        }

        return $rows->map(fn ($r) => [
            'id' => Out::id($r->id),
            'name' => $r->name,
            'pluralName' => $r->plural_name,
            'description' => $r->description ?? '',
            'extras' => (object) [],
            'fraction' => $r->fraction === null ? true : (bool) $r->fraction,
            'abbreviation' => $r->abbreviation ?? '',
            'pluralAbbreviation' => $r->plural_abbreviation,
            'useAbbreviation' => $r->use_abbreviation === null ? false : (bool) $r->use_abbreviation,
            'aliases' => $aliases[$r->id] ?? [],
            'standardQuantity' => $r->standard_unit ? (((float) $r->standard_quantity) > 0 ? (float) $r->standard_quantity : null) : null,
            'standardUnit' => $r->standard_unit && ((float) $r->standard_quantity) > 0 ? $r->standard_unit : null,
            'createdAt' => Out::dt($r->created_at),
            'updatedAt' => Out::dt($r->update_at),
        ])->all();
    }

    public static function unit(object $row): array
    {
        return self::units([$row])[0];
    }

    // ---------------------------------------------------------------- comments

    /** Base query for recipe_comments with the fields RecipeCommentOut needs. */
    public static function commentQuery(?string $groupId): \Illuminate\Database\Query\Builder
    {
        $q = Db::table('recipe_comments')
            ->join('recipes', 'recipes.id', '=', 'recipe_comments.recipe_id')
            ->leftJoin('users', 'users.id', '=', 'recipe_comments.user_id')
            ->select('recipe_comments.*', 'users.username as u_username', 'users.admin as u_admin', 'users.full_name as u_full_name', 'users.id as u_id');
        if ($groupId !== null) {
            $q->where('recipes.group_id', $groupId);
        }

        return $q;
    }

    public static function comment(object $r): array
    {
        return [
            'id' => Out::id($r->id),
            'recipeId' => Out::id($r->recipe_id),
            'text' => $r->text,
            'createdAt' => Out::dt($r->created_at),
            'updatedAt' => Out::dt($r->update_at),
            'userId' => Out::id($r->user_id),
            'user' => [
                'id' => Out::id($r->u_id),
                'username' => $r->u_username,
                'admin' => (bool) $r->u_admin,
                'fullName' => $r->u_full_name,
            ],
        ];
    }

    // ---------------------------------------------------------------- timeline

    /** Translations used for system timeline subjects (en-US messages.json). */
    public const TIMELINE_T = [
        'recipe.recipe-created' => 'Recipe Created',
    ];

    public static function timelineQuery(?string $groupId): \Illuminate\Database\Query\Builder
    {
        $q = Db::table('recipe_timeline_events')
            ->join('recipes', 'recipes.id', '=', 'recipe_timeline_events.recipe_id')
            ->leftJoin('users as ru', 'ru.id', '=', 'recipes.user_id')
            ->select('recipe_timeline_events.*', 'recipes.group_id as r_group_id', 'ru.household_id as r_household_id');
        if ($groupId !== null) {
            $q->where('recipes.group_id', $groupId);
        }

        return $q;
    }

    public static function timeline(object $r, bool $translate = true): array
    {
        $subject = $r->subject;
        if ($translate && $r->event_type === 'system') {
            $subject = self::TIMELINE_T[$subject] ?? $subject;
        }

        return [
            'recipeId' => Out::id($r->recipe_id),
            'userId' => Out::id($r->user_id),
            'subject' => $subject,
            'eventType' => $r->event_type,
            'eventMessage' => $r->message,
            'image' => $r->image,
            'timestamp' => Out::dt($r->timestamp),
            'id' => Out::id($r->id),
            'groupId' => Out::id($r->r_group_id),
            'householdId' => Out::id($r->r_household_id),
            'createdAt' => Out::dt($r->created_at),
            'updatedAt' => Out::dt($r->update_at),
        ];
    }

    public static function newId(): string
    {
        return Guid::new();
    }
}
