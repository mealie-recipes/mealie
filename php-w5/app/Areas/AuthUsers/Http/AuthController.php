<?php

namespace App\Areas\AuthUsers\Http;

use App\Areas\AuthUsers\Support\Pyd;
use App\Areas\AuthUsers\Support\Settings;
use App\Areas\AuthUsers\Support\Translator;
use App\Areas\AuthUsers\Support\Users;
use App\Auth\Jwt;
use App\Http\Middleware\MealieAuth;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** mealie/routes/auth/auth.py */
class AuthController
{
    /** POST /auth/token — get_token (auth.py:134) with CredentialsProvider. */
    public function token(Request $request): JsonResponse
    {
        $v = new Pyd('auth/auth.py', 134, 'get_token', 'POST', '/api/auth/token');

        // CredentialsRequestForm: Form("") / Form(False). Only form-encoded bodies are read.
        $ct = strtolower((string) $request->headers->get('content-type', ''));
        $isForm = str_starts_with($ct, 'application/x-www-form-urlencoded') || str_starts_with($ct, 'multipart/form-data');
        $form = $isForm ? $request->request->all() : [];
        $username = $form['username'] ?? '';
        $password = $form['password'] ?? '';
        $rememberMe = false;
        if (array_key_exists('remember_me', $form)) {
            $b = Pyd::toBool($form['remember_me']);
            if ($b === null) {
                $v->add('bool_parsing', ['body', 'remember_me'], 'Input should be a valid boolean, unable to interpret input', $form['remember_me']);
            } else {
                $rememberMe = $b;
            }
        }
        $v->done();
        $username = is_string($username) ? $username : '';
        $password = is_string($password) ? $password : '';

        $db = Users::db();
        $user = $db->table('users')->whereRaw('lower(username) = ?', [strtolower($username)])->first()
            ?? $db->table('users')->whereRaw('lower(email) = ?', [strtolower($username)])->first();

        if ($user === null) {
            Users::fakeVerify();
            Errors::http(401, 'Unauthorized');
        }
        if ($user->auth_method !== 'MEALIE') {
            Users::fakeVerify();
            Errors::http(401, 'Unauthorized');
        }

        $attempts = (int) ($user->login_attemps ?? 0);
        $locked = false;
        if ($user->locked_at !== null) {
            $lockedAt = strtotime($user->locked_at.' UTC');
            $locked = $lockedAt + Settings::lockoutHours() * 3600 > time();
        }
        if ($attempts >= Settings::maxLoginAttempts() || $locked) {
            Errors::http(423, 'User is locked out');
        }

        if (! Users::verifyPassword($password, $user->password)) {
            $attempts++;
            Users::update($user, ['login_attemps' => $attempts]);
            if ($attempts >= Settings::maxLoginAttempts()) {
                $user = $db->table('users')->where('id', $user->id)->first();
                Users::update($user, ['locked_at' => Dates::nowDb()]);
            }
            Errors::http(401, 'Unauthorized');
        }

        Users::update($user, ['login_attemps' => 0]);
        [$token, $seconds] = Users::createAccessToken(['sub' => Guid::fromDb($user->id), 'rme' => $rememberMe]);

        return Users::tokenResponse($request, $token, $seconds, $rememberMe);
    }

    /** POST /auth/refresh — refresh_token (auth.py:301). */
    public function refresh(Request $request): JsonResponse
    {
        $user = CurrentUser::get();
        $payload = Jwt::decode(MealieAuth::token($request), Jwt::secret());
        if ($payload === null) {
            Errors::http(401, 'Unauthorized');
        }
        if (! empty($payload['long_token'])) {
            Errors::http(400, 'API tokens cannot be exchanged for a session token');
        }
        $rememberMe = (bool) ($payload['rme'] ?? false);
        [$token, $seconds] = Users::createAccessToken(['sub' => Guid::fromDb($user->id), 'rme' => $rememberMe]);

        return Users::tokenResponse($request, $token, $seconds, $rememberMe);
    }

    /** POST /auth/logout — logout (auth.py:332). */
    public function logout(Request $request): JsonResponse
    {
        $attrs = Users::cookieAttrs($request);
        $expires = gmdate('D, d M Y H:i:s', time()).' GMT';
        $response = response()->json(['message' => Translator::t($request, 'notifications.logged-out')]);
        $response->headers->set('set-cookie', 'mealie.access_token=""; expires='.$expires.'; Max-Age=0; Path=/; SameSite='.$attrs['samesite']
            .($attrs['secure'] ? '; Secure' : '').($attrs['partitioned'] ? '; Partitioned' : ''), false);

        return $response;
    }
}
