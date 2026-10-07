<?php

namespace App\Areas\Households\Controllers;

use App\Auth\Jwt;
use App\Support\Errors;
use App\Support\Guid;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\BinaryFileResponse;
use Symfony\Component\Mime\MimeTypes;

/** mealie/routes/media/*.py and mealie/routes/utility_routes.py (public file routes) */
class MediaController
{
    private const IMAGE_TYPES = ['original.webp', 'min-original.webp', 'tiny-original.webp'];

    private static function dataDir(): string
    {
        return rtrim((string) config('mealie.data_dir'), '/');
    }

    private static function imageType(string $fileName): string
    {
        if (! in_array($fileName, self::IMAGE_TYPES, true)) {
            Errors::validation("Input should be 'original.webp', 'min-original.webp' or 'tiny-original.webp' at path.file_name");
        }

        return $fileName;
    }

    /** pathlib resolve() without requiring existence: normalise "." and ".." segments. */
    private static function normalize(string $path): string
    {
        $parts = [];
        foreach (explode('/', $path) as $seg) {
            if ($seg === '' || $seg === '.') {
                continue;
            }
            if ($seg === '..') {
                array_pop($parts);

                continue;
            }
            $parts[] = $seg;
        }
        $joined = '/'.implode('/', $parts);
        $real = realpath($joined);

        return $real !== false ? $real : $joined;
    }

    private static function isRelativeTo(string $path, string $base): bool
    {
        return $path === $base || str_starts_with($path, rtrim($base, '/').'/');
    }

    private static function webp(string $file): BinaryFileResponse
    {
        return response()->file($file, ['Content-Type' => 'image/webp']);
    }

    /** GET /media/recipes/{recipe_id}/images/{file_name} */
    public function recipeImage(string $recipeId, string $fileName)
    {
        $id = Guid::fromDb(Guid::requireUuid4($recipeId));
        $file = self::dataDir()."/recipes/{$id}/images/".self::imageType($fileName);
        if (! file_exists($file)) {
            Errors::http(404, 'Not Found');
        }

        return self::webp($file);
    }

    /** GET /media/recipes/{recipe_id}/images/timeline/{timeline_event_id}/{file_name} */
    public function timelineImage(string $recipeId, string $eventId, string $fileName)
    {
        $id = Guid::fromDb(Guid::requireUuid4($recipeId));
        $event = Guid::fromDb(Guid::requireUuid4($eventId));
        $file = self::dataDir()."/recipes/{$id}/images/timeline/{$event}/".self::imageType($fileName);
        if (! file_exists($file)) {
            Errors::http(404, 'Not Found');
        }

        return self::webp($file);
    }

    /** GET /media/recipes/{recipe_id}/assets/{file_name} */
    public function recipeAsset(string $recipeId, string $fileName)
    {
        $id = Guid::fromDb(Guid::requireUuid4($recipeId));
        $assetDir = self::normalize(self::dataDir()."/recipes/{$id}/assets");
        $file = self::normalize($assetDir.'/'.$fileName);
        if (! self::isRelativeTo($file, $assetDir)) {
            Errors::http(400, 'Bad Request');
        }
        if (! file_exists($file)) {
            Errors::http(404, 'Not Found');
        }

        $type = MimeTypes::getDefault()->getMimeTypes(pathinfo($file, PATHINFO_EXTENSION))[0] ?? 'text/plain';
        $response = response()->file($file, ['Content-Type' => $type, 'X-Content-Type-Options' => 'nosniff']);
        $response->headers->set('Content-Disposition', self::attachment(basename($file)));

        return $response;
    }

    /** GET /media/users/{user_id}/{file_name} */
    public function userImage(string $userId, string $fileName)
    {
        $id = Guid::fromDb(Guid::requireUuid4($userId));
        $userDir = self::normalize(self::dataDir()."/users/{$id}");
        $file = self::normalize($userDir.'/'.$fileName);
        if (! self::isRelativeTo($file, $userDir)) {
            Errors::http(400, 'Bad Request');
        }
        if (! file_exists($file)) {
            Errors::http(404, 'Not Found');
        }

        return self::webp($file);
    }

    /** GET /media/docker/validate.txt */
    public function dockerValidate()
    {
        $file = self::dataDir().'/docker-validation/validate.txt';
        if (! file_exists($file)) {
            Errors::http(404, 'File not found');
        }

        return response()->file($file, ['Content-Type' => 'text/plain; charset=utf-8']);
    }

    /** GET /utils/download?token= — validate_file_token + allowed dirs */
    public function download(Request $request)
    {
        $token = $request->query('token');
        if ($token === null || $token === '') {
            Errors::http(400, 'Bad Request');
        }
        $claims = Jwt::decode((string) $token, Jwt::secret());
        if ($claims === null || ! array_key_exists('file', $claims) || ! is_string($claims['file'])) {
            Errors::http(401, 'could not validate file token');
        }
        $path = $claims['file'];
        if ($path === '' || ! file_exists($path)) {
            Errors::http(400, 'Bad Request');
        }

        $path = self::normalize(str_starts_with($path, '/') ? $path : getcwd().'/'.$path);
        $allowed = [self::normalize(self::dataDir().'/backups'), self::normalize(self::dataDir().'/groups')];
        $ok = false;
        foreach ($allowed as $dir) {
            $ok = $ok || self::isRelativeTo($path, $dir);
        }
        if (! $ok || ! is_file($path)) {
            Errors::http(400, 'Bad Request');
        }

        return response()->file($path, [
            'Content-Type' => 'application/octet-stream',
            'Content-Disposition' => self::attachment(basename($path)),
        ]);
    }

    /** Starlette FileResponse content-disposition */
    private static function attachment(string $name): string
    {
        $quoted = rawurlencode($name);

        return $quoted !== $name
            ? "attachment; filename*=utf-8''{$quoted}"
            : "attachment; filename=\"{$name}\"";
    }
}
