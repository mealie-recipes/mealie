<?php

namespace App\Areas\AuthUsers\Http;

use App\Areas\AuthUsers\Support\Pyd;
use App\Areas\AuthUsers\Support\Users;
use App\Areas\AuthUsers\Support\Uuid;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** mealie/routes/users/ratings.py and the users_to_recipes helpers used by crud.py */
class RatingsController
{
    /** UserRatingSummary */
    public static function summary(object $row): array
    {
        return [
            'recipeId' => Guid::fromDb($row->recipe_id),
            'rating' => $row->rating === null ? null : (float) $row->rating,
            'isFavorite' => (bool) $row->is_favorite,
        ];
    }

    /** UserRatingOut */
    public static function full(object $row): array
    {
        return self::summary($row) + [
            'userId' => Guid::fromDb($row->user_id),
            'id' => Guid::fromDb($row->id),
        ];
    }

    /** RepositoryUserRatings.get_by_user (repository_users.py:82), table order. */
    public static function rows(string $userId, bool $favoritesOnly)
    {
        $q = Users::db()->table('users_to_recipes')->where('user_id', $userId);
        if ($favoritesOnly) {
            $q->where('is_favorite', 1);
        }

        return $q->get();
    }

    public static function summaries(string $userId, bool $favoritesOnly): array
    {
        return self::rows($userId, $favoritesOnly)->map(fn ($r) => self::summary($r))->all();
    }

    /** GET /users/{id}/ratings (ratings.py:44) */
    public function ratings(string $id): JsonResponse
    {
        return $this->list($id, false, 44, 'get_ratings', '/api/users/{id}/ratings');
    }

    /** GET /users/{id}/favorites (ratings.py:50) */
    public function favorites(string $id): JsonResponse
    {
        return $this->list($id, true, 50, 'get_favorites', '/api/users/{id}/favorites');
    }

    private function list(string $id, bool $favorites, int $line, string $func, string $path): JsonResponse
    {
        $v = new Pyd('users/ratings.py', $line, $func, 'GET', $path);
        $userId = $v->uuid('path', 'id', $id);
        $v->done();

        UserController::assertChangeAllowed($userId, CurrentUser::get());

        return Json::respond(['ratings' => self::rows($userId, $favorites)->map(fn ($r) => self::full($r))->all()]);
    }

    /** POST /users/{id}/ratings/{slug} (ratings.py:56) */
    public function setRating(Request $request, string $id, string $slug): JsonResponse
    {
        $v = new Pyd('users/ratings.py', 56, 'set_rating', 'POST', '/api/users/{id}/ratings/{slug}');
        $userId = $v->uuid('path', 'id', $id);
        $data = $v->fields($v->bodyObject($request), [
            ['name' => 'rating', 'type' => 'float', 'nullable' => true],
            ['name' => 'is_favorite', 'alias' => 'isFavorite', 'type' => 'bool', 'nullable' => true],
        ]);
        $v->done();

        $this->apply($userId, $slug, $data['rating'], $data['is_favorite']);

        return JsonResponse::fromJsonString('null');
    }

    /** POST /users/{id}/favorites/{slug} (ratings.py:80) */
    public function addFavorite(string $id, string $slug): JsonResponse
    {
        return $this->favorite($id, $slug, true, 80, 'add_favorite', 'POST');
    }

    /** DELETE /users/{id}/favorites/{slug} (ratings.py:85) */
    public function removeFavorite(string $id, string $slug): JsonResponse
    {
        return $this->favorite($id, $slug, false, 85, 'remove_favorite', 'DELETE');
    }

    private function favorite(string $id, string $slug, bool $value, int $line, string $func, string $method): JsonResponse
    {
        $v = new Pyd('users/ratings.py', $line, $func, $method, '/api/users/{id}/favorites/{slug}');
        $userId = $v->uuid('path', 'id', $id);
        $v->done();

        $this->apply($userId, $slug, null, $value);

        return JsonResponse::fromJsonString('null');
    }

    /** UserRatingsController.set_rating body after validation. */
    private function apply(string $userId, string $slug, ?float $rating, ?bool $isFavorite): void
    {
        $user = CurrentUser::get();
        UserController::assertChangeAllowed($userId, $user);

        // get_recipe_or_404: group-scoped recipes, by id when the slug parses as a UUID
        $db = Users::db();
        $q = $db->table('recipes')->where('group_id', $user->group_id);
        $asId = Uuid::python($slug);
        $recipe = ($asId !== null ? $q->where('id', $asId) : $q->where('slug', $slug))->first();
        if ($recipe === null) {
            Errors::errorResponse(404, 'Not found.');
        }

        $db->transaction(function () use ($db, $userId, $recipe, $rating, $isFavorite) {
            $now = Dates::nowDb();
            $existing = $db->table('users_to_recipes')->where('user_id', $userId)->where('recipe_id', $recipe->id)->first();
            if ($existing === null) {
                $db->table('users_to_recipes')->insert([
                    'user_id' => $userId,
                    'recipe_id' => $recipe->id,
                    'rating' => $rating,
                    'is_favorite' => $isFavorite ? 1 : 0,
                    'id' => Guid::new(),
                    'created_at' => $now,
                    'update_at' => $now,
                ]);
            } else {
                $changes = [];
                if ($rating !== null && ($existing->rating === null || (float) $existing->rating !== $rating)) {
                    $changes['rating'] = $rating;
                }
                if ($isFavorite !== null && (bool) $existing->is_favorite !== $isFavorite) {
                    $changes['is_favorite'] = $isFavorite ? 1 : 0;
                }
                if ($changes !== []) {
                    $changes['update_at'] = $now;
                    $db->table('users_to_recipes')->where('id', $existing->id)->update($changes);
                }
            }

            // update_recipe_rating (user_to_recipe.py:36) -> calculate_rating (recipe.py:288)
            $avg = $db->table('users_to_recipes')
                ->where('recipe_id', $recipe->id)->whereNotNull('rating')->where('rating', '>', 0)
                ->avg('rating');
            $avg = $avg === null ? null : (float) $avg;
            $current = $recipe->rating === null ? null : (float) $recipe->rating;
            if ($avg !== $current) {
                $db->table('recipes')->where('id', $recipe->id)->update(['rating' => $avg, 'update_at' => $now]);
            }
        });
    }
}
