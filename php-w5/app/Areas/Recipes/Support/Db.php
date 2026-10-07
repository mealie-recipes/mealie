<?php

namespace App\Areas\Recipes\Support;

use Illuminate\Database\Connection;
use Illuminate\Support\Facades\DB as Facade;

class Db
{
    public static function conn(): Connection
    {
        return Facade::connection('mealie');
    }

    public static function table(string $table): \Illuminate\Database\Query\Builder
    {
        return self::conn()->table($table);
    }

    /** FastAPI/Starlette's body for an unhandled exception. */
    public static function serverError(): never
    {
        throw new \Illuminate\Http\Exceptions\HttpResponseException(
            response('Internal Server Error', 500, ['Content-Type' => 'text/plain; charset=utf-8'])
        );
    }
}
