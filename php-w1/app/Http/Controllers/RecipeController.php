<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\ResolvesMealieUser;
use App\Services\ImportService;
use App\Services\RecipeService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

final class RecipeController extends Controller
{
    use ResolvesMealieUser;

    public function __construct(
        private readonly RecipeService $recipes,
        private readonly ImportService $imports,
    ) {}

    public function index(Request $request): JsonResponse
    {
        return response()->json($this->recipes->page($this->mealieUser($request), $request));
    }

    public function store(Request $request): JsonResponse
    {
        return response()->json($this->recipes->create($this->mealieUser($request), $request->all()), 201);
    }

    public function show(Request $request, string $slug): JsonResponse
    {
        $recipe = $this->recipes->find($this->mealieUser($request), $slug);
        if ($recipe === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($recipe);
    }

    public function update(Request $request, string $slug): JsonResponse
    {
        $recipe = $this->recipes->update($this->mealieUser($request), $slug, $request->all());
        if ($recipe === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($recipe);
    }

    public function destroy(Request $request, string $slug): JsonResponse
    {
        if (! $this->recipes->delete($this->mealieUser($request), $slug)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function comments(Request $request, string $slug): JsonResponse
    {
        $recipe = $this->recipes->find($this->mealieUser($request), $slug);
        if ($recipe === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($recipe['comments'] ?? []);
    }

    public function lastMade(Request $request, string $slug): JsonResponse
    {
        $recipe = $this->recipes->touchLastMade($this->mealieUser($request), $slug);
        if ($recipe === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($recipe);
    }

    public function duplicate(Request $request, string $slug): JsonResponse
    {
        $recipe = $this->recipes->duplicate($this->mealieUser($request), $slug);
        if ($recipe === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($recipe, 201);
    }

    public function suggestions(Request $request): JsonResponse
    {
        $limit = (int) $request->query('maxMissingFoods', $request->query('limit', 5));

        return response()->json($this->recipes->suggestions($this->mealieUser($request), $limit > 0 ? min($limit, 20) : 5));
    }

    public function bulk(Request $request, string $action): JsonResponse
    {
        $this->recipes->bulk($this->mealieUser($request), $action, $request->all());

        return response()->json(['message' => 'OK']);
    }

    public function testScrape(Request $request): JsonResponse
    {
        $url = (string) $request->input('url', '');
        if ($url === '' || ! filter_var($url, FILTER_VALIDATE_URL)) {
            return response()->json(['detail' => 'URL is not valid'], 400);
        }

        return response()->json(['url' => $url, 'ready' => true]);
    }

    public function importAi(Request $request): Response
    {
        $prompt = (string) ($request->input('content') ?? $request->input('prompt') ?? $request->input('recipe') ?? '');

        return response($this->imports->streamAi($this->mealieUser($request), $prompt), 200, [
            'Content-Type' => 'text/event-stream',
            'Cache-Control' => 'no-cache',
        ]);
    }

    public function importDocument(Request $request): Response
    {
        $body = (string) ($request->input('data') ?? $request->input('json') ?? $request->getContent());
        try {
            $recipe = $this->imports->fromDocument($this->mealieUser($request), $body);
        } catch (\Throwable $e) {
            return response($this->imports->errorStream($e->getMessage()), 200, [
                'Content-Type' => 'text/event-stream',
                'Cache-Control' => 'no-cache',
            ]);
        }

        return response("event: done\ndata: ".json_encode(['slug' => $recipe['slug'] ?? ''])."\n\n", 200, [
            'Content-Type' => 'text/event-stream',
            'Cache-Control' => 'no-cache',
        ]);
    }

    public function importBulk(Request $request): JsonResponse
    {
        $urls = $request->input('urls', []);
        if (! is_array($urls)) {
            $urls = [];
        }
        $report = [];
        foreach ($urls as $url) {
            if (! is_string($url) || $url === '') {
                continue;
            }
            try {
                $recipe = $this->imports->fromUrl($this->mealieUser($request), $url);
                $report[] = ['url' => $url, 'slug' => $recipe['slug'] ?? null, 'status' => true];
            } catch (\Throwable $e) {
                $report[] = ['url' => $url, 'status' => false, 'exception' => $e->getMessage()];
            }
        }

        return response()->json($report);
    }

    public function assets(Request $request, string $slug): JsonResponse
    {
        $assets = $this->recipes->assets($this->mealieUser($request), $slug);

        return $assets === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($assets);
    }

    public function storeAsset(Request $request, string $slug): JsonResponse
    {
        $file = $request->file('file') ?? $request->file('archive');
        $bytes = $file !== null ? (string) file_get_contents($file->getRealPath()) : '';
        $name = $file !== null ? $file->getClientOriginalName() : 'asset.bin';
        $asset = $this->recipes->storeAsset($this->mealieUser($request), $slug, $name, $bytes);

        return $asset === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($asset, 201);
    }

    public function importUrl(Request $request): JsonResponse|Response
    {
        $url = (string) ($request->input('url') ?? $request->json('url') ?? '');
        if ($request->is('*/stream')) {
            return response($this->imports->stream($this->mealieUser($request), $url), 200, [
                'Content-Type' => 'text/event-stream',
                'Cache-Control' => 'no-cache',
            ]);
        }
        try {
            $recipe = $this->imports->fromUrl($this->mealieUser($request), $url);
        } catch (\Throwable $e) {
            return response()->json(['detail' => $e->getMessage()], 400);
        }

        return response()->json($recipe['slug'] ?? '', 201);
    }

    public function commentIndex(Request $request): JsonResponse
    {
        return response()->json($this->recipes->commentPage($this->mealieUser($request), $request));
    }

    public function updateComment(Request $request, string $id): JsonResponse
    {
        $comment = $this->recipes->updateComment($this->mealieUser($request), $id, (string) $request->input('text', ''));
        if ($comment === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($comment);
    }

    public function destroyComment(Request $request, string $id): JsonResponse
    {
        if (! $this->recipes->deleteComment($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function shares(Request $request): JsonResponse
    {
        return response()->json($this->recipes->shares($this->mealieUser($request), $request));
    }

    public function storeShare(Request $request): JsonResponse
    {
        $share = $this->recipes->createShare($this->mealieUser($request), $request->all());
        if ($share === null) {
            return response()->json(['detail' => 'Recipe not found.'], 404);
        }

        return response()->json($share, 201);
    }

    public function share(Request $request, string $id): JsonResponse
    {
        $share = $this->recipes->share($this->mealieUser($request), $id);

        return $share === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($share);
    }

    public function destroyShare(Request $request, string $id): JsonResponse
    {
        if (! $this->recipes->deleteShare($this->mealieUser($request), $id)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function sharedZip(string $token): BinaryFileResponse|JsonResponse
    {
        $recipe = $this->recipes->sharedRecipe($token);
        if ($recipe === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }
        $path = tempnam(sys_get_temp_dir(), 'mealie-share');
        $zip = new \ZipArchive;
        $zip->open($path, \ZipArchive::OVERWRITE);
        $zip->addFromString('recipe.json', json_encode($recipe, JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT));
        $zip->close();

        return response()->download($path, 'recipe.zip')->deleteFileAfterSend();
    }

    public function shared(string $token): JsonResponse
    {
        $recipe = $this->recipes->sharedRecipe($token);

        return $recipe === null
            ? response()->json(['detail' => 'Not found.'], 404)
            : response()->json($recipe);
    }

    public function uploadImage(Request $request, string $slug): JsonResponse
    {
        $file = $request->file('image');
        $bytes = $file !== null ? (string) file_get_contents($file->getRealPath()) : (string) $request->getContent();
        $saved = $this->recipes->saveImage($this->mealieUser($request), $slug, $bytes);
        if ($saved === null) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($saved);
    }

    public function deleteImage(Request $request, string $slug): JsonResponse
    {
        if (! $this->recipes->deleteImage($this->mealieUser($request), $slug)) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json(['message' => 'Deleted']);
    }

    public function storeComment(Request $request, string $slug): JsonResponse
    {
        $comment = $this->recipes->addComment($this->mealieUser($request), $slug, (string) $request->input('text', ''));
        if ($comment === []) {
            return response()->json(['detail' => 'Not found.'], 404);
        }

        return response()->json($comment, 201);
    }
}
