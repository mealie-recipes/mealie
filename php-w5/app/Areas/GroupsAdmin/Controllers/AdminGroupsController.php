<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Cascade;
use App\Areas\GroupsAdmin\Support\Checks;
use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Out;
use App\Areas\GroupsAdmin\Support\Settings;
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
 * mealie/routes/admin/admin_management_groups.py with RepositoryGroup (repos/repository_group.py)
 * and GroupService.create_group (services/group_services/group_service.py).
 */
class AdminGroupsController
{
    private function find(string $id): ?object
    {
        return Db::table('groups')->where('id', $id)->first();
    }

    public function index(Request $request)
    {
        return Json::respond(Pagination::page(
            $request, Db::table('groups'), fn ($rows) => Out::groupInDbMany($rows), '/groups', [
                'table' => 'groups',
                'model' => 'Group',
                'columns' => ['id' => false, 'name' => true, 'slug' => true],
            ]));
    }

    public function show(string $itemId)
    {
        $group = $this->find(Guid::requireUuid4($itemId));
        if ($group === null) {
            Errors::notFound();
        }

        return Json::respond(Out::groupInDb($group));
    }

    public function store(Request $request)
    {
        $v = Validator::body($request);
        $name = $v->str('name', true, null, false, true, 1);
        $v->check();

        // RepositoryGroup.create: retry as "name (n)" on an IntegrityError, up to 10 attempts
        $id = Guid::new();
        $original = $name;
        $created = false;
        for ($attempt = 0; $attempt < 10 && ! $created; $attempt++) {
            $now = Dates::nowDb();
            try {
                Db::table('groups')->insert([
                    'id' => $id, 'name' => $name, 'slug' => Text::slugify($name), 'created_at' => $now, 'update_at' => $now,
                ]);
                $created = true;
            } catch (QueryException) {
                $name = $original.' ('.($attempt + 1).')';
            }
        }
        if (! $created) {
            Errors::http(500, 'Internal Server Error');
        }

        $now = Dates::nowDb();
        // CreateGroupPreferences + GroupPreferencesModel column defaults
        Db::table('group_preferences')->insert([
            'id' => Guid::new(), 'group_id' => $id, 'private_group' => true, 'show_announcements' => true,
            'first_day_of_week' => 0, 'recipe_public' => true, 'recipe_show_nutrition' => false,
            'recipe_show_assets' => false, 'recipe_landscape_view' => false, 'recipe_disable_comments' => false,
            'recipe_disable_amount' => true, 'created_at' => $now, 'update_at' => $now,
        ]);
        Db::table('ai_provider_settings')->insert([
            'id' => Guid::new(), 'group_id' => $id, 'created_at' => $now, 'update_at' => $now,
        ]);
        $household = AdminHouseholdsController::createHousehold($id, Settings::get('DEFAULT_HOUSEHOLD', 'Family'));
        if ($household === null) {
            Errors::http(500, 'Internal Server Error');
        }
        AdminHouseholdsController::createPreferences($household->id, ['private_household' => true, 'recipe_public' => false]);

        return Json::respond(Out::groupInDb($this->find($id)), 201);
    }

    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $v = Validator::body($request);
        $v->uuid('id');
        $name = $v->str('name');
        $prefs = null;
        if (($prefsIn = $v->object('preferences')) !== null) {
            $pv = $v->nested('preferences', $prefsIn);
            $prefs = [
                'private_group' => $pv->bool('private_group', false, true),
                'show_announcements' => $pv->bool('show_announcements', false, true),
            ];
            $v->absorb($pv);
        }
        $ai = null;
        if (($aiIn = $v->object('ai_provider_settings')) !== null) {
            $av = $v->nested('ai_provider_settings', $aiIn);
            $ai = [];
            foreach (['default_provider_id', 'audio_provider_id', 'image_provider_id'] as $field) {
                $ai[$field] = $av->uuid($field, true, true, true, true);
            }
            $v->absorb($av);
        }
        $v->check();

        $group = $this->find($id);
        if ($group === null) {
            // `mapper(..., None)` / `group.name` on a missing row raise outside any handler
            Errors::http(500, 'Internal Server Error');
        }
        $now = Dates::nowDb();
        if ($prefs !== null) {
            Db::table('group_preferences')->where('group_id', $id)->update($prefs + ['update_at' => $now]);
        }
        if ($ai !== null) {
            Db::table('ai_provider_settings')->where('group_id', $id)->update($ai + ['update_at' => $now]);
        }
        if ($name !== '' && $name !== $group->name) {
            try {
                Db::table('groups')->where('id', $id)->update(['name' => $name, 'slug' => Text::slugify($name), 'update_at' => $now]);
            } catch (QueryException) {
                Errors::http(500, 'Internal Server Error');
            }
        }

        return Json::respond(Out::groupInDb($this->find($id)));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $group = $this->find($id);
        if ($group !== null && Db::table('users')->where('group_id', $id)->exists()) {
            Errors::errorResponse(400, 'Cannot delete group with users');
        }
        if ($group === null) {
            Checks::noResult();
        }
        $out = Out::groupInDb($group);

        Db::conn()->transaction(function () use ($id) {
            foreach (Db::table('households')->where('group_id', $id)->pluck('id') as $householdId) {
                AdminHouseholdsController::deleteHousehold($householdId);
            }
            Db::table('group_to_categories')->where('group_id', $id)->delete();
            Cascade::delete('groups', 'id', [$id]);
        });

        return Json::respond($out);
    }
}
