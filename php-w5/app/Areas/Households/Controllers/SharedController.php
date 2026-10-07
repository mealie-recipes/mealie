<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Out;
use App\Support\CurrentUser;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/shared/__init__.py — GET only (other routes return the full Recipe) */
class SharedController
{
    /** GET /shared/recipes?recipe_id= (group-scoped repo) */
    public function index(Request $request)
    {
        $recipeId = $request->query('recipe_id');
        $query = Out::db()->table('recipe_share_tokens')->where('group_id', CurrentUser::groupId());

        if ($recipeId !== null) {
            // multi_query: no ordering
            $query->where('recipe_id', Guid::requireUuid4((string) $recipeId, 'query'));
        } else {
            // get_all -> page_all(per_page=-1), created_at desc
            $query->orderBy('created_at', 'desc');
        }

        return Json::respond($query->get()->map(fn ($t) => Out::shareTokenSummary($t))->all());
    }
}
