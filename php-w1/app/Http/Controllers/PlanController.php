<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\PlanService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class PlanController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(private readonly PlanService $plans) {}

    public function rules(Request $request): JsonResponse
    {
        return response()->json($this->plans->rules($this->mealieUser($request), $request));
    }

    public function storeRule(Request $request): JsonResponse
    {
        return response()->json($this->plans->createRule($this->mealieUser($request), $request->all()), 201);
    }

    public function updateRule(Request $request, string $itemId): JsonResponse
    {
        $rule = $this->plans->updateRule($this->mealieUser($request), $itemId, $request->all());

        return $rule === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($rule);
    }

    public function destroyRule(Request $request, string $itemId): JsonResponse
    {
        if (! $this->plans->deleteRule($this->mealieUser($request), $itemId)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function mealPlans(Request $request): JsonResponse
    {
        return response()->json($this->plans->mealPlans($this->mealieUser($request), $request));
    }

    public function today(Request $request): JsonResponse
    {
        return response()->json($this->plans->todaysMeals($this->mealieUser($request)));
    }

    public function random(Request $request): JsonResponse
    {
        $entry = $this->plans->randomMeal($this->mealieUser($request), $request->all());
        if ($entry === null) {
            return response()->json(['detail' => 'No recipes match your rules'], 404);
        }

        return response()->json($entry, 201);
    }

    public function storeMealPlan(Request $request): JsonResponse
    {
        return response()->json($this->plans->createMealPlan($this->mealieUser($request), $request->all()), 201);
    }

    public function updateMealPlan(Request $request, int $itemId): JsonResponse
    {
        $entry = $this->plans->updateMealPlan($this->mealieUser($request), $itemId, $request->all());
        if ($entry === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($entry);
    }

    public function destroyMealPlan(Request $request, int $itemId): JsonResponse
    {
        if (! $this->plans->deleteMealPlan($this->mealieUser($request), $itemId)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function shoppingLists(Request $request): JsonResponse
    {
        return response()->json($this->plans->shoppingLists($this->mealieUser($request), $request));
    }

    public function shoppingList(Request $request, string $itemId): JsonResponse
    {
        $list = $this->plans->findShoppingList($this->mealieUser($request), $itemId);
        if ($list === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($list);
    }

    public function storeShoppingList(Request $request): JsonResponse
    {
        return response()->json($this->plans->createShoppingList($this->mealieUser($request), $request->all()), 201);
    }

    public function updateShoppingList(Request $request, string $itemId): JsonResponse
    {
        $list = $this->plans->updateShoppingList($this->mealieUser($request), $itemId, $request->all());
        if ($list === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($list);
    }

    public function addRecipe(Request $request, string $itemId): JsonResponse
    {
        $payload = $request->all();
        $recipes = array_is_list($payload) ? $payload : [$payload];
        $list = $this->plans->addRecipes($this->mealieUser($request), $itemId, $recipes);
        if ($list === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($list);
    }

    public function addOneRecipe(Request $request, string $itemId, string $recipeId): JsonResponse
    {
        $payload = $request->all();
        $payload['recipeId'] = $recipeId;
        $list = $this->plans->addRecipes($this->mealieUser($request), $itemId, [$payload]);
        if ($list === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($list);
    }

    public function removeRecipe(Request $request, string $itemId, string $recipeId): JsonResponse
    {
        $decrement = (float) $request->input('recipeDecrementQuantity', $request->input('recipe_decrement_quantity', 1));
        $list = $this->plans->removeRecipe($this->mealieUser($request), $itemId, $recipeId, $decrement);
        if ($list === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($list);
    }

    public function destroyShoppingList(Request $request, string $itemId): JsonResponse
    {
        if (! $this->plans->deleteShoppingList($this->mealieUser($request), $itemId)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function items(Request $request): JsonResponse
    {
        return response()->json($this->plans->shoppingItems($this->mealieUser($request), $request));
    }

    public function storeItem(Request $request): JsonResponse
    {
        $payload = $request->all();
        $items = array_is_list($payload) ? $payload : [$payload];

        return response()->json($this->plans->createItems($this->mealieUser($request), $items), 201);
    }

    public function updateItems(Request $request): JsonResponse
    {
        $payload = $request->all();
        $items = array_is_list($payload) ? $payload : [$payload];

        return response()->json($this->plans->updateItems($this->mealieUser($request), $items));
    }

    public function updateItem(Request $request, string $itemId): JsonResponse
    {
        $payload = $request->all();
        $payload['id'] = $itemId;

        return response()->json($this->plans->updateItems($this->mealieUser($request), [$payload]));
    }

    public function destroyItems(Request $request): JsonResponse
    {
        $ids = $request->query('ids', []);
        if (is_string($ids)) {
            $ids = [$ids];
        }

        $this->plans->deleteItems($this->mealieUser($request), $ids);

        return response()->json(['message' => 'Deleted']);
    }

    public function destroyItem(Request $request, string $itemId): JsonResponse
    {
        $this->plans->deleteItems($this->mealieUser($request), [$itemId]);

        return response()->json(['message' => 'Deleted']);
    }
}
