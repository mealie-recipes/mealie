<?php

namespace App\Areas\AuthUsers\Http;

use App\Areas\AuthUsers\Support\Pyd;
use App\Areas\AuthUsers\Support\Users;
use App\Support\Json;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

/** mealie/routes/validators/validators.py — ValidationResponse {"valid": bool} */
class ValidatorsController
{
    /** GET /validators/user/name (line 14) */
    public function userName(Request $request): JsonResponse
    {
        $v = new Pyd('validators/validators.py', 14, 'validate_user', 'GET', '/api/validators/user/name');
        $name = $v->queryStr($request, 'name');
        $v->done();

        $exists = Users::db()->table('users')->whereRaw('lower(username) = ?', [mb_strtolower($name)])->exists();

        return Json::respond(['valid' => ! $exists]);
    }

    /** GET /validators/user/email (line 22) */
    public function userEmail(Request $request): JsonResponse
    {
        $v = new Pyd('validators/validators.py', 22, 'validate_user_email', 'GET', '/api/validators/user/email');
        $email = $v->queryStr($request, 'email');
        $v->done();

        $exists = Users::db()->table('users')->whereRaw('lower(email) = ?', [mb_strtolower($email)])->exists();

        return Json::respond(['valid' => ! $exists]);
    }

    /** GET /validators/group (line 30) */
    public function group(Request $request): JsonResponse
    {
        $v = new Pyd('validators/validators.py', 30, 'validate_group', 'GET', '/api/validators/group');
        $name = $v->queryStr($request, 'name');
        $v->done();

        return Json::respond(['valid' => ! Users::db()->table('groups')->where('name', $name)->exists()]);
    }

    /**
     * GET /validators/household (line 38). The Python handler builds the repositories with group_id=None and
     * RepositoryHousehold.get_by_name raises "group_id not set" (repository_household.py:70), so every request
     * that passes query validation ends in an unhandled 500.
     */
    public function household(Request $request)
    {
        $v = new Pyd('validators/validators.py', 38, 'validate_household', 'GET', '/api/validators/household');
        $v->queryStr($request, 'name');
        $v->done();

        return response('Internal Server Error', 500, ['Content-Type' => 'text/plain; charset=utf-8']);
    }

    /** GET /validators/recipe (line 46) */
    public function recipe(Request $request): JsonResponse
    {
        $v = new Pyd('validators/validators.py', 46, 'validate_recipe', 'GET', '/api/validators/recipe');
        $groupRaw = Pyd::queryParam($request, 'group_id');
        $groupId = null;
        if ($groupRaw === null) {
            $v->add('missing', ['query', 'group_id'], 'Field required', null);
        } else {
            $groupId = $v->uuid('query', 'group_id', $groupRaw, null);
        }
        $name = $v->queryStr($request, 'name');
        $v->done();

        $exists = Users::db()->table('recipes')->where('group_id', $groupId)->where('slug', self::slugify($name))->exists();

        return Json::respond(['valid' => ! $exists]);
    }

    /** python-slugify defaults (lowercase, "-" separator, unidecode). */
    public static function slugify(string $text): string
    {
        $text = html_entity_decode($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
        $text = Str::ascii($text);
        $text = strtolower($text);
        $text = preg_replace("/'+/", '', $text);
        $text = preg_replace('/(?<=\d),(?=\d)/', '', $text);
        $text = preg_replace('/[^-a-z0-9]+/', '-', $text);
        $text = preg_replace('/-{2,}/', '-', $text);

        return trim($text, '-');
    }
}
