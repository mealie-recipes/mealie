<?php

namespace App\Areas\AuthUsers\Http;

use App\Http\Middleware\MealieAuth;
use Closure;
use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Http\Request;

/**
 * Wraps the shared `mealie:user` middleware. The shared MealieAuth throws HttpResponseException, which
 * bootstrap/app.php's catch-all Throwable renderer turns into a 500 when thrown from middleware
 * (only Route::run unwraps it). Returning the response here keeps the 401 Python sends.
 */
class RequireUser
{
    public function handle(Request $request, Closure $next)
    {
        try {
            return app(MealieAuth::class)->handle($request, $next, 'user');
        } catch (HttpResponseException $e) {
            return $e->getResponse();
        }
    }
}
