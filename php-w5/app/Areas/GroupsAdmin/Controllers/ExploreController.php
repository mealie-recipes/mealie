<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Out;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use App\Support\Pagination;
use Illuminate\Http\Request;

/**
 * mealie/routes/explore/controller_public_foods.py, controller_public_households.py,
 * controller_public_organizers.py; group resolution from get_public_group
 * (mealie/core/dependencies/dependencies.py:66).
 */
class ExploreController
{
    private const ORGANIZER_COLUMNS = ['id' => false, 'group_id' => false, 'name' => true, 'slug' => true];

    /** get_public_group */
    private function group(string $slug): object
    {
        $hex = Guid::toDb($slug);
        $group = $hex !== null
            ? Db::table('groups')->where('id', $hex)->first()
            : Db::table('groups')->where('slug', $slug)->first();
        $prefs = $group ? Db::table('group_preferences')->where('group_id', $group->id)->first() : null;
        if ($group === null || $prefs === null || $prefs->private_group) {
            Errors::http(404, 'group not found');
        }

        return $group;
    }

    private function url(object $group, string $endpoint): string
    {
        return "/explore/groups/{$group->slug}/{$endpoint}";
    }

    // ------------------------------------------------------------ foods

    public function foods(Request $request, string $groupSlug)
    {
        $group = $this->group($groupSlug);
        $query = Db::table('ingredient_foods')->where('ingredient_foods.group_id', $group->id);

        return Json::respond(Pagination::page(
            $request, $query, fn ($rows) => Out::foodMany($rows), $this->url($group, 'foods'), [
                'table' => 'ingredient_foods',
                'model' => 'IngredientFoodModel',
                'columns' => ['id' => false, 'group_id' => false, 'name' => true, 'plural_name' => true, 'description' => true,
                    'label_id' => false, 'name_normalized' => true, 'plural_name_normalized' => true],
                'search' => ['ingredient_foods.name_normalized', 'ingredient_foods.plural_name_normalized'],
                'normalizeSearch' => true,
            ]));
    }

    public function food(string $groupSlug, string $itemId)
    {
        $group = $this->group($groupSlug);
        $id = Guid::requireUuid4($itemId);
        $food = Db::table('ingredient_foods')->where('group_id', $group->id)->where('id', $id)->first();
        if ($food === null) {
            Errors::http(404, 'food not found');
        }

        return Json::respond(Out::foodMany([$food])[0]);
    }

    // ------------------------------------------------------------ households

    public function households(Request $request, string $groupSlug)
    {
        $group = $this->group($groupSlug);
        // fixed filter "(preferences.private_household = FALSE)"
        $query = Db::table('households')->where('households.group_id', $group->id)
            ->whereExists(fn ($q) => $q->selectRaw('1')->from('household_preferences')
                ->whereColumn('household_preferences.household_id', 'households.id')
                ->where('household_preferences.private_household', false))
            ->select('households.*');

        return Json::respond(Pagination::page(
            $request, $query, fn ($rows) => Out::householdSummaryMany($rows), $this->url($group, 'households'), [
                'table' => 'households',
                'model' => 'Household',
                'columns' => ['id' => false, 'name' => true, 'slug' => true, 'group_id' => false],
            ]));
    }

    public function household(string $groupSlug, string $householdSlug)
    {
        $group = $this->group($groupSlug);
        $query = Db::table('households')->where('group_id', $group->id);
        $hex = Guid::toDb($householdSlug);
        $household = $hex !== null ? $query->where('id', $hex)->first() : $query->where('slug', $householdSlug)->first();
        $prefs = $household ? Db::table('household_preferences')->where('household_id', $household->id)->first() : null;
        if ($household === null || ($prefs !== null && $prefs->private_household)) {
            Errors::http(404, 'household not found');
        }

        return Json::respond(Out::householdSummary($household));
    }

    // ------------------------------------------------------------ organizers

    private function organizerPage(Request $request, object $group, string $table, string $model, string $route, callable $map)
    {
        $query = Db::table($table)->where("{$table}.group_id", $group->id);
        if ($table !== 'tools') {
            $query->select("{$table}.*")->selectRaw(Out::recipeCountSql($table));
        }

        return Json::respond(Pagination::page(
            $request, $query, $map, $route, [
                'table' => $table,
                'model' => $model,
                'columns' => self::ORGANIZER_COLUMNS,
                'search' => ["{$table}.name"],
            ]));
    }

    private function organizer(object $group, string $table, string $id): ?object
    {
        $query = Db::table($table)->where('group_id', $group->id)->where('id', $id);
        if ($table !== 'tools') {
            $query->select("{$table}.*")->selectRaw(Out::recipeCountSql($table));
        }

        return $query->first();
    }

    public function categories(Request $request, string $groupSlug)
    {
        $group = $this->group($groupSlug);

        // Python builds the guides from tags_router here
        return $this->organizerPage($request, $group, 'categories', 'Category', $this->url($group, 'organizers/tags'),
            fn ($rows) => array_map([Out::class, 'recipeTag'], $rows));
    }

    public function category(string $groupSlug, string $itemId)
    {
        $group = $this->group($groupSlug);
        $item = $this->organizer($group, 'categories', Guid::requireUuid4($itemId));
        if ($item === null) {
            Errors::http(404, 'category not found');
        }

        return Json::respond(Out::categoryOut($item));
    }

    public function tags(Request $request, string $groupSlug)
    {
        $group = $this->group($groupSlug);

        return $this->organizerPage($request, $group, 'tags', 'Tag', $this->url($group, 'organizers/tags'),
            fn ($rows) => array_map([Out::class, 'recipeTag'], $rows));
    }

    public function tag(string $groupSlug, string $itemId)
    {
        $group = $this->group($groupSlug);
        $item = $this->organizer($group, 'tags', Guid::requireUuid4($itemId));
        if ($item === null) {
            Errors::http(404, 'tag not found');
        }

        return Json::respond(Out::tagOut($item));
    }

    public function tools(Request $request, string $groupSlug)
    {
        $group = $this->group($groupSlug);

        return $this->organizerPage($request, $group, 'tools', 'Tool', $this->url($group, 'organizers/tools'),
            fn ($rows) => Out::recipeToolMany($rows));
    }

    public function tool(string $groupSlug, string $itemId)
    {
        $group = $this->group($groupSlug);
        $item = $this->organizer($group, 'tools', Guid::requireUuid4($itemId));
        if ($item === null) {
            Errors::http(404, 'tool not found');
        }

        return Json::respond(Out::recipeToolOut($item));
    }
}
