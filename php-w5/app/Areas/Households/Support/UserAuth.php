<?php

namespace App\Areas\Households\Support;

use App\Http\Middleware\MealieAuth;
use Closure;
use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Http\Request;

/**
 * Wraps the shared `mealie:user` middleware. Its 401 is thrown as HttpResponseException outside
 * Route::run, where bootstrap/app.php's catch-all Throwable renderer turns it into a 500;
 * returning the exception's response here keeps the 401 body.
 */
class UserAuth
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
