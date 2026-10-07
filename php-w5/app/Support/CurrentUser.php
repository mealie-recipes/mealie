<?php

namespace App\Support;

/**
 * The authenticated users row (stdClass, raw SQLite values: ids are 32-char hex).
 * Set by App\Http\Middleware\MealieAuth. Mirrors BaseUserController.user / group_id / household_id.
 */
class CurrentUser
{
    public static function get(): object
    {
        $user = request()->attributes->get('mealie_user');
        if ($user === null) {
            Errors::unauthorized();
        }

        return $user;
    }

    public static function optional(): ?object
    {
        return request()->attributes->get('mealie_user');
    }

    public static function id(): string
    {
        return self::get()->id;
    }

    public static function groupId(): string
    {
        return self::get()->group_id;
    }

    public static function householdId(): ?string
    {
        return self::get()->household_id;
    }

    public static function isAdmin(): bool
    {
        return (bool) self::get()->admin;
    }
}
