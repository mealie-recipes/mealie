<?php

namespace App\Support;

use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class Json
{
    /** snake_case -> camelCase like humps.camelize used by MealieModel. */
    public static function camel(string $key): string
    {
        return lcfirst(str_replace(' ', '', ucwords(str_replace('_', ' ', $key))));
    }

    public static function camelKeys(array $data): array
    {
        $out = [];
        foreach ($data as $key => $value) {
            $out[is_string($key) ? self::camel($key) : $key] = is_array($value) ? self::camelKeys($value) : $value;
        }

        return $out;
    }

    /** JSON response that keeps "{}" for empty objects and does not escape slashes/unicode. */
    public static function respond(mixed $data, int $status = 200): JsonResponse
    {
        return response()->json($data, $status, [], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRESERVE_ZERO_FRACTION);
    }

    /**
     * Request body as FastAPI would parse it for a Pydantic model parameter:
     * must be a JSON object, otherwise 422.
     */
    public static function body(Request $request): array
    {
        $raw = $request->getContent();
        $decoded = json_decode($raw === '' ? 'null' : $raw, true);
        if (! is_array($decoded) || array_is_list($decoded) && $decoded !== []) {
            Errors::validation('Input should be a valid dictionary or object to extract fields from at body');
        }

        return $decoded;
    }
}
