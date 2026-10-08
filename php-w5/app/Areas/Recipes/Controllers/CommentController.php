<?php

namespace App\Areas\Recipes\Controllers;

use App\Areas\Recipes\Support\Db;
use App\Areas\Recipes\Support\Input;
use App\Areas\Recipes\Support\Map;
use App\Support\CurrentUser;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Pagination;
use Illuminate\Http\Request;

/**
 * mealie/routes/comments/__init__.py and mealie/routes/recipe/comments.py
 */
class CommentController extends Base
{
    private function find(string $id): ?object
    {
        return Map::commentQuery($this->groupId())->where('recipe_comments.id', $id)->first();
    }

    public function index(Request $request)
    {
        $query = Map::commentQuery($this->groupId());
        $result = Pagination::page($request, $query, fn ($rows) => array_map([Map::class, 'comment'], $rows), '/comments', [
            'table' => 'recipe_comments',
            'columns' => ['created_at' => false, 'update_at' => false, 'id' => false, 'text' => true, 'recipe_id' => false, 'user_id' => false],
            'search' => null,
        ]);

        return $this->json($result);
    }

    /** validate_comment_text (mealie/schema/recipe/recipe_comments.py:22) */
    private function text(Input $in): ?string
    {
        $text = $in->str('text');
        if ($text !== null && trim($text) === '') {
            $in->error('text', 'value_error', 'Value error, comment text must not be empty');
        }

        return $text === null ? null : trim($text);
    }

    public function store(Request $request)
    {
        $in = Input::fromRequest($request);
        $recipeId = $in->uuid4('recipe_id');
        $text = $this->text($in);
        $in->check();

        $id = Guid::new();
        $this->write(function () use ($id, $recipeId, $text) {
            Db::table('recipe_comments')->insert([
                'created_at' => $this->now(), 'update_at' => $this->now(), 'id' => $id,
                'text' => $text, 'recipe_id' => $recipeId, 'user_id' => CurrentUser::id(),
            ]);
        }, self::SERVER_ERROR_MSG, 'Database integrity error');

        // repo.create validates the new row without the group filter
        return $this->json(Map::comment(Map::commentQuery(null)->where('recipe_comments.id', $id)->first()), 201);
    }

    public function show(string $item_id)
    {
        $id = Input::pathUuid4($item_id);

        return $this->json(Map::comment($this->find($id) ?? Errors::notFound()));
    }

    /** _check_comment_belongs_to_user (comments/__init__.py:35); a missing comment raises AttributeError -> 500 */
    private function checkOwner(string $id): void
    {
        $row = $this->find($id);
        if (! $row) {
            Db::serverError();
        }
        $user = CurrentUser::get();
        if ($row->user_id !== $user->id && ! $user->admin) {
            // Python raises HTTPException(detail=ErrorResponse(...)): the model is not JSON-serialisable, so the client gets a 500
            Db::serverError();
        }
    }

    public function update(Request $request, string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $in = Input::fromRequest($request);
        $in->uuid4('id');
        $text = $this->text($in);
        $in->check();
        $this->checkOwner($id);

        Db::table('recipe_comments')->where('id', $id)->update(['text' => $text, 'update_at' => $this->now()]);

        return $this->json(Map::comment($this->find($id)));
    }

    public function destroy(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $this->checkOwner($id);
        Db::table('recipe_comments')->where('id', $id)->delete();

        return $this->json(['message' => 'Comment deleted', 'error' => false]);
    }

    /** GET /api/recipes/{slug}/comments: household-scoped recipe lookup by slug; missing -> 500 */
    public function forRecipe(string $slug)
    {
        $recipe = Db::table('recipes')
            ->join('users as ru', 'ru.id', '=', 'recipes.user_id')
            ->where('recipes.group_id', $this->groupId())
            ->where('ru.household_id', CurrentUser::householdId())
            ->where('recipes.slug', $slug)
            ->first(['recipes.id']);
        if (! $recipe) {
            Db::serverError();
        }
        $rows = Map::commentQuery($this->groupId())->where('recipe_comments.recipe_id', $recipe->id)->orderBy('recipe_comments.rowid')->get();

        return $this->json($rows->map(fn ($r) => Map::comment($r))->all());
    }
}
