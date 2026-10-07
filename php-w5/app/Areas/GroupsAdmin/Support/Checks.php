<?php

namespace App\Areas\GroupsAdmin\Support;

use App\Support\CurrentUser;
use App\Support\Errors;

/** mealie/routes/_base/checks.py OperationChecks */
class Checks
{
    public static function canManage(): void
    {
        if (! CurrentUser::get()->can_manage) {
            Errors::http(403);
        }
    }

    /** HttpRepo.get_one / update_one 404 body */
    public static function notFound(): never
    {
        Errors::errorResponse(404, 'Not found.');
    }

    /** HttpRepo.handle_exception for NoResultFound */
    public static function noResult(string $message = 'An unexpected error occurred'): never
    {
        Errors::errorResponse(404, $message, 'No row was found when one was required');
    }
}
