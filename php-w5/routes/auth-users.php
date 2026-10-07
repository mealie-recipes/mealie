<?php

/*
 * Area 1 — auth, users, app, validators. Paths are relative to /api.
 * Order follows mealie/routes/__init__.py and mealie/routes/users/__init__.py;
 * static segments are registered before parameterised ones, as FastAPI matches them.
 */

use App\Areas\AuthUsers\Http\AppController;
use App\Areas\AuthUsers\Http\AuthController;
use App\Areas\AuthUsers\Http\RatingsController;
use App\Areas\AuthUsers\Http\RegistrationController;
use App\Areas\AuthUsers\Http\RequireUser;
use App\Areas\AuthUsers\Http\UserController;
use App\Areas\AuthUsers\Http\ValidatorsController;
use Illuminate\Support\Facades\Route;

// app (mealie/routes/app/app_about.py)
Route::get('app/about', [AppController::class, 'about']);
Route::get('app/about/startup-info', [AppController::class, 'startupInfo']);
Route::get('app/about/theme', [AppController::class, 'theme']);

// auth (mealie/routes/auth/auth.py)
Route::post('auth/token', [AuthController::class, 'token']);
Route::middleware(RequireUser::class)->group(function () {
    Route::post('auth/refresh', [AuthController::class, 'refresh']);
    Route::post('auth/logout', [AuthController::class, 'logout']);
});

// users: registration.py
Route::post('users/register', [RegistrationController::class, 'register']);

// users: crud.py
Route::middleware(RequireUser::class)->group(function () {
    Route::get('users/self', [UserController::class, 'self']);
    Route::get('users/self/ratings', [UserController::class, 'selfRatings']);
    Route::get('users/self/ratings/{recipe_id}', [UserController::class, 'selfRating']);
    Route::get('users/self/favorites', [UserController::class, 'selfFavorites']);
    Route::put('users/password', [UserController::class, 'updatePassword']);
    Route::put('users/{item_id}', [UserController::class, 'updateUser']);
});

// users: forgot_password.py (reset only; forgot-password sends email)
Route::post('users/reset-password', [UserController::class, 'resetPassword']);

// users: api_tokens.py, ratings.py
Route::middleware(RequireUser::class)->group(function () {
    Route::post('users/api-tokens', [UserController::class, 'createApiToken']);
    Route::delete('users/api-tokens/{token_id}', [UserController::class, 'deleteApiToken']);

    Route::get('users/{id}/ratings', [RatingsController::class, 'ratings']);
    Route::get('users/{id}/favorites', [RatingsController::class, 'favorites']);
    Route::post('users/{id}/ratings/{slug}', [RatingsController::class, 'setRating']);
    Route::post('users/{id}/favorites/{slug}', [RatingsController::class, 'addFavorite']);
    Route::delete('users/{id}/favorites/{slug}', [RatingsController::class, 'removeFavorite']);
});

// validators (mealie/routes/validators/validators.py)
Route::get('validators/user/name', [ValidatorsController::class, 'userName']);
Route::get('validators/user/email', [ValidatorsController::class, 'userEmail']);
Route::get('validators/group', [ValidatorsController::class, 'group']);
Route::get('validators/household', [ValidatorsController::class, 'household']);
Route::get('validators/recipe', [ValidatorsController::class, 'recipe']);
