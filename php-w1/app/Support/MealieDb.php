<?php

namespace App\Support;

use Illuminate\Database\Query\Builder;
use Illuminate\Support\Facades\DB;

final class MealieDb
{
    public static function table(string $table): Builder
    {
        return DB::connection('mealie')->table($table);
    }

    public static function now(): string
    {
        return now()->utc()->format('Y-m-d H:i:s');
    }
}
