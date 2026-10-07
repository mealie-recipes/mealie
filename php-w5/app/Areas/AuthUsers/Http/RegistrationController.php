<?php

namespace App\Areas\AuthUsers\Http;

use App\Areas\AuthUsers\Support\Pyd;
use App\Areas\AuthUsers\Support\RawRepr;
use App\Areas\AuthUsers\Support\Settings;
use App\Areas\AuthUsers\Support\Translator;
use App\Areas\AuthUsers\Support\Users;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** mealie/routes/users/registration.py + services/user_services/registration_service.py */
class RegistrationController
{
    private const LOCALES = [
        'af-ZA', 'ar-SA', 'bg-BG', 'ca-ES', 'cs-CZ', 'da-DK', 'de-DE', 'el-GR', 'en-GB', 'en-US', 'es-ES', 'et-EE',
        'fi-FI', 'fr-BE', 'fr-CA', 'fr-FR', 'gl-ES', 'he-IL', 'hr-HR', 'hu-HU', 'is-IS', 'it-IT', 'ja-JP', 'ko-KR',
        'lt-LT', 'lv-LV', 'nl-NL', 'no-NO', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'sk-SK', 'sl-SI', 'sr-SP',
        'sv-SE', 'tr-TR', 'uk-UA', 'vi-VN', 'zh-CN', 'zh-TW',
    ];

    /** POST /users/register (registration.py:20) */
    public function register(Request $request): JsonResponse
    {
        $v = new Pyd('users/registration.py', 20, 'register_new_user', 'POST', '/api/users/register');
        $body = $v->bodyObject($request);
        $data = null;
        if ($body !== null) {
            $data = $this->validate($v, $body);
        }
        $v->done();

        if ((! Settings::allowSignup() && $data['group_token'] === null) || $data['group_token'] === '') {
            Errors::errorResponse(403, 'User Registration is Disabled');
        }

        $db = Users::db();
        if ($db->table('users')->where('username', $data['username'])->exists()) {
            Errors::http(409, ['message' => Translator::t($request, 'exceptions.username-conflict-error')]);
        }
        if ($db->table('users')->where('email', $data['email'])->exists()) {
            Errors::http(409, ['message' => Translator::t($request, 'exceptions.email-conflict-error')]);
        }

        if (! $data['group_token']) {
            if (! $data['group']) {
                Errors::http(400, ['message' => 'Missing group']);
            }
            // Creating a new group (GroupService.create_group + seeding) is not implemented.
            Errors::http(501, 'Registering a new group is not implemented');
        }

        $token = $db->table('invite_tokens')->where('token', $data['group_token'])->first();
        $group = $token?->group_id ? $db->table('groups')->where('id', $token->group_id)->first() : null;
        $household = $token?->household_id ? $db->table('households')->where('id', $token->household_id)->first() : null;
        if ($token === null || $group === null || $household === null) {
            Errors::http(400, ['message' => 'Invalid group token']);
        }

        $id = Guid::new();
        $now = Dates::nowDb();
        $db->transaction(function () use ($db, $data, $id, $now, $group, $household, $token) {
            $db->table('users')->insert([
                'created_at' => $now,
                'update_at' => $now,
                'id' => $id,
                'full_name' => $data['full_name'],
                'username' => $data['username'],
                'email' => $data['email'],
                'password' => Users::hashPassword($data['password']),
                'admin' => 0,
                'advanced' => $data['advanced'] ? 1 : 0,
                'group_id' => $group->id,
                'cache_key' => '1234',
                'can_manage' => 0,
                'can_invite' => 0,
                'can_organize' => 0,
                'owned_recipes_id' => null,
                'login_attemps' => 0,
                'locked_at' => null,
                'auth_method' => 'MEALIE',
                'household_id' => $household->id,
                'can_manage_household' => 0,
                'show_announcements' => 1,
                'last_read_announcement' => null,
                'tokens_valid_after' => null,
                'external_avatar_hash' => null,
            ]);

            $usesLeft = (int) $token->uses_left - 1;
            if ($usesLeft === 0) {
                $db->table('invite_tokens')->where('id', $token->id)->delete();
            } else {
                $db->table('invite_tokens')->where('id', $token->id)->update(['uses_left' => $usesLeft, 'update_at' => $now]);
            }
        });

        // RepositoryUsers.create: copy a random profile image into the user's directory
        $dir = rtrim((string) config('mealie.data_dir'), '/').'/users/'.Guid::fromDb($id);
        @mkdir($dir, 0775, true);
        $src = dirname(base_path()).'/mealie/assets/users/random_'.random_int(1, 3).'.webp';
        if (is_file($src)) {
            @copy($src, $dir.'/profile.webp');
        }

        return Json::respond(Users::out($db->table('users')->where('id', $id)->first()), 201);
    }

    /** CreateUserRegistration (mealie/schema/user/registration.py) */
    private function validate(Pyd $v, object $body): ?array
    {
        $specs = [
            ['name' => 'group', 'type' => 'str', 'nullable' => true],
            ['name' => 'household', 'type' => 'str', 'nullable' => true],
            ['name' => 'group_token', 'alias' => 'groupToken', 'type' => 'str', 'nullable' => true],
            ['name' => 'email', 'type' => 'str', 'required' => true, 'lower' => true, 'strip' => true],
            ['name' => 'username', 'type' => 'str', 'required' => true, 'lower' => true, 'strip' => true],
            ['name' => 'full_name', 'alias' => 'fullName', 'type' => 'str', 'required' => true, 'strip' => true],
            ['name' => 'password', 'type' => 'str', 'required' => true],
            ['name' => 'password_confirm', 'alias' => 'passwordConfirm', 'type' => 'str', 'required' => true],
            ['name' => 'advanced', 'type' => 'bool', 'default' => false],
            ['name' => 'private', 'type' => 'bool', 'default' => false],
            ['name' => 'seed_data', 'alias' => 'seedData', 'type' => 'bool', 'default' => false],
            ['name' => 'locale', 'type' => 'str', 'default' => 'en-US'],
        ];

        // Validate field by field so model validators run in field order with the data validated so far.
        $out = [];
        $ok = true;
        foreach ($specs as $spec) {
            $result = $v->fields($body, [$spec]);
            if ($result === null) {
                $ok = false;

                continue;
            }
            $value = $result[$spec['name']];
            $alias = $spec['alias'] ?? $spec['name'];
            if (! property_exists($body, $alias)) {
                // a validated default is reported under the field name (validate_default=True)
                $alias = $spec['name'];
            }

            if ($spec['name'] === 'group_token') {
                // group_or_token (validate_default=True)
                if (! $value && ! (array_key_exists('group', $out) ? $out['group'] : null)) {
                    $v->add('value_error', ['body', $alias], 'Value error, group or group_token must be provided', $value,
                        ['error' => new RawRepr("ValueError('group or group_token must be provided')")]);
                    $ok = false;

                    continue;
                }
            }
            if ($spec['name'] === 'password_confirm' && array_key_exists('password', $out) && $value !== $out['password']) {
                $v->add('value_error', ['body', $alias], 'Value error, passwords do not match', $value,
                    ['error' => new RawRepr("ValueError('passwords do not match')")]);
                $ok = false;

                continue;
            }
            if ($spec['name'] === 'locale' && property_exists($body, 'locale') && ! in_array($value, self::LOCALES, true)) {
                $v->add('value_error', ['body', $alias], 'Value error, invalid locale', $value,
                    ['error' => new RawRepr("ValueError('invalid locale')")]);
                $ok = false;

                continue;
            }
            $out[$spec['name']] = $value;
        }

        return $ok ? $out : null;
    }
}
