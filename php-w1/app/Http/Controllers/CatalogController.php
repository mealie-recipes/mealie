<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\CatalogService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class CatalogController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(private readonly CatalogService $catalog) {}

    public function categories(Request $request): JsonResponse
    {
        return response()->json($this->catalog->page($this->mealieUser($request), $request, 'categories'));
    }

    public function storeCategory(Request $request): JsonResponse
    {
        return response()->json($this->catalog->createOrganizer($this->mealieUser($request), 'categories', $request->all()), 201);
    }

    public function updateCategory(Request $request, string $id): JsonResponse
    {
        return $this->updateOrganizer($request, 'categories', $id);
    }

    public function destroyCategory(Request $request, string $id): JsonResponse
    {
        return $this->destroyOrganizer($request, 'categories', $id);
    }

    public function tags(Request $request): JsonResponse
    {
        return response()->json($this->catalog->page($this->mealieUser($request), $request, 'tags'));
    }

    public function storeTag(Request $request): JsonResponse
    {
        return response()->json($this->catalog->createOrganizer($this->mealieUser($request), 'tags', $request->all()), 201);
    }

    public function tools(Request $request): JsonResponse
    {
        return response()->json($this->catalog->page($this->mealieUser($request), $request, 'tools'));
    }

    public function storeTool(Request $request): JsonResponse
    {
        return response()->json($this->catalog->createOrganizer($this->mealieUser($request), 'tools', $request->all()), 201);
    }

    public function foods(Request $request): JsonResponse
    {
        return response()->json($this->catalog->foods($this->mealieUser($request), $request));
    }

    public function updateFood(Request $request, string $id): JsonResponse
    {
        $food = $this->catalog->updateFood($this->mealieUser($request), $id, $request->all());

        return $food === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($food);
    }

    public function destroyFood(Request $request, string $id): JsonResponse
    {
        if (! $this->catalog->deleteFood($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function storeFood(Request $request): JsonResponse
    {
        return response()->json($this->catalog->createFood($this->mealieUser($request), $request->all()), 201);
    }

    public function units(Request $request): JsonResponse
    {
        return response()->json($this->catalog->units($this->mealieUser($request), $request));
    }

    public function updateUnit(Request $request, string $id): JsonResponse
    {
        $unit = $this->catalog->updateUnit($this->mealieUser($request), $id, $request->all());

        return $unit === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($unit);
    }

    public function destroyUnit(Request $request, string $id): JsonResponse
    {
        if (! $this->catalog->deleteUnit($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function storeUnit(Request $request): JsonResponse
    {
        return response()->json($this->catalog->createUnit($this->mealieUser($request), $request->all()), 201);
    }

    public function labels(Request $request): JsonResponse
    {
        return response()->json($this->catalog->labels($this->mealieUser($request), $request));
    }

    public function storeLabel(Request $request): JsonResponse
    {
        return response()->json($this->catalog->createLabel($this->mealieUser($request), $request->all()), 201);
    }

    public function updateLabel(Request $request, string $id): JsonResponse
    {
        $label = $this->catalog->updateLabel($this->mealieUser($request), $id, $request->all());

        return $label === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($label);
    }

    public function destroyLabel(Request $request, string $id): JsonResponse
    {
        if (! $this->catalog->deleteLabel($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function cookbooks(Request $request): JsonResponse
    {
        return response()->json($this->catalog->cookbooks($this->mealieUser($request), $request));
    }

    public function storeCookbook(Request $request): JsonResponse
    {
        return response()->json($this->catalog->createCookbook($this->mealieUser($request), $request->all()), 201);
    }

    public function updateCookbook(Request $request, string $id): JsonResponse
    {
        $book = $this->catalog->updateCookbook($this->mealieUser($request), $id, $request->all());

        return $book === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($book);
    }

    public function destroyCookbook(Request $request, string $id): JsonResponse
    {
        if (! $this->catalog->deleteCookbook($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function categorySlug(Request $request, string $slug): JsonResponse
    {
        return $this->bySlug($request, 'categories', $slug);
    }

    public function emptyCategories(Request $request): JsonResponse
    {
        return response()->json($this->catalog->emptyOrganizers($this->mealieUser($request), 'categories'));
    }

    public function mergeCategories(Request $request): JsonResponse
    {
        return $this->merge($request, 'categories');
    }

    public function updateTag(Request $request, string $id): JsonResponse
    {
        return $this->updateOrganizer($request, 'tags', $id);
    }

    public function destroyTag(Request $request, string $id): JsonResponse
    {
        return $this->destroyOrganizer($request, 'tags', $id);
    }

    public function tagSlug(Request $request, string $slug): JsonResponse
    {
        return $this->bySlug($request, 'tags', $slug);
    }

    public function emptyTags(Request $request): JsonResponse
    {
        return response()->json($this->catalog->emptyOrganizers($this->mealieUser($request), 'tags'));
    }

    public function mergeTags(Request $request): JsonResponse
    {
        return $this->merge($request, 'tags');
    }

    public function updateTool(Request $request, string $id): JsonResponse
    {
        return $this->updateOrganizer($request, 'tools', $id);
    }

    public function destroyTool(Request $request, string $id): JsonResponse
    {
        return $this->destroyOrganizer($request, 'tools', $id);
    }

    public function toolSlug(Request $request, string $slug): JsonResponse
    {
        return $this->bySlug($request, 'tools', $slug);
    }

    public function showFood(Request $request, string $id): JsonResponse
    {
        $food = $this->catalog->food($this->mealieUser($request), $id);

        return $food === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($food);
    }

    public function mergeFoods(Request $request): JsonResponse
    {
        $ok = $this->catalog->mergeNamed(
            $this->mealieUser($request),
            'ingredient_foods',
            (string) $request->input('toFood', $request->input('to', '')),
            array_filter([(string) $request->input('fromFood', $request->input('from', ''))]),
            'food_id',
        );

        return $ok
            ? response()->json(['message' => 'Merged'])
            : response()->json(['detail' => 'Not found.'], 404);
    }

    public function showUnit(Request $request, string $id): JsonResponse
    {
        $unit = $this->catalog->unit($this->mealieUser($request), $id);

        return $unit === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($unit);
    }

    public function mergeUnits(Request $request): JsonResponse
    {
        $ok = $this->catalog->mergeNamed(
            $this->mealieUser($request),
            'ingredient_units',
            (string) $request->input('toUnit', $request->input('to', '')),
            array_filter([(string) $request->input('fromUnit', $request->input('from', ''))]),
            'unit_id',
        );

        return $ok
            ? response()->json(['message' => 'Merged'])
            : response()->json(['detail' => 'Not found.'], 404);
    }

    private function bySlug(Request $request, string $table, string $slug): JsonResponse
    {
        $row = $this->catalog->organizerBySlug($this->mealieUser($request), $table, $slug);

        return $row === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($row);
    }

    private function merge(Request $request, string $table): JsonResponse
    {
        $row = $this->catalog->mergeOrganizers(
            $this->mealieUser($request),
            $table,
            (string) $request->input('toId', $request->input('to', '')),
            array_filter([(string) $request->input('fromId', $request->input('from', ''))]),
        );

        return $row === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($row);
    }

    private function updateOrganizer(Request $request, string $table, string $id): JsonResponse
    {
        $row = $this->catalog->updateOrganizer($this->mealieUser($request), $table, $id, $request->all());
        if ($row === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($row);
    }

    private function destroyOrganizer(Request $request, string $table, string $id): JsonResponse
    {
        if (! $this->catalog->deleteOrganizer($this->mealieUser($request), $table, $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }
}
