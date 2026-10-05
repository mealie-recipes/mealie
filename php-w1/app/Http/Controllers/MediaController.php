<?php

namespace App\Http\Controllers;

use App\Support\Guid;
use Illuminate\Http\Response;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

final class MediaController extends Controller
{
    public function recipeImage(string $recipeId, string $fileName): BinaryFileResponse|Response
    {
        $allowed = ['original.webp', 'min-original.webp', 'tiny-original.webp'];
        if (! in_array($fileName, $allowed, true) || Guid::hex($recipeId) === null) {
            return response('Not found.', 404);
        }

        $path = $this->dataDir().'/recipes/'.Guid::dashed($recipeId).'/images/'.$fileName;

        return $this->file($path, 'image/webp');
    }

    public function timelineImage(string $recipeId, string $eventId, string $fileName): BinaryFileResponse|Response
    {
        $allowed = ['original.webp', 'min-original.webp', 'tiny-original.webp'];
        if (! in_array($fileName, $allowed, true) || Guid::hex($recipeId) === null || Guid::hex($eventId) === null) {
            return response('Not found.', 404);
        }
        $path = $this->dataDir().'/recipes/'.Guid::dashed($recipeId).'/images/timeline/'.Guid::dashed($eventId).'/'.$fileName;

        return $this->file($path, 'image/webp');
    }

    public function userImage(string $userId, string $fileName): BinaryFileResponse|Response
    {
        if (Guid::hex($userId) === null || ! preg_match('/^[A-Za-z0-9._-]+\.webp$/', $fileName)) {
            return response('Not found.', 404);
        }

        $path = $this->dataDir().'/users/'.Guid::dashed($userId).'/'.$fileName;

        return $this->file($path, 'image/webp');
    }

    private function file(string $path, string $type): BinaryFileResponse|Response
    {
        $real = realpath($path);
        $root = realpath($this->dataDir());
        if ($real === false || $root === false || ! str_starts_with($real, $root.DIRECTORY_SEPARATOR)) {
            return response('Not found.', 404);
        }

        return response()->file($real, ['Content-Type' => $type]);
    }

    private function dataDir(): string
    {
        return (string) config('mealie.data_dir');
    }
}
