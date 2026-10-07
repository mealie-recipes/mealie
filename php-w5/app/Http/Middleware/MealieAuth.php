<?php

namespace App\Http\Middleware;

use App\Auth\Jwt;
use App\Support\Errors;
use App\Support\Guid;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * mealie/core/dependencies/dependencies.py get_current_user / try_get_current_user / get_admin_user.
 *   mealie.user      -> 401 unless a valid user token
 *   mealie.admin     -> as above, then 403 unless users.admin
 *   mealie.optional  -> sets the user when the token is valid, never fails
 */
class MealieAuth
{
    public function handle(Request $request, Closure $next, string $mode = 'user')
    {
        $user = self::resolve($request);

        if ($user === null && $mode !== 'optional') {
            Errors::unauthorized();
        }
        if ($mode === 'admin' && ! $user->admin) {
            Errors::http(403, 'Forbidden');
        }

        $request->attributes->set('mealie_user', $user);

        return $next($request);
    }

    public static function token(Request $request): string
    {
        $token = $request->bearerToken();
        if ($token === null || $token === '') {
            $token = (string) $request->cookies->get('mealie.access_token', '');
        }

        return $token;
    }

    public static function resolve(Request $request): ?object
    {
        $token = self::token($request);
        if ($token === '') {
            return null;
        }
        $claims = Jwt::decode($token, Jwt::secret());
        if ($claims === null) {
            return null;
        }

        $db = DB::connection('mealie');

        if (array_key_exists('long_token', $claims)) {
            $userId = Guid::toDb((string) ($claims['id'] ?? ''));
            $row = $db->table('long_live_tokens')->where('token', $token)->where('user_id', $userId)->first();

            return $row ? $db->table('users')->where('id', $row->user_id)->first() : null;
        }

        $userId = Guid::toDb((string) ($claims['sub'] ?? ''));
        if ($userId === null) {
            return null;
        }
        $user = $db->table('users')->where('id', $userId)->first();
        if ($user === null) {
            return null;
        }

        if ($user->tokens_valid_after !== null) {
            $iat = $claims['iat'] ?? null;
            $after = strtotime($user->tokens_valid_after.' UTC');
            if (! is_numeric($iat) || $iat < $after) {
                return null;
            }
        }

        return $user;
    }
}
