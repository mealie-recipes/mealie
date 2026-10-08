<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Cascade;
use App\Areas\GroupsAdmin\Support\Checks;
use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Out;
use App\Areas\GroupsAdmin\Support\Validator;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use App\Support\Pagination;
use App\Support\Text;
use Illuminate\Database\QueryException;
use Illuminate\Http\Request;

/**
 * mealie/routes/admin/admin_management_households.py with RepositoryHousehold (repos/repository_household.py)
 * and HouseholdService.create_household (services/household_services/household_service.py).
 */
class AdminHouseholdsController
{
    public const PREFERENCE_FIELDS = [
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

    private function find(string $id): ?object
    {
        return Db::table('households')->where('id', $id)->first();
    }

    public function index(Request $request)
    {
        return Json::respond(Pagination::page(
            $request, Db::table('households'), fn ($rows) => Out::householdInDbMany($rows), '/households', [
                'table' => 'households',
                'model' => 'Household',
                'columns' => ['id' => false, 'name' => true, 'slug' => true, 'group_id' => false],
            ]));
    }

    public function show(string $itemId)
    {
        $household = $this->find(Guid::requireUuid4($itemId));
        if ($household === null) {
            Errors::notFound();
        }

        return Json::respond(Out::householdInDb($household));
    }

    /**
     * RepositoryHousehold.create: slug from the name; on an IntegrityError retry as "name (n)" up to 10 times.
     * Returns the new row, or null when every attempt failed (Python re-raises: 500).
     */
    public static function createHousehold(string $groupId, string $name): ?object
    {
        $id = Guid::new();
        $original = $name;
        for ($attempt = 0; $attempt < 10; $attempt++) {
            $now = Dates::nowDb();
            try {
                Db::table('households')->insert([
                    'id' => $id, 'name' => $name, 'slug' => Text::slugify($name), 'group_id' => $groupId,
                    'created_at' => $now, 'update_at' => $now,
                ]);

                return Db::table('households')->where('id', $id)->first();
            } catch (QueryException) {
                $name = $original.' ('.($attempt + 1).')';
            }
        }

        return null;
    }

    /** SaveHouseholdPreferences (+ model default recipe_disable_amount = True) */
    public static function createPreferences(string $householdId, array $prefs): void
    {
        $now = Dates::nowDb();
        Db::table('household_preferences')->insert(array_merge(self::PREFERENCE_FIELDS, $prefs, [
            'id' => Guid::new(),
            'household_id' => $householdId,
            'recipe_disable_amount' => true,
            'created_at' => $now,
            'update_at' => $now,
        ]));
    }

    public function store(Request $request)
    {
        $v = Validator::body($request);
        $groupId = $v->uuid('group_id', false, true);
        $name = $v->str('name', true, null, false, true, 1);
        $v->check();

        // repos are unscoped for admins, so a missing groupId stays NULL and every insert fails (500)
        $household = $groupId === null ? null : self::createHousehold($groupId, $name);
        if ($household === null) {
            Errors::http(500, 'Internal Server Error');
        }

        $groupPrefs = Db::table('group_preferences')->where('group_id', $groupId)->first();
        $prefs = $groupPrefs
            ? ['private_household' => (bool) $groupPrefs->private_group, 'recipe_public' => ! $groupPrefs->private_group]
            : [];
        // the response is validated before the preferences row exists
        $out = Out::householdInDb($household);
        self::createPreferences($household->id, $prefs);

        return Json::respond($out, 201);
    }

    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $v = Validator::body($request);
        $v->uuid('group_id');
        $name = $v->str('name', true, null, false, true, 1);
        $v->uuid('id');
        $prefsIn = $v->object('preferences');
        $prefs = null;
        if ($prefsIn !== null) {
            $pv = $v->nested('preferences', $prefsIn);
            $prefs = [];
            foreach (self::PREFERENCE_FIELDS as $field => $default) {
                $prefs[$field] = is_int($default) ? $pv->int($field, false, $default) : $pv->bool($field, false, $default);
            }
            $v->absorb($pv);
        }
        $v->check();

        $household = $this->find($id);
        if ($household === null) {
            // `household.name` / `mapper(..., None)` on a missing row raise outside any handler
            Errors::http(500, 'Internal Server Error');
        }

        if ($prefs !== null) {
            $row = Db::table('household_preferences')->where('household_id', $id)->first();
            if ($row === null) {
                Errors::http(500, 'Internal Server Error');
            }
            Db::table('household_preferences')->where('id', $row->id)->update($prefs + ['update_at' => Dates::nowDb()]);
        }

        if ($name !== '' && $name !== $household->name) {
            try {
                Db::table('households')->where('id', $id)->update([
                    'name' => $name, 'slug' => Text::slugify($name), 'update_at' => Dates::nowDb(),
                ]);
            } catch (QueryException) {
                Errors::http(500, 'Internal Server Error');
            }
        }

        return Json::respond(Out::householdInDb($this->find($id)));
    }

    /** Household relationships with cascade="all, delete-orphan" and its many-to-many association rows. */
    public static function deleteHousehold(string $id): void
    {
        Db::table('household_preferences')->where('household_id', $id)->delete();
        Db::table('invite_tokens')->where('household_id', $id)->delete();
        Cascade::delete('recipe_actions', 'household_id', [$id]);
        Cascade::delete('cookbooks', 'household_id', [$id]);
        Db::table('webhook_urls')->where('household_id', $id)->delete();
        Cascade::delete('group_events_notifiers', 'household_id', [$id]);
        Db::table('households_to_recipes')->where('household_id', $id)->delete();
        Db::table('households_to_ingredient_foods')->where('household_id', $id)->delete();
        Db::table('households_to_tools')->where('household_id', $id)->delete();
        Db::table('households')->where('id', $id)->delete();
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $household = $this->find($id);
        if ($household === null) {
            Checks::noResult();
        }
        $users = Db::table('users')->where('group_id', $household->group_id)->where('household_id', $id)->count();
        if ($users) {
            Errors::errorResponse(400, 'Cannot delete household with users');
        }
        $out = Out::householdInDb($household);
        Db::conn()->transaction(fn () => self::deleteHousehold($id));

        return Json::respond($out);
    }
}
