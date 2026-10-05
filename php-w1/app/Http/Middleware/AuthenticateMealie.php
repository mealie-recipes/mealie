<?php

namespace App\Http\Middleware;

use App\Auth\AuthService;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

final class AuthenticateMealie
{
    public function __construct(private readonly AuthService $auth) {}

    public function handle(Request $request, Closure $next): Response
    {
        $user = $this->auth->userFromRequest($request);
        if ($user === null) {
            return response()->json(['detail' => 'Could not validate credentials'], 401);
        }

        $request->attributes->set('mealieUser', $user);

        return $next($request);
    }
}
