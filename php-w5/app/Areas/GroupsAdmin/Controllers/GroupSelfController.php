<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Checks;
use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Fs;
use App\Areas\GroupsAdmin\Support\Out;
use App\Areas\GroupsAdmin\Support\Pager;
use App\Areas\GroupsAdmin\Support\Validator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/groups/controller_group_self_service.py and controller_group_households.py */
class GroupSelfController
{
    /** GET /groups/self */
    public function self()
    {
        $group = Db::table('groups')->where('id', CurrentUser::groupId())->first();

        return Json::respond(Out::groupSummary($group));
    }

    /** GET /groups/members */
    public function members(Request $request)
    {
        $query = Db::table('users')->where('users.group_id', CurrentUser::groupId());

        return Json::respond(Pager::page(
            $request, $query, 'users', 'User',
            ['id' => false, 'full_name' => true, 'username' => true, 'group_id' => false, 'household_id' => false],
            fn ($rows) => array_map([Out::class, 'userSummary'], $rows),
            '/groups/members',
        ));
    }

    /** GET /groups/members/{username_or_id} */
    public function member(string $usernameOrId)
    {
        $query = Db::table('users')->where('group_id', CurrentUser::groupId());
        $hex = Guid::toDb($usernameOrId);
        $user = $hex !== null ? $query->where('id', $hex)->first() : $query->where('username', $usernameOrId)->first();
        if ($user === null) {
            Errors::http(404, 'User Not Found');
        }

        return Json::respond(Out::userSummary($user));
    }

    /** GET /groups/preferences */
    public function preferences()
    {
        $prefs = Db::table('group_preferences')->where('group_id', CurrentUser::groupId())->first();

        return Json::respond(Out::groupPreferences($prefs));
    }

    /** PUT /groups/preferences */
    public function updatePreferences(Request $request)
    {
        $v = Validator::body($request);
        $private = $v->bool('private_group', false, true);
        $announce = $v->bool('show_announcements', false, true);
        $v->check();

        Checks::canManage();

        $groupId = CurrentUser::groupId();
        $row = Db::table('group_preferences')->where('group_id', $groupId)->first();
        if ($row === null) {
            Checks::noResult();
        }
        Db::table('group_preferences')->where('id', $row->id)->update([
            'private_group' => $private,
            'show_announcements' => $announce,
            'update_at' => Dates::nowDb(),
        ]);

        return Json::respond(Out::groupPreferences(Db::table('group_preferences')->where('id', $row->id)->first()));
    }

    /** GET /groups/storage — GroupService.calculate_group_storage */
    public function storage()
    {
        $ids = Db::table('recipes')->where('group_id', CurrentUser::groupId())->pluck('id');
        $used = 0;
        foreach ($ids as $id) {
            $used += Fs::dirSize(Fs::dir('RECIPE_DATA_DIR').'/'.Guid::fromDb($id));
        }
        $allowed = 500 * 1048576;

        return Json::respond([
            'usedStorageBytes' => $used,
            'usedStorageStr' => Fs::prettySize($used),
            'totalStorageBytes' => $allowed,
            'totalStorageStr' => Fs::prettySize($allowed),
        ]);
    }

    /** GET /groups/households */
    public function households(Request $request)
    {
        $query = Db::table('households')->where('households.group_id', CurrentUser::groupId());

        return Json::respond(Pager::page(
            $request, $query, 'households', 'Household',
            ['id' => false, 'name' => true, 'slug' => true, 'group_id' => false],
            fn ($rows) => Out::householdSummaryMany($rows),
            '/groups/households',
        ));
    }

    /** GET /groups/households/{household_slug} — RepositoryHousehold.get_by_slug_or_id */
    public function household(string $slug)
    {
        $query = Db::table('households')->where('group_id', CurrentUser::groupId());
        $hex = Guid::toDb($slug);
        $household = $hex !== null ? $query->where('id', $hex)->first() : $query->where('slug', $slug)->first();
        if ($household === null) {
            Errors::http(404, 'Household not found');
        }

        return Json::respond(Out::householdSummary($household));
    }
}
