<?php

namespace App\Areas\GroupsAdmin\Support;

use App\Http\Middleware\MealieAuth;
use Closure;
use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Http\Request;

/**
 * Wraps the shared MealieAuth middleware. Its 401/403 are thrown as HttpResponseException outside
 * Route::run, where bootstrap/app.php's catch-all Throwable renderer turns them into 500s; here the
 * prepared response is returned instead.
 */
class Auth
{
    public function handle(Request $request, Closure $next, string $mode = 'user')
    {
        try {
            return (new MealieAuth)->handle($request, $next, $mode);
        } catch (HttpResponseException $e) {
            return $e->getResponse();
        }
    }
}
