<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Http;
use App\Areas\Households\Support\Input;
use App\Areas\Households\Support\Out;
use App\Areas\Households\Support\Paginator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/households/controller_mealplan_rules.py (PlanRulesOut, household-scoped repo) */
class MealplanRuleController
{
    private const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'unset'];

    private const TYPES = ['breakfast', 'lunch', 'dinner', 'side', 'snack', 'drink', 'dessert', 'unset'];

    private function query()
    {
        return Out::db()->table('group_meal_plan_rules')
            ->where('group_id', CurrentUser::groupId())->where('household_id', CurrentUser::householdId());
    }

    /** PlanRulesCreate (non-empty query_filter_string is not validated: query-filter language out of scope) */
    private function parse(array $data): array
    {
        return [
            'day' => Input::enum($data, 'day', self::DAYS, 'unset'),
            'entry_type' => Input::enum($data, 'entry_type', self::TYPES, 'unset'),
            'query_filter_string' => Input::str($data, 'query_filter_string', ''),
        ];
    }

    public function index(Request $request)
    {
        return Json::respond(Paginator::page(
            $request, $this->query(), fn ($r) => Out::planRule($r), 'group_meal_plan_rules',
            ['id', 'group_id', 'household_id', 'day', 'entry_type', 'created_at', 'update_at'],
            ['day', 'entry_type'], '/households/mealplans/rules', null, 'GroupMealPlanRules', ['query_filter_string'],
        ));
    }

    public function store(Request $request)
    {
        $values = $this->parse(Input::object($request));
        $id = Guid::new();
        $now = Dates::nowDb();
        Out::db()->table('group_meal_plan_rules')->insert($values + [
            'id' => $id,
            'group_id' => CurrentUser::groupId(),
            'household_id' => CurrentUser::householdId(),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return Json::respond(Out::planRule(Out::db()->table('group_meal_plan_rules')->where('id', $id)->first()), 201);
    }

    public function show(string $itemId)
    {
        $row = $this->query()->where('id', Guid::requireUuid4($itemId))->first();
        if (! $row) {
            Http::notFound();
        }

        return Json::respond(Out::planRule($row));
    }

    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $values = $this->parse(Input::object($request));
        if (! $this->query()->where('id', $id)->exists()) {
            Http::notFound();
        }
        Out::db()->table('group_meal_plan_rules')->where('id', $id)->update($values + ['update_at' => Dates::nowDb()]);

        return Json::respond(Out::planRule(Out::db()->table('group_meal_plan_rules')->where('id', $id)->first()));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $row = $this->query()->where('id', $id)->first();
        if (! $row) {
            Http::deleteNotFound('An unexpected error occurred.');
        }
        $db = Out::db();
        $db->table('plan_rules_to_categories')->where('group_plan_rule_id', $id)->delete();
        $db->table('plan_rules_to_tags')->where('plan_rule_id', $id)->delete();
        $db->table('plan_rules_to_households')->where('group_plan_rule_id', $id)->delete();
        $db->table('group_meal_plan_rules')->where('id', $id)->delete();

        return Json::respond(Out::planRule($row));
    }
}
