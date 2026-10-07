<?php

namespace App\Areas\AuthUsers\Support;

use App\Auth\Jwt;
use App\Support\Dates;
use App\Support\Guid;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class Users
{
    public static function db()
    {
        return DB::connection('mealie');
    }

    /** users.auth_method stores the enum name; the API returns the value. */
    public const AUTH_METHODS = ['MEALIE' => 'Mealie', 'LDAP' => 'LDAP', 'OIDC' => 'OIDC'];

    /** UserOut (mealie/schema/user/user.py:170) in field order. */
    public static function out(object $user): array
    {
        $db = self::db();
        $group = $db->table('groups')->where('id', $user->group_id)->first();
        $household = $user->household_id ? $db->table('households')->where('id', $user->household_id)->first() : null;
        $tokens = $db->table('long_live_tokens')->where('user_id', $user->id)->orderBy('id')->get();

        return [
            'id' => Guid::fromDb($user->id),
            'username' => $user->username,
            'fullName' => $user->full_name,
            'email' => $user->email,
            'authMethod' => self::AUTH_METHODS[$user->auth_method] ?? $user->auth_method,
            'admin' => (bool) $user->admin,
            'group' => $group?->name,
            'household' => $household?->name,
            'advanced' => (bool) $user->advanced,
            'showAnnouncements' => (bool) $user->show_announcements,
            'lastReadAnnouncement' => $user->last_read_announcement,
            'canInvite' => (bool) $user->can_invite,
            'canManage' => (bool) $user->can_manage,
            'canManageHousehold' => (bool) $user->can_manage_household,
            'canOrganize' => (bool) $user->can_organize,
            'groupId' => Guid::fromDb($user->group_id),
            'groupSlug' => $group?->slug,
            'householdId' => Guid::fromDb($user->household_id),
            'householdSlug' => $household?->slug,
            'tokens' => $tokens->map(fn ($t) => [
                'name' => $t->name,
                'id' => (int) $t->id,
                'createdAt' => Dates::out($t->created_at),
            ])->all(),
            'cacheKey' => $user->cache_key,
        ];
    }

    /** Group and household names of a users row (PrivateUser.group / .household). */
    public static function groupName(object $user): ?string
    {
        return self::db()->table('groups')->where('id', $user->group_id)->value('name');
    }

    public static function householdName(object $user): ?string
    {
        return $user->household_id ? self::db()->table('households')->where('id', $user->household_id)->value('name') : null;
    }

    // ---------------------------------------------------------------- passwords (BcryptHasher)

    public static function verifyPassword(string $plain, ?string $hash): bool
    {
        if ($hash === null || $hash === '') {
            return false;
        }

        return password_verify(substr($plain, 0, 72), $hash);
    }

    public static function hashPassword(string $plain): string
    {
        $hash = password_hash(substr($plain, 0, 72), PASSWORD_BCRYPT, ['cost' => 12]);

        return '$2b$'.substr($hash, 4);
    }

    public static function fakeVerify(): void
    {
        password_verify('abc123cba321', '$2b$12$JdHtJOlkPFwyxdjdygEzPOtYmdQF5/R5tHxw5Tq8pxjubyLqdIX5i');
    }

    // ---------------------------------------------------------------- tokens (mealie/core/security/tokens.py)

    /** @return array{0: string, 1: int} token and lifetime in seconds */
    public static function createAccessToken(array $data, ?int $seconds = null): array
    {
        $seconds ??= Settings::tokenTime() * 3600;
        $now = time();
        $claims = $data + ['iss' => 'mealie', 'iat' => $now, 'exp' => $now + $seconds];

        return [Jwt::encode($claims, Jwt::secret()), $seconds];
    }

    /** MealieAuthToken.respond + set_session_cookie (auth.py:100). */
    public static function tokenResponse(Request $request, string $token, int $seconds, bool $rememberMe): JsonResponse
    {
        $response = response()->json([
            'access_token' => $token,
            'token_type' => 'bearer',
            'expires_in' => $seconds,
        ]);
        $attrs = self::cookieAttrs($request);
        $cookie = 'mealie.access_token='.$token.($rememberMe ? '; Max-Age='.$seconds : '').'; Path=/; SameSite='.$attrs['samesite']
            .($attrs['secure'] ? '; Secure' : '').($attrs['partitioned'] ? '; Partitioned' : '');
        $response->headers->set('set-cookie', $cookie, false);

        return $response;
    }

    /** session_cookie_attrs (auth.py:82). */
    public static function cookieAttrs(Request $request): array
    {
        $secure = $request->getScheme() === 'https'
            || strtolower(trim(explode(',', (string) $request->headers->get('x-forwarded-proto', ''))[0])) === 'https';
        $embedded = $secure && strtolower((string) $request->headers->get('x-mealie-embedded', '')) === 'true';

        return ['secure' => $secure, 'samesite' => $embedded ? 'none' : 'lax', 'partitioned' => $embedded];
    }

    /** Store a users row update; stamps update_at only when a column changed (SQLAlchemy onupdate). */
    public static function update(object $user, array $changes): void
    {
        $diff = [];
        foreach ($changes as $col => $value) {
            $current = $user->{$col} ?? null;
            if (is_bool($value)) {
                $same = $current !== null && (bool) $current === $value;
            } else {
                $same = $current === $value || ($current !== null && $value !== null && (string) $current === (string) $value);
            }
            if (! $same) {
                $diff[$col] = is_bool($value) ? (int) $value : $value;
            }
        }
        if ($diff === []) {
            return;
        }
        $diff['update_at'] = Dates::nowDb();
        self::db()->table('users')->where('id', $user->id)->update($diff);
    }
}
