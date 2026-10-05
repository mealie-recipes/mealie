<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\AdminService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class AdminController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(private readonly AdminService $admin) {}

    public function about(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->about());
    }

    public function statistics(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->statistics());
    }

    public function check(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->check());
    }

    public function users(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->users($request));
    }

    public function groups(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->groups($request));
    }

    public function households(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->households($request));
    }

    public function user(Request $request, string $id): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }
        $user = $this->admin->user($id);

        return $user === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($user);
    }

    public function storeUser(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->createUser($request->all()), 201);
    }

    public function updateUser(Request $request, string $id): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }
        $user = $this->admin->updateUser($id, $request->all());

        return $user === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($user);
    }

    public function destroyUser(Request $request, string $id): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }
        if (! $this->admin->deleteUser($id, $this->mealieUser($request))) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function passwordResetToken(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }
        $token = $this->admin->passwordResetToken((string) $request->input('email', ''));

        return $token === null
            ? response()->json(['detail' => 'User not found.'], 404)
            : response()->json($token);
    }

    public function unlock(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json(['unlocked' => $this->admin->unlock()]);
    }

    public function backups(Request $request): JsonResponse
    {
        if ($denied = $this->deny($request)) {
            return $denied;
        }

        return response()->json($this->admin->backups());
    }

    private function deny(Request $request): ?JsonResponse
    {
        $user = $this->mealieUser($request);
        if (! filter_var($user->admin, FILTER_VALIDATE_BOOL)) {
            return response()->json(['detail' => 'Forbidden'], 403);
        }

        return null;
    }
}
