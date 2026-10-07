<?php

namespace App\Areas\Recipes\Support;

use App\Http\Middleware\MealieAuth;
use Closure;
use Illuminate\Http\Request;

/**
 * Same as the shared `mealie:user` middleware, but returns the 401 instead of throwing it:
 * bootstrap/app.php's catch-all Throwable renderer turns a thrown HttpResponseException into a 500.
 */
class Auth
{
    public function handle(Request $request, Closure $next)
    {
        $user = MealieAuth::resolve($request);
        if ($user === null) {
            return response()->json(['detail' => 'Could not validate credentials'], 401, ['WWW-Authenticate' => 'Bearer']);
        }
        $request->attributes->set('mealie_user', $user);

        return $next($request);
    }
}
