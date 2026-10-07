<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Http;
use App\Areas\Households\Support\Input;
use App\Areas\Households\Support\Out;
use App\Areas\Households\Support\Paginator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/households/controller_group_recipe_actions.py (CRUD only) */
class RecipeActionController
{
    private function query()
    {
        return Out::db()->table('recipe_actions')
            ->where('group_id', CurrentUser::groupId())->where('household_id', CurrentUser::householdId());
    }

    /** CreateGroupRecipeAction */
    private function parse(array $data): array
    {
        $type = Input::enum($data, 'action_type', ['link', 'post']);
        $title = Input::str($data, 'title');
        $url = Input::str($data, 'url');
        $lower = strtolower(trim($url));
        if (! (str_starts_with($lower, 'http://') || str_starts_with($lower, 'https://'))) {
            Errors::validation('Value error, URL must use http or https scheme at body.url');
        }

        return ['action_type' => $type, 'title' => $title, 'url' => $url];
    }

    public function index(Request $request)
    {
        return Json::respond(Paginator::page(
            $request, $this->query(), fn ($r) => Out::recipeAction($r), 'recipe_actions',
            ['id', 'group_id', 'household_id', 'action_type', 'title', 'created_at', 'update_at'],
            ['action_type', 'title'], '/households/recipe-actions', null, 'GroupRecipeAction', ['url'],
        ));
    }

    public function store(Request $request)
    {
        $values = $this->parse(Input::object($request));
        $id = Guid::new();
        $now = Dates::nowDb();
        Out::db()->table('recipe_actions')->insert($values + [
            'id' => $id,
            'group_id' => CurrentUser::groupId(),
            'household_id' => CurrentUser::householdId(),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return Json::respond(Out::recipeAction(Out::db()->table('recipe_actions')->where('id', $id)->first()), 201);
    }

    public function show(string $itemId)
    {
        $row = $this->query()->where('id', Guid::requireUuid4($itemId))->first();
        if (! $row) {
            Http::notFound();
        }

        return Json::respond(Out::recipeAction($row));
    }

    /** body: SaveGroupRecipeAction (group_id / household_id are written as given) */
    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $data = Input::object($request);
        $values = $this->parse($data);
        $values['group_id'] = Input::uuid($data, 'group_id');
        $values['household_id'] = Input::uuid($data, 'household_id');

        if (! $this->query()->where('id', $id)->exists()) {
            Http::notFound();
        }
        Out::db()->table('recipe_actions')->where('id', $id)->update($values + ['update_at' => Dates::nowDb()]);

        return Json::respond(Out::recipeAction(Out::db()->table('recipe_actions')->where('id', $id)->first()));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $row = $this->query()->where('id', $id)->first();
        if (! $row) {
            Http::deleteNotFound('An unexpected error occurred.');
        }
        Out::db()->table('recipe_actions')->where('id', $id)->delete();

        return Json::respond(Out::recipeAction($row));
    }
}
