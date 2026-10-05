<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\MealieDb;

final class AiService
{
    /**
     * @return array<string, mixed>
     */
    public function settings(object $user): array
    {
        $settings = $this->ensureSettings($user);
        $providers = MealieDb::table('ai_providers')->where('settings_id', $settings->id)->orderBy('name')->get();

        return [
            'defaultProviderId' => Guid::dashed($settings->default_provider_id),
            'audioProviderId' => Guid::dashed($settings->audio_provider_id),
            'imageProviderId' => Guid::dashed($settings->image_provider_id),
            'providers' => $providers->map(fn ($row) => [
                'id' => Guid::dashed($row->id),
                'name' => $row->name,
            ])->all(),
            'aiEnabled' => $settings->default_provider_id !== null,
            'audioProviderEnabled' => $settings->audio_provider_id !== null,
            'imageProviderEnabled' => $settings->image_provider_id !== null,
        ];
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function updateSettings(object $user, array $payload): array
    {
        $settings = $this->ensureSettings($user);
        $fields = ['update_at' => MealieDb::now()];
        foreach ([
            'defaultProviderId' => 'default_provider_id',
            'audioProviderId' => 'audio_provider_id',
            'imageProviderId' => 'image_provider_id',
        ] as $key => $column) {
            if (array_key_exists($key, $payload)) {
                $fields[$column] = Guid::hex(is_string($payload[$key]) ? $payload[$key] : null);
            }
        }
        MealieDb::table('ai_provider_settings')->where('id', $settings->id)->update($fields);

        return $this->settings($user);
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function providers(object $user): array
    {
        $settings = $this->ensureSettings($user);

        return MealieDb::table('ai_providers')->where('settings_id', $settings->id)->orderBy('name')->get()
            ->map(fn ($row) => $this->providerOut($row))->all();
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createProvider(object $user, array $payload): array
    {
        $settings = $this->ensureSettings($user);
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('ai_providers')->insert([
            'id' => $id,
            'settings_id' => $settings->id,
            'name' => (string) ($payload['name'] ?? 'Provider'),
            'base_url' => $payload['baseUrl'] ?? $payload['base_url'] ?? null,
            'api_key' => (string) ($payload['apiKey'] ?? $payload['api_key'] ?? ''),
            'model' => (string) ($payload['model'] ?? ''),
            'timeout' => (int) ($payload['timeout'] ?? 30),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->providerOut(MealieDb::table('ai_providers')->where('id', $id)->first());
    }

    /**
     * @return array<string, mixed>|null
     */
    public function defaultProvider(object $user): ?object
    {
        $settings = MealieDb::table('ai_provider_settings')->where('group_id', $user->group_id)->first();
        if ($settings === null || $settings->default_provider_id === null) {
            return null;
        }

        return MealieDb::table('ai_providers')->where('id', $settings->default_provider_id)->first();
    }

    /**
     * @return array<string, mixed>|null
     */
    public function provider(object $user, string $id): ?array
    {
        $row = $this->ownedProvider($user, $id);

        return $row === null ? null : $this->providerOut($row);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateProvider(object $user, string $id, array $payload): ?array
    {
        $row = $this->ownedProvider($user, $id);
        if ($row === null) {
            return null;
        }
        $fields = [
            'name' => (string) ($payload['name'] ?? $row->name),
            'base_url' => $payload['baseUrl'] ?? $payload['base_url'] ?? $row->base_url,
            'model' => (string) ($payload['model'] ?? $row->model),
            'timeout' => (int) ($payload['timeout'] ?? $row->timeout),
            'update_at' => MealieDb::now(),
        ];
        $key = $payload['apiKey'] ?? $payload['api_key'] ?? null;
        if (is_string($key) && $key !== '') {
            $fields['api_key'] = $key;
        }
        MealieDb::table('ai_providers')->where('id', $row->id)->update($fields);

        return $this->providerOut(MealieDb::table('ai_providers')->where('id', $row->id)->first());
    }

    public function deleteProvider(object $user, string $id): bool
    {
        $row = $this->ownedProvider($user, $id);
        if ($row === null) {
            return false;
        }
        foreach (['default_provider_id', 'audio_provider_id', 'image_provider_id'] as $column) {
            MealieDb::table('ai_provider_settings')->where('group_id', $user->group_id)->where($column, $row->id)->update([$column => null]);
        }

        return MealieDb::table('ai_providers')->where('id', $row->id)->delete() > 0;
    }

    private function ensureSettings(object $user): object
    {
        $existing = MealieDb::table('ai_provider_settings')->where('group_id', $user->group_id)->first();
        if ($existing !== null) {
            return $existing;
        }
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('ai_provider_settings')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return MealieDb::table('ai_provider_settings')->where('id', $id)->first();
    }

    private function ownedProvider(object $user, string $id): ?object
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $settings = MealieDb::table('ai_provider_settings')->where('group_id', $user->group_id)->first();
        if ($settings === null) {
            return null;
        }

        return MealieDb::table('ai_providers')->where('id', $hex)->where('settings_id', $settings->id)->first();
    }

    /**
     * @return array<string, mixed>
     */
    private function providerOut(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'baseUrl' => $row->base_url,
            'model' => $row->model,
            'timeout' => (int) $row->timeout,
            'settingsId' => Guid::dashed($row->settings_id),
            'requestHeaders' => new \stdClass,
            'requestParams' => new \stdClass,
        ];
    }
}
