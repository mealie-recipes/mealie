<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\AiService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class AiController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(private readonly AiService $ai) {}

    public function settings(Request $request): JsonResponse
    {
        return response()->json($this->ai->settings($this->mealieUser($request)));
    }

    public function updateSettings(Request $request): JsonResponse
    {
        return response()->json($this->ai->updateSettings($this->mealieUser($request), $request->all()));
    }

    public function providers(Request $request): JsonResponse
    {
        return response()->json($this->ai->providers($this->mealieUser($request)));
    }

    public function storeProvider(Request $request): JsonResponse
    {
        return response()->json($this->ai->createProvider($this->mealieUser($request), $request->all()), 201);
    }

    public function provider(Request $request, string $id): JsonResponse
    {
        $provider = $this->ai->provider($this->mealieUser($request), $id);

        return $provider === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($provider);
    }

    public function updateProvider(Request $request, string $id): JsonResponse
    {
        $provider = $this->ai->updateProvider($this->mealieUser($request), $id, $request->all());

        return $provider === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($provider);
    }

    public function destroyProvider(Request $request, string $id): JsonResponse
    {
        if (! $this->ai->deleteProvider($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function test(Request $request): JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Live provider tests are not available on the PHP backend yet',
        ]);
    }
}
