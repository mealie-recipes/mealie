<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Input;
use App\Areas\Households\Support\Out;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use App\Support\Pagination;
use Illuminate\Http\Request;

/** mealie/routes/households/controller_household_self_service.py */
class SelfServiceController
{
    private const PREF_FIELDS = [
        'private_household' => true,
        'show_announcements' => true,
        'lock_recipe_edits_from_other_households' => true,
        'first_day_of_week' => 0,
        'recipe_public' => true,
        'recipe_show_nutrition' => false,
        'recipe_show_assets' => false,
        'recipe_landscape_view' => false,
        'recipe_disable_comments' => false,
    ];

    /** GET /households/self */
    public function self()
    {
        $h = Out::db()->table('households')->where('id', CurrentUser::householdId())->first();

        return Json::respond($h ? Out::household($h) : null);
    }

    /** GET /households/self/recipes/{recipe_slug} -> HouseholdService.get_household_recipe */
    public function recipe(string $recipeSlug)
    {
        $db = Out::db();
        $query = $db->table('recipes')->where('group_id', CurrentUser::groupId());
        $hex = Guid::toDb($recipeSlug);
        $recipe = $hex !== null && preg_match('/^[0-9a-fA-F-{}]+$/', trim($recipeSlug))
            ? $query->where('id', $hex)->first()
            : $query->where('slug', $recipeSlug)->first();
        if (! $recipe) {
            Errors::http(404, 'Recipe not found');
        }

        $hr = $db->table('households_to_recipes')
            ->where('household_id', CurrentUser::householdId())->where('recipe_id', $recipe->id)->first();

        return Json::respond([
            'lastMade' => $hr ? Dates::out($hr->last_made) : null,
            'recipeId' => Guid::fromDb($recipe->id),
        ]);
    }

    /** GET /households/members */
    public function members(Request $request)
    {
        if (! CurrentUser::get()->can_manage) {
            Errors::http(403, 'Forbidden');
        }
        $householdId = CurrentUser::householdId();
        $query = Out::db()->table('users')->where('group_id', CurrentUser::groupId())->where('household_id', $householdId);

        return Json::respond(Pagination::page($request, $query, fn ($rows) => array_map([Out::class, 'user'], $rows), '/households/members', [
            'table' => 'users', 'model' => 'User',
            'columns' => ['id' => false, 'full_name' => true, 'username' => true, 'group_id' => false, 'household_id' => false],
            'queryFilter' => 'household_id='.Guid::fromDb($householdId),
        ]));
    }

    /** GET /households/preferences */
    public function preferences()
    {
        $p = Out::db()->table('household_preferences')->where('household_id', CurrentUser::householdId())->first();

        return Json::respond(Out::preferences($p));
    }

    /** PUT /households/preferences */
    public function updatePreferences(Request $request)
    {
        $data = Input::object($request);
        if (! CurrentUser::get()->can_manage_household) {
            Errors::http(403, 'Forbidden');
        }

        $values = [];
        foreach (self::PREF_FIELDS as $field => $default) {
            $values[$field] = is_bool($default) ? Input::bool($data, $field, $default) : Input::int($data, $field, $default);
        }

        $db = Out::db();
        $row = $db->table('household_preferences')->where('household_id', CurrentUser::householdId())->first();
        if (! $row) {
            Errors::http(404, ['message' => 'An unexpected error occurred', 'error' => true, 'exception' => 'No row was found when one was required']);
        }
        $db->table('household_preferences')->where('id', $row->id)->update($values + ['update_at' => Dates::nowDb()]);

        return Json::respond(Out::preferences($db->table('household_preferences')->where('id', $row->id)->first()));
    }

    /** PUT /households/permissions */
    public function permissions(Request $request)
    {
        $data = Input::object($request);
        $userId = Input::uuid($data, 'user_id');
        $flags = [];
        foreach (['can_manage_household', 'can_manage', 'can_invite', 'can_organize'] as $f) {
            $flags[$f] = Input::bool($data, $f, false);
        }

        $me = CurrentUser::get();
        if (! $me->can_manage) {
            Errors::http(403, 'Forbidden');
        }

        $db = Out::db();
        // repos.users is group-scoped
        $target = $db->table('users')->where('group_id', $me->group_id)->where('id', $userId)->first();
        if (! $target) {
            Errors::http(404, 'User not found');
        }
        if ($target->group_id !== $me->group_id) {
            Errors::http(403, 'User is not a member of this group');
        }
        if ($target->household_id !== $me->household_id) {
            Errors::http(403, 'User is not a member of this household');
        }
        if ($target->id === $me->id) {
            Errors::http(403, 'User is not allowed to change their own permissions');
        }

        // User._set_permissions: admins keep every permission
        if ($target->admin) {
            $flags = ['can_manage_household' => true, 'can_manage' => true, 'can_invite' => true, 'can_organize' => true, 'advanced' => true];
        }
        $db->table('users')->where('id', $target->id)->update($flags + ['update_at' => Dates::nowDb()]);

        return Json::respond(Out::user($db->table('users')->where('id', $target->id)->first()));
    }

    /** GET /households/statistics -> RepositoryHousehold.statistics */
    public function statistics()
    {
        $db = Out::db();
        $g = CurrentUser::groupId();
        $h = CurrentUser::householdId();

        return Json::respond([
            'totalRecipes' => $db->table('recipes')->where('group_id', $g)
                ->whereIn('user_id', fn ($q) => $q->select('id')->from('users')->where('household_id', $h))->count(),
            'totalUsers' => $db->table('users')->where('group_id', $g)->where('household_id', $h)->count(),
            'totalCategories' => $db->table('categories')->where('group_id', $g)->count(),
            'totalTags' => $db->table('tags')->where('group_id', $g)->count(),
            'totalTools' => $db->table('tools')->where('group_id', $g)->count(),
        ]);
    }
}
