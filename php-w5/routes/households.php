<?php

/*
 * Area 3 — households, media, shared, utils. Paths without /api (added by bootstrap/app.php).
 * Order follows mealie/routes/households/__init__.py (rules before meal plans) and each controller's
 * definition order, so static segments win over parameters as in FastAPI.
 */

use App\Areas\Households\Controllers\CookbookController;
use App\Areas\Households\Controllers\InvitationController;
use App\Areas\Households\Controllers\MealplanController;
use App\Areas\Households\Controllers\MealplanRuleController;
use App\Areas\Households\Controllers\MediaController;
use App\Areas\Households\Controllers\NotifierController;
use App\Areas\Households\Controllers\RecipeActionController;
use App\Areas\Households\Controllers\SelfServiceController;
use App\Areas\Households\Controllers\SharedController;
use App\Areas\Households\Controllers\WebhookController;
use App\Areas\Households\Support\UserAuth;
use Illuminate\Support\Facades\Route;

Route::middleware(UserAuth::class)->group(function () {
    // controller_cookbooks.py
    Route::get('/households/cookbooks', [CookbookController::class, 'index']);
    Route::post('/households/cookbooks', [CookbookController::class, 'store']);
    Route::put('/households/cookbooks', [CookbookController::class, 'updateMany']);
    Route::get('/households/cookbooks/{item_id}', [CookbookController::class, 'show']);
    Route::put('/households/cookbooks/{item_id}', [CookbookController::class, 'update']);
    Route::delete('/households/cookbooks/{item_id}', [CookbookController::class, 'destroy']);

    // controller_group_notifications.py (POST /{item_id}/test not implemented: Apprise)
    Route::get('/households/events/notifications', [NotifierController::class, 'index']);
    Route::post('/households/events/notifications', [NotifierController::class, 'store']);
    Route::get('/households/events/notifications/{item_id}', [NotifierController::class, 'show']);
    Route::put('/households/events/notifications/{item_id}', [NotifierController::class, 'update']);
    Route::delete('/households/events/notifications/{item_id}', [NotifierController::class, 'destroy']);

    // controller_group_recipe_actions.py (trigger not implemented: outbound HTTP)
    Route::get('/households/recipe-actions', [RecipeActionController::class, 'index']);
    Route::post('/households/recipe-actions', [RecipeActionController::class, 'store']);
    Route::get('/households/recipe-actions/{item_id}', [RecipeActionController::class, 'show']);
    Route::put('/households/recipe-actions/{item_id}', [RecipeActionController::class, 'update']);
    Route::delete('/households/recipe-actions/{item_id}', [RecipeActionController::class, 'destroy']);

    // controller_household_self_service.py
    Route::get('/households/self', [SelfServiceController::class, 'self']);
    Route::get('/households/self/recipes/{recipe_slug}', [SelfServiceController::class, 'recipe']);
    Route::get('/households/members', [SelfServiceController::class, 'members']);
    Route::get('/households/preferences', [SelfServiceController::class, 'preferences']);
    Route::put('/households/preferences', [SelfServiceController::class, 'updatePreferences']);
    Route::put('/households/permissions', [SelfServiceController::class, 'permissions']);
    Route::get('/households/statistics', [SelfServiceController::class, 'statistics']);

    // controller_invitations.py (POST /email not implemented: SMTP)
    Route::get('/households/invitations', [InvitationController::class, 'index']);
    Route::post('/households/invitations', [InvitationController::class, 'store']);

    // controller_webhooks.py (POST /rerun and /{item_id}/test not implemented: fire webhooks)
    Route::get('/households/webhooks', [WebhookController::class, 'index']);
    Route::post('/households/webhooks', [WebhookController::class, 'store']);
    Route::get('/households/webhooks/{item_id}', [WebhookController::class, 'show']);
    Route::put('/households/webhooks/{item_id}', [WebhookController::class, 'update']);
    Route::delete('/households/webhooks/{item_id}', [WebhookController::class, 'destroy']);

    // controller_mealplan_rules.py (registered before meal plans, as in Python)
    Route::get('/households/mealplans/rules', [MealplanRuleController::class, 'index']);
    Route::post('/households/mealplans/rules', [MealplanRuleController::class, 'store']);
    Route::get('/households/mealplans/rules/{item_id}', [MealplanRuleController::class, 'show']);
    Route::put('/households/mealplans/rules/{item_id}', [MealplanRuleController::class, 'update']);
    Route::delete('/households/mealplans/rules/{item_id}', [MealplanRuleController::class, 'destroy']);

    // controller_mealplan.py (POST /random not implemented: query filter + random order)
    Route::get('/households/mealplans', [MealplanController::class, 'index']);
    Route::post('/households/mealplans', [MealplanController::class, 'store']);
    Route::get('/households/mealplans/today', [MealplanController::class, 'today']);
    Route::get('/households/mealplans/{item_id}', [MealplanController::class, 'show']);
    Route::put('/households/mealplans/{item_id}', [MealplanController::class, 'update']);
    Route::delete('/households/mealplans/{item_id}', [MealplanController::class, 'destroy']);

    // shared/__init__.py (POST, GET/DELETE /{item_id} not implemented: full Recipe serializer)
    Route::get('/shared/recipes', [SharedController::class, 'index']);
});

// media/__init__.py, media_recipe.py, media_user.py — public
Route::get('/media/recipes/{recipe_id}/images/{file_name}', [MediaController::class, 'recipeImage']);
Route::get('/media/recipes/{recipe_id}/images/timeline/{timeline_event_id}/{file_name}', [MediaController::class, 'timelineImage']);
Route::get('/media/recipes/{recipe_id}/assets/{file_name}', [MediaController::class, 'recipeAsset']);
Route::get('/media/users/{user_id}/{file_name}', [MediaController::class, 'userImage']);
Route::get('/media/docker/validate.txt', [MediaController::class, 'dockerValidate']);

// utility_routes.py — public (file token)
Route::get('/utils/download', [MediaController::class, 'download']);
