<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\AccountService;
use App\Support\Guid;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class AccountController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(private readonly AccountService $accounts) {}

    public function updateSelf(Request $request): JsonResponse
    {
        return response()->json($this->accounts->updateSelf($this->mealieUser($request), $request->all()));
    }

    public function tokens(Request $request): JsonResponse
    {
        return response()->json($this->accounts->tokens($this->mealieUser($request)));
    }

    public function storeToken(Request $request): JsonResponse
    {
        return response()->json($this->accounts->createToken($this->mealieUser($request), (string) $request->input('name', 'Token')), 201);
    }

    public function destroyToken(Request $request, int $id): JsonResponse
    {
        if (! $this->accounts->deleteToken($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function permissions(Request $request): JsonResponse
    {
        $user = $this->accounts->setPermissions($this->mealieUser($request), $request->all());

        return $user === null
            ? response()->json(['detail' => 'Not allowed'], 403)
            : response()->json($user);
    }

    public function self(Request $request): JsonResponse
    {
        return response()->json($this->accounts->userOut($this->mealieUser($request)));
    }

    public function ratings(Request $request): JsonResponse
    {
        return response()->json($this->accounts->ratings($this->mealieUser($request)));
    }

    public function favorites(Request $request): JsonResponse
    {
        return response()->json($this->accounts->ratings($this->mealieUser($request), true));
    }

    public function setRating(Request $request, string $id, string $slug): JsonResponse
    {
        $user = $this->mealieUser($request);
        if (strcasecmp(Guid::dashed($user->id) ?? '', $id) !== 0 && Guid::hex($user->id) !== Guid::hex($id)) {
            return response()->json(['detail' => 'Forbidden'], 403);
        }
        $rating = $request->exists('rating') ? ($request->input('rating') === null ? null : (float) $request->input('rating')) : null;
        $favorite = $request->exists('isFavorite') || $request->exists('is_favorite')
            ? filter_var($request->input('isFavorite', $request->input('is_favorite')), FILTER_VALIDATE_BOOL)
            : null;
        $row = $this->accounts->setRating($user, $slug, $rating, $favorite);
        if ($row === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($row);
    }

    public function favorite(Request $request, string $id, string $slug): JsonResponse
    {
        $request->merge(['isFavorite' => true]);

        return $this->setRating($request, $id, $slug);
    }

    public function unfavorite(Request $request, string $id, string $slug): JsonResponse
    {
        $request->merge(['isFavorite' => false]);

        return $this->setRating($request, $id, $slug);
    }

    public function forgotPassword(Request $request): JsonResponse
    {
        $this->accounts->forgotPassword((string) $request->input('email', ''));

        return response()->json(['message' => 'If that email exists, a reset token was created']);
    }

    public function resetPassword(Request $request): JsonResponse
    {
        $ok = $this->accounts->resetPassword(
            (string) $request->input('token', ''),
            (string) $request->input('password', ''),
        );
        if (! $ok) {
            return response()->json(['detail' => 'Invalid reset token'], 400);
        }

        return response()->json(['message' => 'Password updated']);
    }

    public function register(Request $request): JsonResponse
    {
        try {
            return response()->json($this->accounts->register($request->all()), 201);
        } catch (\RuntimeException) {
            return response()->json(['detail' => 'User Registration is Disabled'], 403);
        } catch (\InvalidArgumentException $e) {
            return response()->json(['detail' => $e->getMessage()], 400);
        }
    }

    public function uploadImage(Request $request, string $id): JsonResponse
    {
        $file = $request->file('profile') ?? $request->file('image');
        $bytes = $file !== null ? (string) file_get_contents($file->getRealPath()) : '';
        if (! $this->accounts->saveUserImage($this->mealieUser($request), $id, $bytes)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'OK']);
    }

    public function password(Request $request): JsonResponse
    {
        $ok = $this->accounts->changePassword(
            $this->mealieUser($request),
            (string) $request->input('currentPassword', $request->input('current_password', '')),
            (string) $request->input('newPassword', $request->input('new_password', '')),
        );

        if (! $ok) {
            return response()->json(['detail' => 'Invalid current password'], 400);
        }

        return response()->json(['message' => 'Password updated']);
    }

    public function group(Request $request): JsonResponse
    {
        return response()->json($this->accounts->groupSelf($this->mealieUser($request)));
    }

    public function groupPreferences(Request $request): JsonResponse
    {
        return response()->json($this->accounts->groupPreferencesFor($this->mealieUser($request)));
    }

    public function updateGroupPreferences(Request $request): JsonResponse
    {
        return response()->json($this->accounts->updateGroupPreferences($this->mealieUser($request), $request->all()));
    }

    public function groupMembers(Request $request): JsonResponse
    {
        return response()->json($this->accounts->members($this->mealieUser($request), 'group', $request));
    }

    public function household(Request $request): JsonResponse
    {
        return response()->json($this->accounts->householdSelf($this->mealieUser($request)));
    }

    public function householdPreferences(Request $request): JsonResponse
    {
        return response()->json($this->accounts->householdPreferencesFor($this->mealieUser($request)));
    }

    public function updateHouseholdPreferences(Request $request): JsonResponse
    {
        return response()->json($this->accounts->updateHouseholdPreferences($this->mealieUser($request), $request->all()));
    }

    public function householdMembers(Request $request): JsonResponse
    {
        return response()->json($this->accounts->members($this->mealieUser($request), 'household', $request));
    }

    public function householdStatistics(Request $request): JsonResponse
    {
        return response()->json($this->accounts->householdStatistics($this->mealieUser($request)));
    }
}
