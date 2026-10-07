<?php

/*
 * Area 4 — groups, admin, explore. Paths are written without /api (bootstrap/app.php adds it).
 * Static segments are registered before parameterised ones, as in the Python routers.
 * Contract: compx574/workflow-5-contracts/area-4.md
 */

use App\Areas\GroupsAdmin\Controllers\AdminAboutController;
use App\Areas\GroupsAdmin\Controllers\AdminFilesController;
use App\Areas\GroupsAdmin\Controllers\AdminGroupsController;
use App\Areas\GroupsAdmin\Controllers\AdminHouseholdsController;
use App\Areas\GroupsAdmin\Controllers\AdminUsersController;
use App\Areas\GroupsAdmin\Controllers\AiProvidersController;
use App\Areas\GroupsAdmin\Controllers\ExploreController;
use App\Areas\GroupsAdmin\Controllers\GroupSelfController;
use App\Areas\GroupsAdmin\Controllers\LabelsController;
use App\Areas\GroupsAdmin\Controllers\ReportsController;
use App\Areas\GroupsAdmin\Support\Auth;
use Illuminate\Support\Facades\Route;

// ---------------------------------------------------------------- groups (get_current_user)
Route::middleware(Auth::class.':user')->prefix('groups')->group(function () {
    Route::get('ai-providers/settings', [AiProvidersController::class, 'settings']);
    Route::put('ai-providers/settings', [AiProvidersController::class, 'updateSettings']);
    Route::post('ai-providers/providers', [AiProvidersController::class, 'groupCreate']);
    Route::get('ai-providers/providers/{providerId}', [AiProvidersController::class, 'groupShow']);
    Route::put('ai-providers/providers/{providerId}', [AiProvidersController::class, 'groupUpdate']);
    Route::delete('ai-providers/providers/{providerId}', [AiProvidersController::class, 'groupDestroy']);

    Route::get('households', [GroupSelfController::class, 'households']);
    Route::get('households/{householdSlug}', [GroupSelfController::class, 'household']);

    Route::get('self', [GroupSelfController::class, 'self']);
    Route::get('members', [GroupSelfController::class, 'members']);
    Route::get('members/{usernameOrId}', [GroupSelfController::class, 'member']);
    Route::get('preferences', [GroupSelfController::class, 'preferences']);
    Route::put('preferences', [GroupSelfController::class, 'updatePreferences']);
    Route::get('storage', [GroupSelfController::class, 'storage']);

    Route::get('reports', [ReportsController::class, 'index']);
    Route::get('reports/{itemId}', [ReportsController::class, 'show']);
    Route::delete('reports/{itemId}', [ReportsController::class, 'destroy']);

    Route::get('labels', [LabelsController::class, 'index']);
    Route::post('labels', [LabelsController::class, 'store']);
    Route::get('labels/{itemId}', [LabelsController::class, 'show']);
    Route::put('labels/{itemId}', [LabelsController::class, 'update']);
    Route::delete('labels/{itemId}', [LabelsController::class, 'destroy']);
});

// ---------------------------------------------------------------- admin (get_admin_user)
Route::middleware(Auth::class.':admin')->prefix('admin')->group(function () {
    Route::get('about/statistics', [AdminAboutController::class, 'statistics']);
    Route::get('about/check', [AdminAboutController::class, 'check']);

    Route::get('users', [AdminUsersController::class, 'index']);
    Route::post('users', [AdminUsersController::class, 'store']);
    Route::post('users/unlock', [AdminUsersController::class, 'unlock']);
    Route::post('users/password-reset-token', [AdminUsersController::class, 'resetToken']);
    Route::get('users/{itemId}', [AdminUsersController::class, 'show']);
    Route::put('users/{itemId}', [AdminUsersController::class, 'update']);
    Route::delete('users/{itemId}', [AdminUsersController::class, 'destroy']);

    Route::get('households', [AdminHouseholdsController::class, 'index']);
    Route::post('households', [AdminHouseholdsController::class, 'store']);
    Route::get('households/{itemId}', [AdminHouseholdsController::class, 'show']);
    Route::put('households/{itemId}', [AdminHouseholdsController::class, 'update']);
    Route::delete('households/{itemId}', [AdminHouseholdsController::class, 'destroy']);

    Route::get('groups', [AdminGroupsController::class, 'index']);
    Route::post('groups', [AdminGroupsController::class, 'store']);
    Route::get('groups/{itemId}', [AdminGroupsController::class, 'show']);
    Route::put('groups/{itemId}', [AdminGroupsController::class, 'update']);
    Route::delete('groups/{itemId}', [AdminGroupsController::class, 'destroy']);

    Route::post('groups/{groupId}/ai-providers/providers', [AiProvidersController::class, 'adminCreate']);
    Route::get('groups/{groupId}/ai-providers/providers/{providerId}', [AiProvidersController::class, 'adminShow']);
    Route::put('groups/{groupId}/ai-providers/providers/{providerId}', [AiProvidersController::class, 'adminUpdate']);
    Route::delete('groups/{groupId}/ai-providers/providers/{providerId}', [AiProvidersController::class, 'adminDestroy']);

    Route::get('email', [AdminAboutController::class, 'email']);

    Route::get('backups', [AdminFilesController::class, 'backups']);
    Route::get('backups/{fileName}', [AdminFilesController::class, 'backupToken']);
    Route::delete('backups/{fileName}', [AdminFilesController::class, 'deleteBackup']);

    Route::get('maintenance', [AdminFilesController::class, 'summary']);
    Route::get('maintenance/storage', [AdminFilesController::class, 'storage']);
    Route::post('maintenance/clean/images', [AdminFilesController::class, 'cleanImagesRoute']);
    Route::post('maintenance/clean/temp', [AdminFilesController::class, 'cleanTemp']);
    Route::post('maintenance/clean/recipe-folders', [AdminFilesController::class, 'cleanRecipeFoldersRoute']);
});

// ---------------------------------------------------------------- explore (public, get_public_group)
Route::prefix('explore/groups/{groupSlug}')->group(function () {
    Route::get('foods', [ExploreController::class, 'foods']);
    Route::get('foods/{itemId}', [ExploreController::class, 'food']);
    Route::get('households', [ExploreController::class, 'households']);
    Route::get('households/{householdSlug}', [ExploreController::class, 'household']);
    Route::get('organizers/categories', [ExploreController::class, 'categories']);
    Route::get('organizers/categories/{itemId}', [ExploreController::class, 'category']);
    Route::get('organizers/tags', [ExploreController::class, 'tags']);
    Route::get('organizers/tags/{itemId}', [ExploreController::class, 'tag']);
    Route::get('organizers/tools', [ExploreController::class, 'tools']);
    Route::get('organizers/tools/{itemId}', [ExploreController::class, 'tool']);
});
