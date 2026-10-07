<?php

namespace App\Support;

use Illuminate\Http\Exceptions\HttpResponseException;

/**
 * Error bodies as FastAPI produces them for this app.
 * - HTTPException:       {"detail": <string|object>}
 * - Validation (dev):    {"status_code": 422, "message": <string>, "data": null}  (mealie/routes/handlers.py)
 * - HttpRepo errors:     detail = {"message", "error": true, "exception"}         (mealie/schema/response/responses.py)
 */
class Errors
{
    public static function http(int $status, mixed $detail = null, array $headers = []): never
    {
        $detail ??= match ($status) {
            400 => 'Bad Request',
            401 => 'Unauthorized',
            403 => 'Forbidden',
            404 => 'Not Found',
            405 => 'Method Not Allowed',
            409 => 'Conflict',
            default => 'Error',
        };

        throw new HttpResponseException(response()->json(['detail' => $detail], $status, $headers));
    }

    public static function validation(string $message): never
    {
        throw new HttpResponseException(response()->json([
            'status_code' => 422,
            'message' => $message,
            'data' => null,
        ], 422));
    }

    /** ErrorResponse.respond(message, exception) wrapped in detail. */
    public static function errorResponse(int $status, string $message, ?string $exception = null): never
    {
        self::http($status, ['message' => $message, 'error' => true, 'exception' => $exception]);
    }

    public static function unauthorized(): never
    {
        self::http(401, 'Could not validate credentials', ['WWW-Authenticate' => 'Bearer']);
    }
}
