<?php

namespace App\Http\Controllers\Concerns;

use Illuminate\Http\Request;

trait ResolvesMealieUser
{
    protected function mealieUser(Request $request): object
    {
        /** @var object $user */
        $user = $request->attributes->get('mealieUser');

        return $user;
    }
}
