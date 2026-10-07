<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Http;
use App\Areas\Households\Support\Input;
use App\Areas\Households\Support\Out;
use App\Areas\Households\Support\Paginator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/households/controller_mealplan.py (ReadPlanEntry; household = entry user's household) */
class MealplanController
{
    private const TYPES = ['breakfast', 'lunch', 'dinner', 'side', 'snack', 'drink', 'dessert'];

    private const GENERIC = 'An unexpected error occurred';

    /** RepositoryMeals: group_id column + household_id association proxy via users */
    private function query()
    {
        $householdId = CurrentUser::householdId();

        return Out::db()->table('group_meal_plans')
            ->where('group_id', CurrentUser::groupId())
            ->whereIn('user_id', fn ($q) => $q->select('id')->from('users')->where('household_id', $householdId));
    }

    /** CreatePlanEntry */
    private function parse(array $data): array
    {
        $date = Input::date($data, 'date');
        $type = Input::enum($data, 'entry_type', self::TYPES, 'breakfast');
        $title = Input::str($data, 'title', '');
        $text = Input::str($data, 'text', '');
        $recipeId = Input::uuid($data, 'recipe_id', false, null, true);
        if (! $recipeId && $title === '') {
            Errors::validation("Value error, `recipe_id=None` or `title={$title}` must be provided at body.recipe_id");
        }

        return ['date' => $date, 'entry_type' => $type, 'title' => $title, 'text' => $text, 'recipe_id' => $recipeId];
    }

    public function index(Request $request)
    {
        $start = $request->query('start_date');
        $end = $request->query('end_date');
        foreach (['start_date' => $start, 'end_date' => $end] as $name => $v) {
            if ($v !== null && Input::parseDate((string) $v) === null) {
                Errors::validation("Input should be a valid date at query.{$name}");
            }
        }

        $query = $this->query();
        if ($start) {
            $query->where('date', '>=', $start);
        }
        if ($end) {
            $query->where('date', '<=', $end);
        }

        return Json::respond(Paginator::page(
            $request, $query, fn ($r) => Out::planEntry($r), 'group_meal_plans',
            ['id', 'date', 'entry_type', 'title', 'text', 'group_id', 'user_id', 'recipe_id', 'created_at', 'update_at'],
            ['entry_type', 'title', 'text'],
        ));
    }

    public function store(Request $request)
    {
        $values = $this->parse(Input::object($request));
        $now = Dates::nowDb();
        $id = Out::db()->table('group_meal_plans')->insertGetId($values + [
            'group_id' => CurrentUser::groupId(),
            'user_id' => CurrentUser::id(),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return Json::respond(Out::planEntry(Out::db()->table('group_meal_plans')->where('id', $id)->first()), 201);
    }

    /** GET /households/mealplans/today — RepositoryMeals.get_today (household only, local date) */
    public function today()
    {
        $householdId = CurrentUser::householdId();
        $rows = Out::db()->table('group_meal_plans')
            ->where('date', date('Y-m-d'))
            ->whereIn('user_id', fn ($q) => $q->select('id')->from('users')->where('household_id', $householdId))
            ->get();

        return Json::respond($rows->map(fn ($r) => Out::planEntry($r))->all());
    }

    public function show(string $itemId)
    {
        $row = $this->query()->where('id', Input::pathInt($itemId))->first();
        if (! $row) {
            Http::notFound();
        }

        return Json::respond(Out::planEntry($row));
    }

    /** body: UpdatePlanEntry (group_id / user_id are written as given) */
    public function update(Request $request, string $itemId)
    {
        $id = Input::pathInt($itemId);
        $data = Input::object($request);
        $values = $this->parse($data);
        Input::int($data, 'id');
        $values['group_id'] = Input::uuid($data, 'group_id', false);
        $values['user_id'] = Input::uuid($data, 'user_id', false);

        if (! $this->query()->where('id', $id)->exists()) {
            Http::notFound();
        }
        Out::db()->table('group_meal_plans')->where('id', $id)->update($values + ['update_at' => Dates::nowDb()]);

        return Json::respond(Out::planEntry(Out::db()->table('group_meal_plans')->where('id', $id)->first()));
    }

    public function destroy(string $itemId)
    {
        $id = Input::pathInt($itemId);
        $row = $this->query()->where('id', $id)->first();
        if (! $row) {
            Http::deleteNotFound(self::GENERIC);
        }
        $out = Out::planEntry($row);
        Out::db()->table('group_meal_plans')->where('id', $id)->delete();

        return Json::respond($out);
    }
}
