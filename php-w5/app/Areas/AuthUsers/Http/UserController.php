<?php

namespace App\Areas\AuthUsers\Http;

use App\Areas\AuthUsers\Support\Pyd;
use App\Areas\AuthUsers\Support\Translator;
use App\Areas\AuthUsers\Support\Users;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Throwable;

/** mealie/routes/users/crud.py, api_tokens.py, forgot_password.py (reset only) */
class UserController
{
    private const PERMISSIONS = ['can_invite', 'can_manage', 'can_manage_household', 'can_organize', 'admin'];

    /** GET /users/self */
    public function self(): JsonResponse
    {
        return Json::respond(Users::out(CurrentUser::get()));
    }

    /** GET /users/self/ratings and /users/self/favorites (UserRatingSummary) */
    public function selfRatings(): JsonResponse
    {
        return Json::respond(['ratings' => RatingsController::summaries(CurrentUser::id(), false)]);
    }

    public function selfFavorites(): JsonResponse
    {
        return Json::respond(['ratings' => RatingsController::summaries(CurrentUser::id(), true)]);
    }

    /** GET /users/self/ratings/{recipe_id} (crud.py:27) */
    public function selfRating(string $recipeId): JsonResponse
    {
        $v = new Pyd('users/crud.py', 27, 'get_logged_in_user_rating_for_recipe', 'GET', '/api/users/self/ratings/{recipe_id}');
        $recipe = $v->uuid('path', 'recipe_id', $recipeId);
        $v->done();

        $row = Users::db()->table('users_to_recipes')
            ->where('user_id', CurrentUser::id())->where('recipe_id', $recipe)->first();
        if ($row === null) {
            Errors::errorResponse(404, 'User has not rated this recipe');
        }

        return Json::respond(RatingsController::summary($row));
    }

    /** PUT /users/password (crud.py:42) */
    public function updatePassword(Request $request): JsonResponse
    {
        $v = new Pyd('users/crud.py', 42, 'update_password', 'PUT', '/api/users/password');
        $data = $v->fields($v->bodyObject($request), [
            ['name' => 'current_password', 'alias' => 'currentPassword', 'type' => 'str', 'default' => ''],
            ['name' => 'new_password', 'alias' => 'newPassword', 'type' => 'str', 'required' => true, 'min_length' => 8],
        ]);
        $v->done();

        $user = CurrentUser::get();
        if ($user->auth_method === 'LDAP') {
            Errors::errorResponse(400, Translator::t($request, 'user.ldap-update-password-unavailable'));
        }
        if (! Users::verifyPassword($data['current_password'], $user->password)) {
            Errors::errorResponse(400, Translator::t($request, 'user.invalid-current-password'));
        }

        try {
            $now = Dates::nowDb();
            Users::db()->table('users')->where('id', $user->id)->update([
                'password' => Users::hashPassword($data['new_password']),
                // User.update_password: floored to the second
                'tokens_valid_after' => substr($now, 0, 19).'.000000',
                'update_at' => $now,
            ]);
        } catch (Throwable) {
            Errors::errorResponse(400, 'Failed to update password');
        }

        return Json::respond(['message' => Translator::t($request, 'user.password-updated'), 'error' => false]);
    }

    /** PUT /users/{item_id} (crud.py:65) */
    public function updateUser(Request $request, string $itemId): JsonResponse
    {
        $v = new Pyd('users/crud.py', 65, 'update_user', 'PUT', '/api/users/{item_id}');
        $id = $v->uuid('path', 'item_id', $itemId);
        $data = $v->fields($v->bodyObject($request), [
            ['name' => 'id', 'type' => 'uuid4', 'nullable' => true],
            ['name' => 'username', 'type' => 'str', 'nullable' => true],
            ['name' => 'full_name', 'alias' => 'fullName', 'type' => 'str', 'nullable' => true],
            ['name' => 'email', 'type' => 'str', 'required' => true, 'lower' => true, 'strip' => true],
            ['name' => 'auth_method', 'alias' => 'authMethod', 'type' => 'enum', 'enum' => ['Mealie', 'LDAP', 'OIDC'], 'default' => 'Mealie'],
            ['name' => 'admin', 'type' => 'bool', 'default' => false],
            ['name' => 'group', 'type' => 'str', 'nullable' => true],
            ['name' => 'household', 'type' => 'str', 'nullable' => true],
            ['name' => 'advanced', 'type' => 'bool', 'default' => false],
            ['name' => 'show_announcements', 'alias' => 'showAnnouncements', 'type' => 'bool', 'default' => true],
            ['name' => 'last_read_announcement', 'alias' => 'lastReadAnnouncement', 'type' => 'str', 'nullable' => true],
            ['name' => 'can_invite', 'alias' => 'canInvite', 'type' => 'bool', 'default' => false],
            ['name' => 'can_manage', 'alias' => 'canManage', 'type' => 'bool', 'default' => false],
            ['name' => 'can_manage_household', 'alias' => 'canManageHousehold', 'type' => 'bool', 'default' => false],
            ['name' => 'can_organize', 'alias' => 'canOrganize', 'type' => 'bool', 'default' => false],
        ]);
        $v->done();

        $user = CurrentUser::get();
        self::assertChangeAllowed($id, $user, $data);

        // User.update (mealie/db/models/users/users.py:183) via auto_init
        $db = Users::db();
        try {
            $group = $data['group'] === null ? null : $db->table('groups')->where('name', $data['group'])->first();
            $household = $group === null ? null
                : $db->table('households')->where('name', $data['household'])->where('group_id', $group->id)->first();
            if ($group === null) {
                throw new \RuntimeException('group_id may not be null');
            }
            $admin = $data['admin'];
            $changes = [
                'username' => $data['username'] ?? $data['full_name'],
                'full_name' => $data['full_name'],
                'email' => $data['email'],
                'auth_method' => array_search($data['auth_method'], Users::AUTH_METHODS, true),
                'advanced' => $admin ? true : $data['advanced'],
                'show_announcements' => $data['show_announcements'],
                'last_read_announcement' => $data['last_read_announcement'],
                'group_id' => $group->id,
                'household_id' => $household?->id,
                'admin' => $admin,
                'can_manage_household' => $admin ? true : $data['can_manage_household'],
                'can_manage' => $admin ? true : $data['can_manage'],
                'can_invite' => $admin ? true : $data['can_invite'],
                'can_organize' => $admin ? true : $data['can_organize'],
            ];
            $db->transaction(fn () => Users::update($db->table('users')->where('id', $id)->where('group_id', $user->group_id)->first(), $changes));
        } catch (Throwable) {
            Errors::errorResponse(400, 'Failed to update user');
        }

        return Json::respond(['message' => Translator::t($request, 'user.user-updated'), 'error' => false]);
    }

    /**
     * mealie/routes/users/_helpers.py assert_user_change_allowed.
     * $new holds the permission flags and group/household names to compare (null => compare the caller to itself).
     */
    public static function assertChangeAllowed(string $id, object $user, ?array $new = null): void
    {
        if ($new === null) {
            $new = [];
            foreach (self::PERMISSIONS as $p) {
                $new[$p] = (bool) $user->{$p};
            }
            $new['group'] = Users::groupName($user);
            $new['household'] = Users::householdName($user);
        }
        $permChanged = false;
        foreach (self::PERMISSIONS as $p) {
            if ((bool) $user->{$p} !== $new[$p]) {
                $permChanged = true;
            }
        }

        if (! $user->admin) {
            if ($user->id !== $id) {
                Errors::errorResponse(403, 'User cannot edit other users');
            }
            if ($permChanged) {
                Errors::errorResponse(403, 'User cannot change their own permissions');
            }
            if (Users::groupName($user) !== $new['group']) {
                Errors::errorResponse(403, "User doesn't have permission to change their group");
            }
            if (Users::householdName($user) !== $new['household']) {
                Errors::errorResponse(403, "User doesn't have permission to change their household");
            }

            return;
        }

        if ($user->id !== $id) {
            Errors::errorResponse(403, 'Use the Admin API to update other users');
        }
        if ($permChanged) {
            Errors::errorResponse(403, "Admins can't change their own permissions");
        }
    }

    /** POST /users/reset-password (forgot_password.py:24, password_reset_service.py:51) */
    public function resetPassword(Request $request): JsonResponse
    {
        $v = new Pyd('users/forgot_password.py', 24, 'reset_password', 'POST', '/api/users/reset-password');
        $data = $v->fields($v->bodyObject($request), [
            ['name' => 'token', 'type' => 'str', 'required' => true],
            ['name' => 'email', 'type' => 'str', 'required' => true],
            ['name' => 'password', 'type' => 'str', 'required' => true],
            ['name' => 'passwordConfirm', 'type' => 'str', 'required' => true],
        ]);
        $v->done();

        $db = Users::db();
        $entry = $db->table('password_reset_tokens')->where('token', $data['token'])->first();
        if ($entry === null) {
            Errors::http(400, 'Invalid token');
        }
        $now = Dates::nowDb();
        $db->table('users')->where('id', $entry->user_id)->update([
            'password' => Users::hashPassword($data['password']),
            'tokens_valid_after' => substr($now, 0, 19).'.000000',
            'update_at' => $now,
        ]);
        $db->table('password_reset_tokens')->where('id', $entry->id)->delete();

        return JsonResponse::fromJsonString('null');
    }

    /** POST /users/api-tokens (api_tokens.py:21) */
    public function createApiToken(Request $request): JsonResponse
    {
        $v = new Pyd('users/api_tokens.py', 21, 'create_api_token', 'POST', '/api/users/api-tokens');
        $data = $v->fields($v->bodyObject($request), [
            ['name' => 'name', 'type' => 'str', 'required' => true],
            ['name' => 'integration_id', 'alias' => 'integrationId', 'type' => 'str', 'default' => 'generic'],
        ]);
        $v->done();

        $user = CurrentUser::get();
        [$token] = Users::createAccessToken([
            'long_token' => true,
            'id' => Guid::fromDb($user->id),
            'name' => $data['name'],
            'integration_id' => $data['integration_id'],
        ], 1825 * 86400);

        $now = Dates::nowDb();
        $id = Users::db()->table('long_live_tokens')->insertGetId([
            'created_at' => $now,
            'update_at' => $now,
            'name' => $data['name'],
            'token' => $token,
            'user_id' => $user->id,
        ]);

        return Json::respond([
            'name' => $data['name'],
            'id' => (int) $id,
            'createdAt' => null, // Python returns the token before created_at is loaded
            'token' => $token,
        ], 201);
    }

    /** DELETE /users/api-tokens/{token_id} (api_tokens.py:49) */
    public function deleteApiToken(string $tokenId): JsonResponse
    {
        $v = new Pyd('users/api_tokens.py', 49, 'delete_api_token', 'DELETE', '/api/users/api-tokens/{token_id}');
        $id = $v->int('path', 'token_id', $tokenId);
        $v->done();

        $user = CurrentUser::get();
        $db = Users::db();
        // group repository: the token's user must be in the caller's group
        $token = $db->table('long_live_tokens')
            ->join('users', 'users.id', '=', 'long_live_tokens.user_id')
            ->where('long_live_tokens.id', $id)
            ->where('users.group_id', $user->group_id)
            ->select('long_live_tokens.*')
            ->first();
        if ($token === null) {
            Errors::http(404, "Could not locate token with id '{$id}' in database");
        }
        if ($token->user_id !== $user->id) {
            Errors::http(403, 'Forbidden');
        }
        $db->table('long_live_tokens')->where('id', $id)->delete();

        return Json::respond(['tokenDelete' => $token->name]);
    }
}
