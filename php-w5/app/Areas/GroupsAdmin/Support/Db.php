<?php

namespace App\Areas\GroupsAdmin\Support;

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

    public static function bool(mixed $value): bool
    {
        return (bool) $value;
    }

    /** Nullable boolean column as Pydantic `bool | None` would return it. */
    public static function nbool(mixed $value): ?bool
    {
        return $value === null ? null : (bool) $value;
    }
}
