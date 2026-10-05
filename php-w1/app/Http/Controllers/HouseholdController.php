<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\HouseholdService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class HouseholdController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(private readonly HouseholdService $households) {}

    public function timeline(Request $request): JsonResponse
    {
        return response()->json($this->households->timeline($this->mealieUser($request), $request));
    }

    public function uploadTimelineImage(Request $request, string $id): JsonResponse
    {
        $file = $request->file('image');
        $bytes = $file !== null ? (string) file_get_contents($file->getRealPath()) : '';
        $event = $this->households->saveTimelineImage($this->mealieUser($request), $id, $bytes);

        return $event === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($event);
    }

    public function updateTimeline(Request $request, string $id): JsonResponse
    {
        $event = $this->households->updateTimeline($this->mealieUser($request), $id, $request->all());

        return $event === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($event);
    }

    public function destroyTimeline(Request $request, string $id): JsonResponse
    {
        if (! $this->households->deleteTimeline($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function storeTimeline(Request $request): JsonResponse
    {
        $event = $this->households->createTimeline($this->mealieUser($request), $request->all());
        if ($event === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($event, 201);
    }

    public function webhooks(Request $request): JsonResponse
    {
        return response()->json($this->households->webhooks($this->mealieUser($request), $request));
    }

    public function webhook(Request $request, string $id): JsonResponse
    {
        $hook = $this->households->webhookOne($this->mealieUser($request), $id);

        return $hook === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($hook);
    }

    public function updateWebhook(Request $request, string $id): JsonResponse
    {
        $hook = $this->households->updateWebhook($this->mealieUser($request), $id, $request->all());

        return $hook === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($hook);
    }

    public function testWebhook(Request $request, string $id): JsonResponse
    {
        if (! $this->households->testWebhook($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Webhook test failed'], 400);
        }

        return response()->json(null);
    }

    public function storeWebhook(Request $request): JsonResponse
    {
        return response()->json($this->households->createWebhook($this->mealieUser($request), $request->all()), 201);
    }

    public function destroyWebhook(Request $request, string $id): JsonResponse
    {
        if (! $this->households->deleteWebhook($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function invitations(Request $request): JsonResponse
    {
        $user = $this->mealieUser($request);
        if (! filter_var($user->admin, FILTER_VALIDATE_BOOL)) {
            return response()->json(['detail' => 'Only admins can list invite tokens'], 403);
        }

        return response()->json($this->households->invitations($user));
    }

    public function storeInvitation(Request $request): JsonResponse
    {
        $uses = (int) $request->input('uses', $request->input('usesLeft', 1));

        return response()->json($this->households->createInvitation($this->mealieUser($request), $uses), 201);
    }
}
