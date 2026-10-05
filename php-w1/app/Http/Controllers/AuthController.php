<?php

namespace App\Http\Controllers;

use App\Auth\AuthService;
use App\Auth\UserLockedOut;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use RuntimeException;

final class AuthController extends Controller
{
    public function __construct(private readonly AuthService $auth) {}

    public function oauth(): JsonResponse
    {
        return response()->json(['detail' => 'OIDC is not configured'], 404);
    }

    public function token(Request $request): JsonResponse
    {
        if (! config('mealie.allow_password_login')) {
            return response()->json(['detail' => 'Password login is disabled'], 403);
        }

        $remember = filter_var($request->input('remember_me', false), FILTER_VALIDATE_BOOL);

        try {
            $session = $this->auth->login(
                (string) $request->input('username', ''),
                (string) $request->input('password', ''),
                $remember,
            );
        } catch (UserLockedOut) {
            return response()->json(['detail' => 'User is locked out'], 423);
        } catch (RuntimeException) {
            return response()->json(['detail' => 'Mealie signing secret is not configured'], 500);
        }

        if ($session === null) {
            return response()->json(['detail' => 'Unauthorized'], 401);
        }

        return $this->tokenResponse($session);
    }

    public function refresh(Request $request): JsonResponse
    {
        try {
            $session = $this->auth->refresh($request);
        } catch (RuntimeException $e) {
            $status = $e->getMessage() === 'api-token' ? 400 : 401;

            return response()->json(['detail' => $status === 400 ? 'API tokens cannot be exchanged for a session token' : 'Unauthorized'], $status);
        }

        return $this->tokenResponse($session);
    }

    public function logout(Request $request): JsonResponse
    {
        return response()->json(['message' => 'Logged out'])->withoutCookie(AuthService::COOKIE);
    }

    /**
     * @param  array{token: string, expires_in: int, remember: bool}  $session
     */
    private function tokenResponse(array $session): JsonResponse
    {
        $response = response()->json([
            'access_token' => $session['token'],
            'token_type' => 'bearer',
            'expires_in' => $session['expires_in'],
        ]);

        return $response->cookie(
            AuthService::COOKIE,
            $session['token'],
            $session['remember'] ? (int) ($session['expires_in'] / 60) : 0,
            '/',
            null,
            $requestIsSecure = request()->isSecure(),
            false,
            false,
            $requestIsSecure ? 'none' : 'lax',
        );
    }
}
