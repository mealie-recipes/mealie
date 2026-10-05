<?php

namespace App\Auth;

use App\Support\Guid;
use App\Support\JsonShape;
use App\Support\MealieDb;
use Illuminate\Http\Request;
use RuntimeException;

final class AuthService
{
    public const COOKIE = 'mealie.access_token';

    /**
     * @return array{token: string, expires_in: int, remember: bool}|null
     */
    public function login(string $username, string $password, bool $remember): ?array
    {
        $user = MealieDb::table('users')
            ->whereRaw('lower(username) = ?', [strtolower($username)])
            ->orWhereRaw('lower(email) = ?', [strtolower($username)])
            ->first();

        if ($user === null || ($user->auth_method ?? 'MEALIE') !== 'MEALIE') {
            password_verify('abc123cba321', '$2b$12$JdHtJOlkPFwyxdjdygEzPOtYmdQF5/R5tHxw5Tq8pxjubyLqdIX5i');

            return null;
        }

        if ($this->locked($user)) {
            throw new UserLockedOut;
        }

        if (! password_verify(substr($password, 0, 72), (string) $user->password)) {
            $attempts = ((int) $user->login_attemps) + 1;
            $update = ['login_attemps' => $attempts, 'update_at' => MealieDb::now()];
            if ($attempts >= (int) config('mealie.max_login_attempts')) {
                $update['locked_at'] = MealieDb::now();
            }
            MealieDb::table('users')->where('id', $user->id)->update($update);

            return null;
        }

        MealieDb::table('users')->where('id', $user->id)->update([
            'login_attemps' => 0,
            'update_at' => MealieDb::now(),
        ]);

        return $this->issue((string) $user->id, $remember);
    }

    /**
     * @return array{token: string, expires_in: int, remember: bool}
     */
    public function refresh(Request $request): array
    {
        $token = $this->bearer($request);
        $claims = $token === null ? null : $this->claims($token);
        if ($claims === null || isset($claims['long_token'])) {
            throw new RuntimeException($claims === null ? 'invalid' : 'api-token');
        }

        return $this->issue((string) $claims['sub'], JsonShape::bool($claims['rme'] ?? false));
    }

    /**
     * @return object|null database user row
     */
    public function userFromRequest(Request $request): ?object
    {
        $token = $this->bearer($request);
        if ($token === null || $token === '') {
            return null;
        }

        try {
            $claims = $this->claims($token);
        } catch (RuntimeException) {
            return null;
        }

        if ($claims === null || ! isset($claims['sub'])) {
            return null;
        }

        $user = MealieDb::table('users')->where('id', Guid::hex((string) $claims['sub']))->first();
        if ($user === null) {
            return null;
        }

        if ($user->tokens_valid_after !== null) {
            $issued = $claims['iat'] ?? null;
            if ($issued === null || (int) $issued < strtotime((string) $user->tokens_valid_after)) {
                return null;
            }
        }

        return $user;
    }

    public function bearer(Request $request): ?string
    {
        $header = $request->bearerToken();
        if (is_string($header) && $header !== '') {
            return $header;
        }

        $cookie = $request->cookie(self::COOKIE);

        return is_string($cookie) && $cookie !== '' ? $cookie : null;
    }

    /**
     * @return array{token: string, expires_in: int, remember: bool}
     */
    private function issue(string $userId, bool $remember): array
    {
        $hours = (int) config('mealie.token_hours');
        $now = time();
        $expires = $now + ($hours * 3600);
        $token = Jwt::encode([
            'sub' => Guid::dashed($userId),
            'rme' => $remember,
            'iss' => 'mealie',
            'iat' => $now,
            'exp' => $expires,
        ], Jwt::secret());

        return ['token' => $token, 'expires_in' => $hours * 3600, 'remember' => $remember];
    }

    /**
     * @return array<string, mixed>|null
     */
    private function claims(string $token): ?array
    {
        return Jwt::decode($token, Jwt::secret());
    }

    private function locked(object $user): bool
    {
        if ($user->locked_at === null) {
            return ((int) $user->login_attemps) >= (int) config('mealie.max_login_attempts');
        }

        $expires = strtotime((string) $user->locked_at) + ((int) config('mealie.lockout_hours') * 3600);

        return $expires > time() || ((int) $user->login_attemps) >= (int) config('mealie.max_login_attempts');
    }
}
