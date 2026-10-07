<?php

/*
 * Area 2 — recipe, organizers, unit_and_foods, comments (paths without /api; bootstrap adds it).
 * Order mirrors FastAPI's include order in mealie/routes/__init__.py and mealie/routes/recipe/__init__.py:
 * static segments are registered before the parameterised routes they would otherwise hit.
 */

use App\Areas\Recipes\Controllers\CommentController;
use App\Areas\Recipes\Controllers\FoodUnitController;
use App\Areas\Recipes\Controllers\OrganizerController;
use App\Areas\Recipes\Controllers\RecipeController;
use App\Areas\Recipes\Controllers\TimelineController;
use App\Areas\Recipes\Support\Auth;
use Illuminate\Support\Facades\Route;

// ---------------------------------------------------------------- recipe (mealie/routes/recipe)
Route::middleware(Auth::class)->group(function () {
    // exports.py
    Route::get('recipes/exports', [RecipeController::class, 'formats']);
    // recipe_crud_routes.py
    Route::get('recipes', [RecipeController::class, 'index']);
    Route::get('recipes/{slug}', [RecipeController::class, 'show']);
    // comments.py
    Route::get('recipes/{slug}/comments', [CommentController::class, 'forRecipe']);
    // bulk_actions.py
    Route::get('recipes/bulk-actions/export', [RecipeController::class, 'exports']);
});

// shared_routes.py (no auth)
Route::get('recipes/shared/{token_id}', [RecipeController::class, 'shared']);

Route::middleware(Auth::class)->group(function () {
    // timeline_events.py
    Route::get('recipes/timeline/events', [TimelineController::class, 'index']);
    Route::post('recipes/timeline/events', [TimelineController::class, 'store']);
    Route::get('recipes/timeline/events/{item_id}', [TimelineController::class, 'show']);
    Route::put('recipes/timeline/events/{item_id}', [TimelineController::class, 'update']);
    Route::delete('recipes/timeline/events/{item_id}', [TimelineController::class, 'destroy']);

    // ------------------------------------------------------------ organizers
    Route::get('organizers/categories', [OrganizerController::class, 'categoriesIndex']);
    Route::post('organizers/categories', [OrganizerController::class, 'categoriesStore']);
    Route::get('organizers/categories/empty', [OrganizerController::class, 'categoriesEmpty']);
    Route::post('organizers/categories/merge', [OrganizerController::class, 'categoriesMerge']);
    Route::get('organizers/categories/{item_id}', [OrganizerController::class, 'categoriesShow']);
    Route::put('organizers/categories/{item_id}', [OrganizerController::class, 'categoriesUpdate']);
    Route::delete('organizers/categories/{item_id}', [OrganizerController::class, 'categoriesDestroy']);
    Route::get('organizers/categories/slug/{category_slug}', [OrganizerController::class, 'categoriesBySlug']);

    Route::get('organizers/tags', [OrganizerController::class, 'tagsIndex']);
    Route::get('organizers/tags/empty', [OrganizerController::class, 'tagsEmpty']);
    Route::post('organizers/tags/merge', [OrganizerController::class, 'tagsMerge']);
    Route::get('organizers/tags/{item_id}', [OrganizerController::class, 'tagsShow']);
    Route::post('organizers/tags', [OrganizerController::class, 'tagsStore']);
    Route::put('organizers/tags/{item_id}', [OrganizerController::class, 'tagsUpdate']);
    Route::delete('organizers/tags/{item_id}', [OrganizerController::class, 'tagsDestroy']);
    Route::get('organizers/tags/slug/{tag_slug}', [OrganizerController::class, 'tagsBySlug']);

    Route::get('organizers/tools', [OrganizerController::class, 'toolsIndex']);
    Route::post('organizers/tools', [OrganizerController::class, 'toolsStore']);
    Route::get('organizers/tools/{item_id}', [OrganizerController::class, 'toolsShow']);
    Route::put('organizers/tools/{item_id}', [OrganizerController::class, 'toolsUpdate']);
    Route::delete('organizers/tools/{item_id}', [OrganizerController::class, 'toolsDestroy']);
    Route::get('organizers/tools/slug/{tool_slug}', [OrganizerController::class, 'toolsBySlug']);

    // ------------------------------------------------------------ comments
    Route::get('comments', [CommentController::class, 'index']);
    Route::post('comments', [CommentController::class, 'store']);
    Route::get('comments/{item_id}', [CommentController::class, 'show']);
    Route::put('comments/{item_id}', [CommentController::class, 'update']);
    Route::delete('comments/{item_id}', [CommentController::class, 'destroy']);

    // ------------------------------------------------------------ unit_and_foods
    Route::get('foods', [FoodUnitController::class, 'foodsIndex']);
    Route::post('foods', [FoodUnitController::class, 'foodsStore']);
    Route::put('foods/merge', [FoodUnitController::class, 'foodsMerge']);
    Route::get('foods/{item_id}', [FoodUnitController::class, 'foodsShow']);
    Route::put('foods/{item_id}', [FoodUnitController::class, 'foodsUpdate']);
    Route::delete('foods/{item_id}', [FoodUnitController::class, 'foodsDestroy']);

    Route::get('units', [FoodUnitController::class, 'unitsIndex']);
    Route::post('units', [FoodUnitController::class, 'unitsStore']);
    Route::put('units/merge', [FoodUnitController::class, 'unitsMerge']);
    Route::get('units/{item_id}', [FoodUnitController::class, 'unitsShow']);
    Route::put('units/{item_id}', [FoodUnitController::class, 'unitsUpdate']);
    Route::delete('units/{item_id}', [FoodUnitController::class, 'unitsDestroy']);
});
