<?php

namespace App\Services;

use App\Auth\Jwt;
use App\Support\Guid;
use App\Support\Images;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;

final class AccountService
{
    /**
     * @return array<string, mixed>
     */
    public function userOut(object $user): array
    {
        $group = MealieDb::table('groups')->where('id', $user->group_id)->first();
        $household = $user->household_id
            ? MealieDb::table('households')->where('id', $user->household_id)->first()
            : null;
        $tokens = MealieDb::table('long_live_tokens')->where('user_id', $user->id)->get()
            ->map(fn ($token) => [
                'name' => $token->name,
                'id' => (int) $token->id,
                'createdAt' => JsonShape::dateTime($token->created_at ?? null),
            ])->all();

        return JsonShape::camel([
            'id' => Guid::dashed($user->id),
            'username' => $user->username,
            'full_name' => $user->full_name,
            'email' => $user->email,
            'auth_method' => $user->auth_method ?? 'MEALIE',
            'admin' => JsonShape::bool($user->admin),
            'group' => $group->name ?? '',
            'household' => $household->name ?? '',
            'advanced' => JsonShape::bool($user->advanced),
            'show_announcements' => JsonShape::bool($user->show_announcements ?? true),
            'last_read_announcement' => $user->last_read_announcement,
            'can_invite' => JsonShape::bool($user->can_invite),
            'can_manage' => JsonShape::bool($user->can_manage),
            'can_manage_household' => JsonShape::bool($user->can_manage_household),
            'can_organize' => JsonShape::bool($user->can_organize),
            'group_id' => Guid::dashed($user->group_id),
            'group_slug' => $group->slug ?? '',
            'household_id' => Guid::dashed($user->household_id),
            'household_slug' => $household->slug ?? '',
            'tokens' => $tokens,
            'cache_key' => $user->cache_key ?? '',
        ]);
    }

    /**
     * @return array<string, mixed>
     */
    public function groupSelf(object $user): array
    {
        $group = MealieDb::table('groups')->where('id', $user->group_id)->first();
        $preferences = MealieDb::table('group_preferences')->where('group_id', $user->group_id)->first();

        return JsonShape::camel([
            'id' => Guid::dashed($group->id),
            'name' => $group->name,
            'slug' => $group->slug,
            'preferences' => $preferences ? $this->groupPreferences($preferences) : null,
            'ai_provider_settings' => null,
        ]);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function groupPreferencesFor(object $user): ?array
    {
        $preferences = MealieDb::table('group_preferences')->where('group_id', $user->group_id)->first();

        return $preferences ? JsonShape::camel($this->groupPreferences($preferences)) : null;
    }

    /**
     * @return array<string, mixed>
     */
    public function householdSelf(object $user): array
    {
        $household = MealieDb::table('households')->where('id', $user->household_id)->first();
        $group = MealieDb::table('groups')->where('id', $user->group_id)->first();
        $preferences = MealieDb::table('household_preferences')->where('household_id', $user->household_id)->first();
        $users = MealieDb::table('users')->where('household_id', $user->household_id)->get()
            ->map(fn ($member) => [
                'id' => Guid::dashed($member->id),
                'fullName' => $member->full_name,
            ])->all();

        return [
            'id' => Guid::dashed($household->id),
            'name' => $household->name,
            'slug' => $household->slug,
            'groupId' => Guid::dashed($household->group_id),
            'group' => $group->name ?? '',
            'preferences' => $preferences ? JsonShape::camel($this->householdPreferences($preferences)) : null,
            'users' => $users,
            'webhooks' => [],
        ];
    }

    /**
     * @return array<string, mixed>|null
     */
    public function householdPreferencesFor(object $user): ?array
    {
        $preferences = MealieDb::table('household_preferences')->where('household_id', $user->household_id)->first();

        return $preferences ? JsonShape::camel($this->householdPreferences($preferences)) : null;
    }

    /**
     * @return array<string, int>
     */
    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateGroupPreferences(object $user, array $payload): ?array
    {
        $row = MealieDb::table('group_preferences')->where('group_id', $user->group_id)->first();
        if ($row === null) {
            return null;
        }
        $fields = ['update_at' => MealieDb::now()];
        if (array_key_exists('privateGroup', $payload) || array_key_exists('private_group', $payload)) {
            $fields['private_group'] = JsonShape::bool($payload['privateGroup'] ?? $payload['private_group']) ? 1 : 0;
        }
        if (array_key_exists('showAnnouncements', $payload) || array_key_exists('show_announcements', $payload)) {
            $fields['show_announcements'] = JsonShape::bool($payload['showAnnouncements'] ?? $payload['show_announcements']) ? 1 : 0;
        }
        MealieDb::table('group_preferences')->where('id', $row->id)->update($fields);

        return $this->groupPreferencesFor($user);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateHouseholdPreferences(object $user, array $payload): ?array
    {
        $row = MealieDb::table('household_preferences')->where('household_id', $user->household_id)->first();
        if ($row === null) {
            return null;
        }
        $map = [
            'privateHousehold' => 'private_household',
            'showAnnouncements' => 'show_announcements',
            'lockRecipeEditsFromOtherHouseholds' => 'lock_recipe_edits_from_other_households',
            'firstDayOfWeek' => 'first_day_of_week',
            'recipePublic' => 'recipe_public',
            'recipeShowNutrition' => 'recipe_show_nutrition',
            'recipeShowAssets' => 'recipe_show_assets',
            'recipeLandscapeView' => 'recipe_landscape_view',
            'recipeDisableComments' => 'recipe_disable_comments',
        ];
        $fields = ['update_at' => MealieDb::now()];
        foreach ($map as $camel => $column) {
            $snake = strtolower(preg_replace('/[A-Z]/', '_$0', $camel) ?? $camel);
            if (! array_key_exists($camel, $payload) && ! array_key_exists($snake, $payload)) {
                continue;
            }
            $value = $payload[$camel] ?? $payload[$snake];
            $fields[$column] = $column === 'first_day_of_week' ? (int) $value : (JsonShape::bool($value) ? 1 : 0);
        }
        MealieDb::table('household_preferences')->where('id', $row->id)->update($fields);

        return $this->householdPreferencesFor($user);
    }

    /**
     * @return array<string, mixed>
     */
    public function members(object $user, string $scope, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('users')->where($scope === 'group' ? 'group_id' : 'household_id', $scope === 'group' ? $user->group_id : $user->household_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('username')->forPage($query['page'], max($query['perPage'], 1))->get();
        $items = $scope === 'group'
            ? $rows->map(fn ($row) => [
                'id' => Guid::dashed($row->id),
                'groupId' => Guid::dashed($row->group_id),
                'householdId' => Guid::dashed($row->household_id),
                'username' => $row->username,
                'fullName' => $row->full_name,
            ])->all()
            : $rows->map(fn ($row) => $this->userOut($row))->all();

        return Pages::make($items, $query['page'], $query['perPage'], $total);
    }

    public function householdStatistics(object $user): array
    {
        $groupId = $user->group_id;

        return [
            'totalRecipes' => MealieDb::table('recipes')->where('group_id', $groupId)->count(),
            'totalUsers' => MealieDb::table('users')->where('household_id', $user->household_id)->count(),
            'totalCategories' => MealieDb::table('categories')->where('group_id', $groupId)->count(),
            'totalTags' => MealieDb::table('tags')->where('group_id', $groupId)->count(),
            'totalTools' => MealieDb::table('tools')->where('group_id', $groupId)->count(),
        ];
    }

    /**
     * @return array{ratings: list<array<string, mixed>>}
     */
    public function ratings(object $user, bool $favoritesOnly = false): array
    {
        $query = MealieDb::table('users_to_recipes')->where('user_id', $user->id);
        if ($favoritesOnly) {
            $query->where('is_favorite', 1);
        }

        $ratings = $query->get()->map(fn ($row) => [
            'recipeId' => Guid::dashed($row->recipe_id),
            'rating' => $row->rating === null ? null : (float) $row->rating,
            'isFavorite' => JsonShape::bool($row->is_favorite),
        ])->all();

        return ['ratings' => $ratings];
    }

    /**
     * @return array<string, mixed>|null
     */
    public function setRating(object $user, string $slug, ?float $rating, ?bool $favorite): ?array
    {
        $recipe = MealieDb::table('recipes')->where('group_id', $user->group_id)->where('slug', $slug)->first()
            ?? MealieDb::table('recipes')->where('group_id', $user->group_id)->where('id', Guid::hex($slug))->first();
        if ($recipe === null) {
            return null;
        }

        $existing = MealieDb::table('users_to_recipes')->where('user_id', $user->id)->where('recipe_id', $recipe->id)->first();
        $now = MealieDb::now();
        if ($existing === null) {
            MealieDb::table('users_to_recipes')->insert([
                'id' => Guid::newHex(),
                'user_id' => $user->id,
                'recipe_id' => $recipe->id,
                'rating' => $rating,
                'is_favorite' => ($favorite ?? false) ? 1 : 0,
                'created_at' => $now,
                'update_at' => $now,
            ]);
        } else {
            $fields = ['update_at' => $now];
            if ($rating !== null) {
                $fields['rating'] = $rating;
            }
            if ($favorite !== null) {
                $fields['is_favorite'] = $favorite ? 1 : 0;
            }
            MealieDb::table('users_to_recipes')->where('id', $existing->id)->update($fields);
        }

        $row = MealieDb::table('users_to_recipes')->where('user_id', $user->id)->where('recipe_id', $recipe->id)->first();

        return [
            'recipeId' => Guid::dashed($recipe->id),
            'rating' => $row->rating === null ? null : (float) $row->rating,
            'isFavorite' => JsonShape::bool($row->is_favorite),
        ];
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function register(array $payload): array
    {
        $token = $payload['groupToken'] ?? $payload['group_token'] ?? null;
        if (! config('mealie.allow_signup') && ($token === null || $token === '')) {
            throw new \RuntimeException('disabled');
        }
        $password = (string) ($payload['password'] ?? '');
        $confirm = (string) ($payload['passwordConfirm'] ?? $payload['password_confirm'] ?? '');
        if ($password === '' || $password !== $confirm) {
            throw new \InvalidArgumentException('passwords do not match');
        }

        $group = null;
        $household = null;
        if (is_string($token) && $token !== '') {
            $invite = MealieDb::table('invite_tokens')->where('token', $token)->where('uses_left', '>', 0)->first();
            if ($invite === null) {
                throw new \InvalidArgumentException('invalid token');
            }
            $group = MealieDb::table('groups')->where('id', $invite->group_id)->first();
            $household = MealieDb::table('households')->where('id', $invite->household_id)->first();
            MealieDb::table('invite_tokens')->where('id', $invite->id)->update(['uses_left' => ((int) $invite->uses_left) - 1]);
        } else {
            $groupName = $payload['group'] ?? config('mealie.default_group');
            $group = MealieDb::table('groups')->where('name', $groupName)->first();
            if ($group) {
                $householdName = $payload['household'] ?? config('mealie.default_household');
                $household = MealieDb::table('households')->where('group_id', $group->id)->where('name', $householdName)->first();
            }
        }
        if ($group === null || $household === null) {
            throw new \InvalidArgumentException('group not found');
        }

        $email = strtolower(trim((string) ($payload['email'] ?? '')));
        $username = strtolower(trim((string) ($payload['username'] ?? '')));
        if (MealieDb::table('users')->where('email', $email)->orWhere('username', $username)->exists()) {
            throw new \InvalidArgumentException('user exists');
        }

        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('users')->insert([
            'id' => $id,
            'username' => $username,
            'full_name' => trim((string) ($payload['fullName'] ?? $payload['full_name'] ?? $username)),
            'email' => $email,
            'password' => password_hash(substr($password, 0, 72), PASSWORD_BCRYPT),
            'admin' => 0,
            'advanced' => JsonShape::bool($payload['advanced'] ?? false) ? 1 : 0,
            'group_id' => $group->id,
            'household_id' => $household->id,
            'auth_method' => 'MEALIE',
            'can_manage' => 0,
            'can_invite' => 0,
            'can_organize' => 0,
            'can_manage_household' => 0,
            'cache_key' => bin2hex(random_bytes(8)),
            'login_attemps' => 0,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->userOut(MealieDb::table('users')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function updateSelf(object $user, array $payload): array
    {
        $fields = ['update_at' => MealieDb::now()];
        foreach ([
            'username' => 'username',
            'fullName' => 'full_name',
            'email' => 'email',
            'advanced' => 'advanced',
            'showAnnouncements' => 'show_announcements',
            'lastReadAnnouncement' => 'last_read_announcement',
        ] as $key => $column) {
            if (! array_key_exists($key, $payload) && ! array_key_exists($column, $payload)) {
                continue;
            }
            $value = $payload[$key] ?? $payload[$column];
            $fields[$column] = in_array($column, ['advanced', 'show_announcements'], true)
                ? (JsonShape::bool($value) ? 1 : 0)
                : $value;
        }
        MealieDb::table('users')->where('id', $user->id)->update($fields);

        return $this->userOut(MealieDb::table('users')->where('id', $user->id)->first());
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function tokens(object $user): array
    {
        return MealieDb::table('long_live_tokens')->where('user_id', $user->id)->orderByDesc('id')->get()
            ->map(fn ($row) => [
                'name' => $row->name,
                'id' => (int) $row->id,
                'createdAt' => JsonShape::dateTime($row->created_at),
            ])->all();
    }

    /**
     * @return array<string, mixed>
     */
    public function createToken(object $user, string $name): array
    {
        $now = time();
        $token = Jwt::encode([
            'sub' => Guid::dashed($user->id),
            'rme' => true,
            'iss' => 'mealie',
            'iat' => $now,
            'exp' => $now + (86400 * 365 * 10),
        ], Jwt::secret());
        $id = MealieDb::table('long_live_tokens')->insertGetId([
            'name' => $name !== '' ? $name : 'Token',
            'token' => $token,
            'user_id' => $user->id,
            'created_at' => MealieDb::now(),
            'update_at' => MealieDb::now(),
        ]);

        return [
            'name' => $name,
            'id' => (int) $id,
            'token' => $token,
            'createdAt' => JsonShape::dateTime(MealieDb::now()),
        ];
    }

    public function deleteToken(object $user, int $id): bool
    {
        return MealieDb::table('long_live_tokens')->where('id', $id)->where('user_id', $user->id)->delete() > 0;
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function setPermissions(object $actor, array $payload): ?array
    {
        if (! JsonShape::bool($actor->can_manage ?? false) && ! JsonShape::bool($actor->admin)) {
            return null;
        }
        $targetId = Guid::hex((string) ($payload['userId'] ?? $payload['user_id'] ?? ''));
        $target = $targetId === null ? null : MealieDb::table('users')->where('id', $targetId)->first();
        if ($target === null || $target->household_id !== $actor->household_id || $target->id === $actor->id) {
            return null;
        }
        MealieDb::table('users')->where('id', $target->id)->update([
            'can_invite' => JsonShape::bool($payload['canInvite'] ?? $payload['can_invite'] ?? false) ? 1 : 0,
            'can_manage' => JsonShape::bool($payload['canManage'] ?? $payload['can_manage'] ?? false) ? 1 : 0,
            'can_manage_household' => JsonShape::bool($payload['canManageHousehold'] ?? $payload['can_manage_household'] ?? false) ? 1 : 0,
            'can_organize' => JsonShape::bool($payload['canOrganize'] ?? $payload['can_organize'] ?? false) ? 1 : 0,
            'update_at' => MealieDb::now(),
        ]);

        return $this->userOut(MealieDb::table('users')->where('id', $target->id)->first());
    }

    public function forgotPassword(string $email): void
    {
        $user = MealieDb::table('users')->whereRaw('lower(email) = ?', [strtolower($email)])->first();
        if ($user === null) {
            return;
        }
        $token = bin2hex(random_bytes(16));
        MealieDb::table('password_reset_tokens')->insert([
            'user_id' => $user->id,
            'token' => $token,
            'created_at' => MealieDb::now(),
            'update_at' => MealieDb::now(),
        ]);
        if (config('mealie.smtp_enabled')) {
            app(MailService::class)->send(
                $email,
                'Reset your Mealie password',
                'Open this link to choose a new password: '.rtrim((string) config('mealie.base_url'), '/').'/reset-password?token='.$token,
            );
        }
    }

    public function resetPassword(string $token, string $password): bool
    {
        $row = MealieDb::table('password_reset_tokens')->where('token', $token)->first();
        if ($row === null || strlen($password) < 8) {
            return false;
        }
        MealieDb::table('users')->where('id', $row->user_id)->update([
            'password' => password_hash(substr($password, 0, 72), PASSWORD_BCRYPT),
            'tokens_valid_after' => MealieDb::now(),
            'update_at' => MealieDb::now(),
        ]);
        MealieDb::table('password_reset_tokens')->where('id', $row->id)->delete();

        return true;
    }

    public function saveUserImage(object $actor, string $id, string $bytes): bool
    {
        $hex = Guid::hex($id);
        if ($hex === null || $bytes === '' || ($hex !== $actor->id && ! JsonShape::bool($actor->admin))) {
            return false;
        }
        $dir = rtrim((string) config('mealie.data_dir'), '/').'/users/'.Guid::dashed($hex);
        if (! is_dir($dir) && ! mkdir($dir, 0775, true) && ! is_dir($dir)) {
            return false;
        }
        Images::writeSet($dir, $bytes);
        if (is_file($dir.'/original.webp')) {
            copy($dir.'/original.webp', $dir.'/profile.webp');
        }
        MealieDb::table('users')->where('id', $hex)->update([
            'cache_key' => bin2hex(random_bytes(6)),
            'update_at' => MealieDb::now(),
        ]);

        return true;
    }

    public function changePassword(object $user, string $current, string $next): bool
    {
        if (($user->auth_method ?? 'MEALIE') !== 'MEALIE') {
            return false;
        }
        if (! password_verify(substr($current, 0, 72), (string) $user->password)) {
            return false;
        }

        MealieDb::table('users')->where('id', $user->id)->update([
            'password' => password_hash(substr($next, 0, 72), PASSWORD_BCRYPT),
            'tokens_valid_after' => MealieDb::now(),
            'update_at' => MealieDb::now(),
        ]);

        return true;
    }

    /**
     * @return array<string, mixed>
     */
    public function about(): array
    {
        $group = MealieDb::table('groups')->where('name', config('mealie.default_group'))->first();
        $groupSlug = null;
        $householdSlug = null;
        if ($group) {
            $preferences = MealieDb::table('group_preferences')->where('group_id', $group->id)->first();
            if ($preferences && ! JsonShape::bool($preferences->private_group)) {
                $groupSlug = $group->slug;
                $household = MealieDb::table('households')
                    ->where('group_id', $group->id)
                    ->where('name', config('mealie.default_household'))
                    ->first();
                if ($household) {
                    $householdPreferences = MealieDb::table('household_preferences')->where('household_id', $household->id)->first();
                    if ($householdPreferences && ! JsonShape::bool($householdPreferences->private_household)) {
                        $householdSlug = $household->slug;
                    }
                }
            }
        }

        return [
            'production' => (bool) config('mealie.production'),
            'version' => (string) config('mealie.version'),
            'demoStatus' => (bool) config('mealie.demo'),
            'allowSignup' => (bool) config('mealie.allow_signup'),
            'allowPasswordLogin' => (bool) config('mealie.allow_password_login'),
            'defaultGroupSlug' => $groupSlug,
            'defaultHouseholdSlug' => $householdSlug,
            'enableOidc' => false,
            'oidcRedirect' => false,
            'oidcProviderName' => '',
            'tokenTime' => (int) config('mealie.token_hours'),
            'allowedIframeHosts' => [],
        ];
    }

    /**
     * @return array<string, mixed>
     */
    public function startup(): array
    {
        $exists = MealieDb::table('users')->where('email', config('mealie.default_email'))->exists();

        return [
            'isFirstLogin' => $exists,
            'isDemo' => (bool) config('mealie.demo'),
        ];
    }

    /**
     * @return array<string, string>
     */
    public function theme(): array
    {
        return [
            'lightPrimary' => '#E58325',
            'lightAccent' => '#007A99',
            'lightSecondary' => '#973542',
            'lightSuccess' => '#43A047',
            'lightInfo' => '#1976D2',
            'lightWarning' => '#FF6D00',
            'lightError' => '#EF5350',
            'darkPrimary' => '#E58325',
            'darkAccent' => '#007A99',
            'darkSecondary' => '#973542',
            'darkSuccess' => '#43A047',
            'darkInfo' => '#1976D2',
            'darkWarning' => '#FF6D00',
            'darkError' => '#EF5350',
        ];
    }

    /**
     * @return array{page: int, perPage: int}
     */
    public function pageQuery(Request $request): array
    {
        $page = Pages::query($request);

        return ['page' => $page['page'], 'perPage' => $page['perPage']];
    }

    /**
     * @return array<string, mixed>
     */
    private function groupPreferences(object $preferences): array
    {
        return [
            'id' => Guid::dashed($preferences->id),
            'group_id' => Guid::dashed($preferences->group_id),
            'private_group' => JsonShape::bool($preferences->private_group),
            'show_announcements' => JsonShape::bool($preferences->show_announcements ?? true),
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function householdPreferences(object $preferences): array
    {
        return [
            'id' => Guid::dashed($preferences->id),
            'private_household' => JsonShape::bool($preferences->private_household),
            'show_announcements' => JsonShape::bool($preferences->show_announcements ?? true),
            'lock_recipe_edits_from_other_households' => JsonShape::bool($preferences->lock_recipe_edits_from_other_households ?? true),
            'first_day_of_week' => (int) $preferences->first_day_of_week,
            'recipe_public' => JsonShape::bool($preferences->recipe_public),
            'recipe_show_nutrition' => JsonShape::bool($preferences->recipe_show_nutrition),
            'recipe_show_assets' => JsonShape::bool($preferences->recipe_show_assets),
            'recipe_landscape_view' => JsonShape::bool($preferences->recipe_landscape_view),
            'recipe_disable_comments' => JsonShape::bool($preferences->recipe_disable_comments),
        ];
    }
}
