<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Checks;
use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Fs;
use App\Areas\GroupsAdmin\Support\Out;
use App\Areas\GroupsAdmin\Support\Pager;
use App\Areas\GroupsAdmin\Support\Settings;
use App\Areas\GroupsAdmin\Support\Validator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Database\QueryException;
use Illuminate\Http\Request;

/**
 * mealie/routes/admin/admin_management_users.py with mealie/repos/repository_users.py,
 * mealie/db/models/users/users.py (User.__init__ / User.update / _set_permissions),
 * services/user_services/user_service.py and password_reset_service.py.
 */
class AdminUsersController
{
    private const SERVER_ERROR = 'An unexpected error occurred';

    private const AUTH_METHODS = ['Mealie' => 'MEALIE', 'LDAP' => 'LDAP', 'OIDC' => 'OIDC'];

    private function find(string $id): ?object
    {
        return Db::table('users')->where('id', $id)->first();
    }

    public function index(Request $request)
    {
        return Json::respond(Pager::page(
            $request, Db::table('users'), 'users', 'User',
            ['id' => false, 'full_name' => true, 'username' => true, 'group_id' => false, 'household_id' => false],
            fn ($rows) => Out::userOutMany($rows),
            '/users',
        ));
    }

    public function show(string $itemId)
    {
        $user = $this->find(Guid::requireUuid4($itemId));
        if ($user === null) {
            Checks::notFound();
        }

        return Json::respond(Out::userOut($user));
    }

    /** UserBase fields shared by UserIn and UserOut */
    private function base(Validator $v): array
    {
        $email = $v->str('email');

        return [
            'username' => $v->str('username', false, null, true),
            'full_name' => $v->str('full_name', false, null, true),
            'email' => $email === null ? null : strtolower(trim($email)),
            'auth_method' => $v->enum('auth_method', array_keys(self::AUTH_METHODS), false, 'Mealie') ?? 'Mealie',
            'admin' => $v->bool('admin', false, false),
            'group' => $v->str('group', false, null, true),
            'household' => $v->str('household', false, null, true),
            'advanced' => $v->bool('advanced', false, false),
            'show_announcements' => $v->bool('show_announcements', false, true),
            'last_read_announcement' => $v->str('last_read_announcement', false, null, true),
            'can_invite' => $v->bool('can_invite', false, false),
            'can_manage' => $v->bool('can_manage', false, false),
            'can_manage_household' => $v->bool('can_manage_household', false, false),
            'can_organize' => $v->bool('can_organize', false, false),
        ];
    }

    /** User._set_permissions */
    private function permissions(array $data): array
    {
        if ($data['admin']) {
            return ['admin' => true, 'can_manage_household' => true, 'can_manage' => true, 'can_invite' => true, 'can_organize' => true, 'advanced' => true];
        }

        return [
            'admin' => false,
            'can_manage_household' => $data['can_manage_household'],
            'can_manage' => $data['can_manage'],
            'can_invite' => $data['can_invite'],
            'can_organize' => $data['can_organize'],
        ];
    }

    /** Group by name, then household by name within it (User.__init__ / User.update). */
    private function resolveGroupHousehold(?string $group, ?string $household): array
    {
        $g = Db::table('groups')->where('name', $group)->first();
        $h = $g ? Db::table('households')->where('name', $household)->where('group_id', $g->id)->first() : null;

        return [$g, $h];
    }

    public function store(Request $request)
    {
        $v = Validator::body($request);
        $id = $v->uuid('id', false, true);
        $data = $this->base($v);
        $data['username'] = $v->str('username');
        $data['full_name'] = $v->str('full_name');
        $password = $v->str('password');
        $v->check();

        if (Db::table('users')->where('username', $data['username'])->exists()) {
            Errors::http(409, ['message' => 'This username is already taken']);
        }
        if (Db::table('users')->where('email', $data['email'])->exists()) {
            Errors::http(409, ['message' => 'This email is already in use']);
        }

        $groupName = $data['group'];
        $householdName = $data['household'];
        if ($groupName === null || $householdName === null) {
            $groupName = $groupName ?: Settings::get('DEFAULT_GROUP', 'Home');
            $householdName = $householdName ?: Settings::get('DEFAULT_HOUSEHOLD', 'Family');
        }
        [$g, $h] = $this->resolveGroupHousehold($groupName, $householdName);
        if ($g === null) {
            Errors::errorResponse(400, self::SERVER_ERROR, "Group {$groupName} does not exist; cannot create user");
        }
        if ($h === null) {
            Errors::errorResponse(400, self::SERVER_ERROR, "Household \"{$householdName}\" does not exist on group \"{$g->name}\" (".Guid::fromDb($g->id).'); cannot create user');
        }

        $id ??= Guid::new();
        $now = Dates::nowDb();
        $hash = preg_replace('/^\$2y\$/', '\$2b\$', password_hash(substr($password, 0, 72), PASSWORD_BCRYPT));
        $row = [
            'id' => $id,
            'created_at' => $now,
            'update_at' => $now,
            'full_name' => $data['full_name'],
            'username' => $data['username'] ?? $data['full_name'],
            'email' => $data['email'],
            'password' => $hash,
            'auth_method' => self::AUTH_METHODS[$data['auth_method']],
            'advanced' => $data['advanced'],
            'group_id' => $g->id,
            'household_id' => $h->id,
            'cache_key' => '1234',
            'login_attemps' => 0,
            'show_announcements' => $data['show_announcements'],
            'last_read_announcement' => $data['last_read_announcement'],
        ];
        $row = array_merge($row, $this->permissions($data));
        try {
            Db::table('users')->insert($row);
        } catch (QueryException $e) {
            LabelsController::integrity($e);
        }

        // RepositoryUsers.create: copy a random profile image into the user's directory
        $dir = Fs::dir('USER_DIR').'/'.Guid::fromDb($id);
        @mkdir($dir, 0755, true);
        $asset = dirname(base_path()).'/mealie/assets/users/random_'.random_int(1, 3).'.webp';
        if (is_file($asset)) {
            @copy($asset, $dir.'/profile.webp');
        }

        return Json::respond(Out::userOut($this->find($id)), 201);
    }

    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $v = Validator::body($request);
        $v->uuid('id');
        $data = $this->base($v);
        $data['group'] = $v->str('group');
        $data['household'] = $v->str('household');
        $groupId = $v->uuid('group_id');
        $v->str('group_slug');
        $householdId = $v->uuid('household_id');
        $v->str('household_slug');
        $cacheKey = $v->str('cache_key');
        [$hasTokens, $tokens] = $v->raw('tokens');
        if ($hasTokens && $tokens !== null && ! is_array($tokens)) {
            $v->error('tokens', 'list_type', 'Input should be a valid list');
        }
        $v->check();

        // Prevent self demotion
        $me = CurrentUser::get();
        if ($me->id === $id && (bool) $me->admin !== $data['admin']) {
            Errors::errorResponse(403, 'you cannot demote yourself');
        }

        if ($this->find($id) === null) {
            Checks::notFound();
        }

        // auto_init iterates the `tokens` relationship; the UserOut default (None) is not iterable
        if (! $hasTokens || $tokens === null) {
            Errors::errorResponse(400, self::SERVER_ERROR, "'NoneType' object is not iterable");
        }

        [$g, $h] = $this->resolveGroupHousehold($data['group'], $data['household']);
        $row = [
            'username' => $data['username'] ?? $data['full_name'],
            'full_name' => $data['full_name'],
            'email' => $data['email'],
            'auth_method' => self::AUTH_METHODS[$data['auth_method']],
            'advanced' => $data['advanced'],
            'show_announcements' => $data['show_announcements'],
            'last_read_announcement' => $data['last_read_announcement'],
            'cache_key' => $cacheKey,
            // the relationships win over the raw ids set by auto_init
            'group_id' => $g?->id,
            'household_id' => $h?->id,
            'update_at' => Dates::nowDb(),
        ];
        $row = array_merge($row, $this->permissions($data));
        if ($g === null) {
            Errors::errorResponse(409, 'Database integrity error', '(sqlite3.IntegrityError) NOT NULL constraint failed: users.group_id');
        }
        try {
            Db::table('users')->where('id', $id)->update($row);
        } catch (QueryException $e) {
            LabelsController::integrity($e);
        }

        return Json::respond(Out::userOut($this->find($id)));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $user = $this->find($id);
        if ($user === null) {
            Checks::noResult(self::SERVER_ERROR);
        }
        $out = Out::userOut($user);

        Db::conn()->transaction(function () use ($id) {
            Db::table('long_live_tokens')->where('user_id', $id)->delete();
            Db::table('recipe_comments')->where('user_id', $id)->delete();
            Db::table('recipe_timeline_events')->where('user_id', $id)->delete();
            Db::table('password_reset_tokens')->where('user_id', $id)->delete();
            Db::table('group_meal_plans')->where('user_id', $id)->delete();
            $lists = Db::table('shopping_lists')->where('user_id', $id)->pluck('id')->all();
            if ($lists) {
                $items = Db::table('shopping_list_items')->whereIn('shopping_list_id', $lists)->pluck('id')->all();
                if ($items) {
                    Db::table('shopping_list_item_recipe_reference')->whereIn('shopping_list_item_id', $items)->delete();
                    Db::table('shopping_list_item_extras')->whereIn('shopping_list_item_id', $items)->delete();
                }
                Db::table('shopping_list_items')->whereIn('shopping_list_id', $lists)->delete();
                Db::table('shopping_list_recipe_reference')->whereIn('shopping_list_id', $lists)->delete();
                Db::table('shopping_lists_multi_purpose_labels')->whereIn('shopping_list_id', $lists)->delete();
                Db::table('shopping_list_extras')->whereIn('shopping_list_id', $lists)->delete();
                Db::table('shopping_lists')->whereIn('id', $lists)->delete();
            }
            Db::table('users_to_recipes')->where('user_id', $id)->delete();
            Db::table('users')->where('id', $id)->delete();
        });
        Fs::rmtree(Fs::dir('USER_DIR').'/'.Guid::fromDb($id));

        return Json::respond($out);
    }

    /** POST /admin/users/unlock */
    public function unlock(Request $request)
    {
        $v = Validator::query($request);
        $force = $v->bool('force', false, false);
        $v->check();

        $hours = (int) (getenv('SECURITY_USER_LOCKOUT_TIME') ?: 24);
        $unlocked = 0;
        foreach (Db::table('users')->whereNotNull('locked_at')->get() as $user) {
            $expires = strtotime($user->locked_at.' UTC') + $hours * 3600;
            $isLocked = $expires > time();
            if ($force || ! $isLocked) {
                Db::table('users')->where('id', $user->id)->update([
                    'locked_at' => null, 'login_attemps' => 0, 'update_at' => Dates::nowDb(),
                ]);
                $unlocked++;
            }
        }

        return Json::respond(['unlocked' => $unlocked]);
    }

    /** POST /admin/users/password-reset-token */
    public function resetToken(Request $request)
    {
        $v = Validator::body($request);
        $email = $v->str('email');
        $v->check();

        $user = Db::table('users')->whereRaw('lower(email) = ?', [strtolower($email)])->first();
        if ($user === null || $user->auth_method === 'LDAP') {
            Errors::errorResponse(500, 'error while generating reset token');
        }

        $token = rtrim(strtr(base64_encode(random_bytes(24)), '+/', '-_'), '=');
        $now = Dates::nowDb();
        Db::table('password_reset_tokens')->insert([
            'user_id' => $user->id, 'token' => $token, 'created_at' => $now, 'update_at' => $now,
        ]);

        return Json::respond(['token' => $token], 201);
    }
}
