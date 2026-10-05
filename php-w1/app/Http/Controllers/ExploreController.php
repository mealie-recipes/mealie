<?php

namespace App\Http\Controllers;

use App\Services\ExploreService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class ExploreController extends Controller
{
    public function __construct(private readonly ExploreService $explore) {}

    public function recipes(Request $request, string $groupSlug): JsonResponse
    {
        $page = $this->explore->recipes($groupSlug, $request);

        return $page === null
            ? response()->json(['detail' => 'group not found'], 404)
            : response()->json($page);
    }

    public function recipe(string $groupSlug, string $recipeSlug): JsonResponse
    {
        $recipe = $this->explore->recipe($groupSlug, $recipeSlug);

        return $recipe === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($recipe);
    }

    public function categories(Request $request, string $groupSlug): JsonResponse
    {
        return $this->organizers($request, $groupSlug, 'categories');
    }

    public function tags(Request $request, string $groupSlug): JsonResponse
    {
        return $this->organizers($request, $groupSlug, 'tags');
    }

    public function tools(Request $request, string $groupSlug): JsonResponse
    {
        return $this->organizers($request, $groupSlug, 'tools');
    }

    public function foods(Request $request, string $groupSlug): JsonResponse
    {
        $page = $this->explore->foods($groupSlug, $request);

        return $page === null
            ? response()->json(['detail' => 'group not found'], 404)
            : response()->json($page);
    }

    public function cookbooks(Request $request, string $groupSlug, string $householdSlug): JsonResponse
    {
        $page = $this->explore->cookbooks($groupSlug, $householdSlug, $request);

        return $page === null
            ? response()->json(['detail' => 'group not found'], 404)
            : response()->json($page);
    }

    public function households(Request $request, string $groupSlug): JsonResponse
    {
        $page = $this->explore->households($groupSlug, $request);

        return $page === null
            ? response()->json(['detail' => 'group not found'], 404)
            : response()->json($page);
    }

    private function organizers(Request $request, string $groupSlug, string $table): JsonResponse
    {
        $page = $this->explore->organizers($groupSlug, $table, $request);

        return $page === null
            ? response()->json(['detail' => 'group not found'], 404)
            : response()->json($page);
    }
}
