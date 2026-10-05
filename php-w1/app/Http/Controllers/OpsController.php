<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\MailService;
use App\Services\MigrationService;
use App\Services\OpsService;
use App\Support\MealieDb;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

final class OpsController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(
        private readonly OpsService $ops,
        private readonly MailService $mail,
        private readonly MigrationService $migrations,
    ) {}

    public function reports(Request $request): JsonResponse
    {
        $category = $request->query('report_type', $request->query('reportType'));

        return response()->json($this->ops->reports($this->mealieUser($request), is_string($category) ? $category : null));
    }

    public function report(Request $request, string $id): JsonResponse
    {
        $report = $this->ops->findReport($this->mealieUser($request), $id);

        return $report === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($report);
    }

    public function destroyReport(Request $request, string $id): JsonResponse
    {
        if (! $this->ops->deleteReport($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function notifiers(Request $request): JsonResponse
    {
        return response()->json($this->ops->notifiers($this->mealieUser($request), $request));
    }

    public function storeNotifier(Request $request): JsonResponse
    {
        return response()->json($this->ops->createNotifier($this->mealieUser($request), $request->all()), 201);
    }

    public function updateNotifier(Request $request, string $id): JsonResponse
    {
        $row = $this->ops->updateNotifier($this->mealieUser($request), $id, $request->all());

        return $row === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($row);
    }

    public function destroyNotifier(Request $request, string $id): JsonResponse
    {
        if (! $this->ops->deleteNotifier($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function testNotifier(Request $request, string $id): JsonResponse
    {
        $row = $this->ops->updateNotifier($this->mealieUser($request), $id, []);
        if ($row === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }
        $url = (string) ($row['appriseUrl'] ?? '');
        if (! str_starts_with($url, 'http://') && ! str_starts_with($url, 'https://')) {
            return response()->json(['success' => false, 'error' => 'Only http and https notifier URLs can be called']);
        }
        try {
            $response = Http::timeout(5)->post($url, [
                'title' => 'Mealie',
                'body' => 'Notifier test from the PHP backend',
            ]);
        } catch (\Throwable $e) {
            return response()->json(['success' => false, 'error' => $e->getMessage()]);
        }

        return response()->json(['success' => $response->successful(), 'error' => $response->successful() ? null : 'Notifier returned '.$response->status()]);
    }

    public function actions(Request $request): JsonResponse
    {
        return response()->json($this->ops->actions($this->mealieUser($request), $request));
    }

    public function storeAction(Request $request): JsonResponse
    {
        return response()->json($this->ops->createAction($this->mealieUser($request), $request->all()), 201);
    }

    public function updateAction(Request $request, string $id): JsonResponse
    {
        $row = $this->ops->updateAction($this->mealieUser($request), $id, $request->all());

        return $row === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($row);
    }

    public function destroyAction(Request $request, string $id): JsonResponse
    {
        if (! $this->ops->deleteAction($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function triggerAction(Request $request, string $id, string $slug): JsonResponse
    {
        $row = $this->ops->updateAction($this->mealieUser($request), $id, []);
        if ($row === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json([
            'message' => 'Triggered',
            'url' => $row['url'],
            'recipe' => $slug,
            'scale' => (float) $request->input('recipe_scale', $request->input('recipeScale', 1)),
        ]);
    }

    public function seedFoods(Request $request): JsonResponse
    {
        return response()->json($this->ops->seed($this->mealieUser($request), 'ingredient_foods', (string) $request->input('locale', 'en-US')));
    }

    public function seedUnits(Request $request): JsonResponse
    {
        return response()->json($this->ops->seed($this->mealieUser($request), 'ingredient_units', (string) $request->input('locale', 'en-US')));
    }

    public function households(Request $request): JsonResponse
    {
        return response()->json($this->ops->households($this->mealieUser($request), $request));
    }

    public function storeHousehold(Request $request): JsonResponse
    {
        return response()->json($this->ops->createHousehold($this->mealieUser($request), $request->all()), 201);
    }

    public function updateHousehold(Request $request, string $id): JsonResponse
    {
        $row = $this->ops->updateHousehold($this->mealieUser($request), $id, $request->all());

        return $row === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($row);
    }

    public function destroyHousehold(Request $request, string $id): JsonResponse
    {
        if (! $this->ops->deleteHousehold($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Household could not be deleted'], 400);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function storage(Request $request): JsonResponse
    {
        return response()->json($this->ops->groupStorage($this->mealieUser($request)));
    }

    public function labelSettings(Request $request, string $itemId): JsonResponse
    {
        $ids = $request->input('labelIds', $request->input('labels', []));
        if (! is_array($ids)) {
            $ids = [];
        }
        if (! $this->ops->replaceLabelSettings($this->mealieUser($request), $itemId, $ids)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Updated']);
    }

    public function email(Request $request): JsonResponse
    {
        $address = (string) $request->input('email', '');
        $token = (string) $request->input('token', '');
        $base = rtrim((string) config('mealie.base_url'), '/');
        $result = $token !== ''
            ? $this->mail->send($address, 'You are invited to Mealie', 'Create your account: '.$base.'/register?token='.$token)
            : $this->mail->send($address, 'Mealie email test', 'This is a test email from Mealie.');

        return response()->json($result, $result['success'] ? 200 : 400);
    }

    public function migration(Request $request): JsonResponse
    {
        $file = $request->file('archive');
        $bytes = $file !== null ? (string) file_get_contents($file->getRealPath()) : '';
        $report = $this->migrations->importArchive(
            $this->mealieUser($request),
            $bytes,
            (string) $request->input('migration_type', $request->input('migrationType', 'nextcloud')),
        );

        return response()->json($report, $report['status'] === 'failure' ? 400 : 200);
    }

    public function backups(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json($this->ops->backups());
    }

    public function createBackup(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json(['message' => 'Backup created', 'name' => $this->ops->createBackup()], 201);
    }

    public function downloadBackup(Request $request, string $fileName): BinaryFileResponse|JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }
        $path = $this->ops->backupPath($fileName);

        return $path === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->download($path, $fileName);
    }

    public function destroyBackup(Request $request, string $fileName): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }
        if (! $this->ops->deleteBackup($fileName)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function uploadBackup(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }
        $file = $request->file('archive') ?? $request->file('file');
        if ($file === null || ! $this->ops->storeUpload($file->getClientOriginalName(), (string) file_get_contents($file->getRealPath()))) {
            return response()->json(['detail' => 'Upload a .zip archive'], 400);
        }

        return response()->json(['message' => 'Upload successful']);
    }

    public function restoreBackup(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        try {
            $this->ops->restoreBackup((string) $request->route('fileName'));
        } catch (\Throwable $e) {
            return response()->json(['detail' => $e->getMessage()], 400);
        }

        return response()->json(['message' => 'Backup restored']);
    }

    public function maintenance(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json($this->ops->maintenance());
    }

    public function storageDetails(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json($this->ops->storageDetails());
    }

    public function logs(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json($this->ops->logs((int) $request->query('lines', 100)));
    }

    public function clean(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json(['message' => 'Nothing to clean']);
    }

    public function analytics(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json([
            'installationId' => substr(sha1((string) config('mealie.data_dir')), 0, 32),
            'version' => (string) config('mealie.version'),
            'databaseType' => (string) config('database.connections.mealie.driver'),
            'usingEmail' => false,
            'usingLdap' => false,
            'apiTokens' => MealieDb::table('long_live_tokens')->count(),
            'users' => MealieDb::table('users')->count(),
            'groups' => MealieDb::table('groups')->count(),
            'recipes' => MealieDb::table('recipes')->count(),
            'shoppingLists' => MealieDb::table('shopping_lists')->count(),
            'cookbooks' => MealieDb::table('cookbooks')->count(),
        ]);
    }

    public function storeGroup(Request $request): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }

        return response()->json($this->ops->createGroup($request->all()), 201);
    }

    public function destroyGroup(Request $request, string $id): JsonResponse
    {
        if ($denied = $this->admin($request)) {
            return $denied;
        }
        if (! $this->ops->deleteGroup($id)) {
            return response()->json(['detail' => 'Group could not be deleted'], 400);
        }

        return response()->json(['message' => 'Deleted']);
    }

    private function admin(Request $request): ?JsonResponse
    {
        $user = $this->mealieUser($request);
        if (! filter_var($user->admin, FILTER_VALIDATE_BOOL)) {
            return response()->json(['detail' => 'Forbidden'], 403);
        }

        return null;
    }
}
