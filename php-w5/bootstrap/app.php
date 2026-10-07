<?php

use App\Http\Middleware\MealieAuth;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Http\Request;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;
use Symfony\Component\HttpKernel\Exception\MethodNotAllowedHttpException;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        apiPrefix: 'api',
        commands: __DIR__.'/../routes/console.php',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->alias(['mealie' => MealieAuth::class]);
        // FastAPI does not redirect /api/foo/ to /api/foo; keep trailing slashes as-is.
        $middleware->remove(\Illuminate\Foundation\Http\Middleware\TrimStrings::class);
        $middleware->remove(\Illuminate\Foundation\Http\Middleware\ConvertEmptyStringsToNull::class);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        // Render callbacks run before Laravel's own HttpResponseException handling, so the
        // catch-all below would turn every Errors::* response thrown from middleware into a 500.
        $exceptions->render(fn (HttpResponseException $e) => $e->getResponse());
        // Match FastAPI/Starlette's default bodies for routing errors.
        $exceptions->render(function (NotFoundHttpException $e, Request $request) {
            $message = $e->getMessage();

            return response()->json(['detail' => $message !== '' && ! str_starts_with($message, 'The route ') ? $message : 'Not Found'], 404);
        });
        $exceptions->render(function (MethodNotAllowedHttpException $e, Request $request) {
            return response()->json(['detail' => 'Method Not Allowed'], 405);
        });
        $exceptions->render(function (HttpExceptionInterface $e, Request $request) {
            return response()->json(['detail' => $e->getMessage() ?: 'Error'], $e->getStatusCode(), $e->getHeaders());
        });
        $exceptions->render(function (Throwable $e, Request $request) {
            report($e);

            return response()->json(['detail' => 'Internal Server Error'], 500);
        });
    })->create();
