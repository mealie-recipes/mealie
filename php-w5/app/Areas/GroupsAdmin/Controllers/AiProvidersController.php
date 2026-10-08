<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Checks;
use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Out;
use App\Areas\GroupsAdmin\Support\Validator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Database\QueryException;
use Illuminate\Http\Request;

/**
 * mealie/routes/groups/controller_group_ai_providers.py (group, can_manage) and
 * mealie/routes/admin/admin_management_ai_providers.py (admin, group from the path);
 * repository logic from mealie/repos/repository_ai_provider.py.
 */
class AiProvidersController
{
    /** HttpRepo without exception_msgs uses this default message. */
    private const DEFAULT_MESSAGE = 'An unexpected error occurred.';

    // ------------------------------------------------------------ settings (group only)

    public function settings()
    {
        Checks::canManage();

        return Json::respond(Out::aiSettings(CurrentUser::groupId()));
    }

    public function updateSettings(Request $request)
    {
        $v = Validator::body($request);
        $ids = [];
        foreach (['default_provider_id', 'audio_provider_id', 'image_provider_id'] as $field) {
            $ids[$field] = $v->uuid($field, true, true, true, true);
        }
        $v->check();

        Checks::canManage();

        $groupId = CurrentUser::groupId();
        $row = Db::table('ai_provider_settings')->where('group_id', $groupId)->first();
        if ($row === null) {
            Checks::noResult(self::DEFAULT_MESSAGE);
        }
        Db::table('ai_provider_settings')->where('id', $row->id)->update($ids + ['update_at' => Dates::nowDb()]);

        return Json::respond(Out::aiSettings($groupId));
    }

    // ------------------------------------------------------------ providers

    /** AIProviderCreate / AIProviderUpdate */
    private function validated(Request $request): array
    {
        $v = Validator::body($request);
        $name = $v->str('name');
        if ($name === '') {
            $v->custom('name', 'name cannot be empty');
        }
        [$hasBase, $base] = $v->raw('base_url');
        if ($hasBase && ! $base) {
            $base = null;
        } elseif ($hasBase && ! is_string($base)) {
            $v->error('base_url', 'string_type', 'Input should be a valid string');
        }
        $apiKey = $v->str('api_key', false, '');
        if ($v->has('api_key') && $apiKey === '') {
            $v->custom('api_key', 'api_key cannot be empty');
        }
        $model = $v->str('model');
        if ($model === '') {
            $v->custom('model', 'model cannot be empty');
        }
        $timeout = $v->int('timeout', false, 300);
        if ($timeout !== null && $timeout < 0) {
            $v->custom('timeout', 'timeout cannot be less than zero');
        }
        $headers = $v->strDict('request_headers');
        $params = $v->strDict('request_params');
        $v->check();

        return [
            'name' => $name,
            'base_url' => $hasBase ? $base : null,
            'api_key' => $apiKey,
            'model' => $model,
            'timeout' => $timeout,
            'headers' => $headers,
            'params' => $params,
        ];
    }

    private function query(string $groupId)
    {
        return Db::table('ai_providers')
            ->join('ai_provider_settings', 'ai_provider_settings.id', '=', 'ai_providers.settings_id')
            ->where('ai_provider_settings.group_id', $groupId)
            ->select('ai_providers.*');
    }

    private function find(string $groupId, string $id): ?object
    {
        return $this->query($groupId)->where('ai_providers.id', $id)->first();
    }

    /** AIProviderOut.model_validate runs the non-empty validators on stored rows too. */
    private static function storedValid(object $p): bool
    {
        return $p->name !== '' && $p->api_key !== '' && $p->model !== '' && (int) $p->timeout >= 0;
    }

    /** repo.get_one: a row that fails validation raises outside any handler (500). */
    private function findValid(string $groupId, string $id): ?object
    {
        $p = $this->find($groupId, $id);
        if ($p !== null && ! self::storedValid($p)) {
            Errors::http(500, 'Internal Server Error');
        }

        return $p;
    }

    private function writeKv(string $providerId, array $headers, array $params, string $now): void
    {
        foreach (['ai_provider_headers' => $headers, 'ai_provider_params' => $params] as $table => $values) {
            Db::table($table)->where('provider_id', $providerId)->delete();
            foreach ($values as $key => $value) {
                Db::table($table)->insert([
                    'provider_id' => $providerId, 'key_name' => (string) $key, 'value' => $value,
                    'created_at' => $now, 'update_at' => $now,
                ]);
            }
        }
    }

    private function integrity(QueryException $e): never
    {
        LabelsController::integrity($e, 'An unexpected error occurred.');
    }

    private function create(Request $request, string $groupId)
    {
        $data = $this->validated($request);
        if ($data['api_key'] === '') {
            Errors::errorResponse(400, self::DEFAULT_MESSAGE, '400: API key cannot be empty');
        }
        $settings = Db::table('ai_provider_settings')->where('group_id', $groupId)->first();
        if ($settings === null) {
            Checks::noResult(self::DEFAULT_MESSAGE);
        }

        $id = Guid::new();
        $now = Dates::nowDb();
        try {
            Db::conn()->transaction(function () use ($id, $settings, $data, $now) {
                Db::table('ai_providers')->insert([
                    'id' => $id, 'settings_id' => $settings->id, 'name' => $data['name'], 'base_url' => $data['base_url'],
                    'api_key' => $data['api_key'], 'model' => $data['model'], 'timeout' => $data['timeout'],
                    'created_at' => $now, 'update_at' => $now,
                ]);
                $this->writeKv($id, $data['headers'], $data['params'], $now);
            });
        } catch (QueryException $e) {
            $this->integrity($e);
        }

        return Json::respond(Out::aiProvider($this->find($groupId, $id)));
    }

    private function show(string $groupId, string $id)
    {
        $provider = $this->findValid($groupId, $id);
        if ($provider === null) {
            Errors::notFound();
        }

        return Json::respond(Out::aiProvider($provider));
    }

    private function update(Request $request, string $groupId, string $id)
    {
        $data = $this->validated($request);
        $existing = $this->findValid($groupId, $id);
        if ($existing === null) {
            Errors::notFound();
        }
        $apiKey = $data['api_key'] !== '' ? $data['api_key'] : $existing->api_key;
        $now = Dates::nowDb();
        try {
            Db::conn()->transaction(function () use ($id, $data, $apiKey, $now) {
                Db::table('ai_providers')->where('id', $id)->update([
                    'name' => $data['name'], 'base_url' => $data['base_url'], 'api_key' => $apiKey,
                    'model' => $data['model'], 'timeout' => $data['timeout'], 'update_at' => $now,
                ]);
                $this->writeKv($id, $data['headers'], $data['params'], $now);
            });
        } catch (QueryException $e) {
            $this->integrity($e);
        }

        return Json::respond(Out::aiProvider($this->find($groupId, $id)));
    }

    private function destroy(string $groupId, string $id)
    {
        $provider = $this->find($groupId, $id);
        if ($provider === null) {
            Checks::noResult(self::DEFAULT_MESSAGE);
        }
        if (! self::storedValid($provider)) {
            // repo.delete validates before deleting; the ValidationError goes through handle_exception
            Errors::errorResponse(400, self::DEFAULT_MESSAGE, '1 validation error for AIProviderOut');
        }
        $out = Out::aiProvider($provider);
        Db::conn()->transaction(function () use ($id) {
            foreach (['default_provider_id', 'audio_provider_id', 'image_provider_id'] as $col) {
                Db::table('ai_provider_settings')->where($col, $id)->update([$col => null]);
            }
            Db::table('ai_provider_headers')->where('provider_id', $id)->delete();
            Db::table('ai_provider_params')->where('provider_id', $id)->delete();
            Db::table('ai_providers')->where('id', $id)->delete();
        });

        return Json::respond($out);
    }

    // ------------------------------------------------------------ group routes (checks.can_manage)

    public function groupCreate(Request $request)
    {
        $this->validated($request);
        Checks::canManage();

        return $this->create($request, CurrentUser::groupId());
    }

    public function groupShow(string $providerId)
    {
        $id = Guid::requireUuid4($providerId);
        Checks::canManage();

        return $this->show(CurrentUser::groupId(), $id);
    }

    public function groupUpdate(Request $request, string $providerId)
    {
        $id = Guid::requireUuid4($providerId);
        $this->validated($request);
        Checks::canManage();

        return $this->update($request, CurrentUser::groupId(), $id);
    }

    public function groupDestroy(string $providerId)
    {
        $id = Guid::requireUuid4($providerId);
        Checks::canManage();

        return $this->destroy(CurrentUser::groupId(), $id);
    }

    // ------------------------------------------------------------ admin routes (group from the path)

    public function adminCreate(Request $request, string $groupId)
    {
        return $this->create($request, Guid::requireUuid4($groupId));
    }

    public function adminShow(string $groupId, string $providerId)
    {
        $gid = Guid::requireUuid4($groupId);

        return $this->show($gid, Guid::requireUuid4($providerId));
    }

    public function adminUpdate(Request $request, string $groupId, string $providerId)
    {
        $gid = Guid::requireUuid4($groupId);

        return $this->update($request, $gid, Guid::requireUuid4($providerId));
    }

    public function adminDestroy(string $groupId, string $providerId)
    {
        $gid = Guid::requireUuid4($groupId);

        return $this->destroy($gid, Guid::requireUuid4($providerId));
    }
}
