<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\Images;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

final class HouseholdService
{
    /**
     * @return array<string, mixed>
     */
    public function timeline(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('recipe_timeline_events')
            ->join('recipes', 'recipes.id', '=', 'recipe_timeline_events.recipe_id')
            ->where('recipes.group_id', $user->group_id)
            ->select('recipe_timeline_events.*');
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('timestamp', 'desc')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->event($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function createTimeline(object $user, array $payload): ?array
    {
        $recipeId = Guid::hex($payload['recipeId'] ?? $payload['recipe_id'] ?? null);
        $recipe = $recipeId ? MealieDb::table('recipes')->where('id', $recipeId)->where('group_id', $user->group_id)->first() : null;
        if ($recipe === null) {
            return null;
        }
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('recipe_timeline_events')->insert([
            'id' => $id,
            'recipe_id' => $recipeId,
            'user_id' => $user->id,
            'subject' => $payload['subject'] ?? '',
            'message' => $payload['eventMessage'] ?? $payload['message'] ?? '',
            'event_type' => $payload['eventType'] ?? $payload['event_type'] ?? 'info',
            'image' => 'does not have image',
            'timestamp' => $payload['timestamp'] ?? $now,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->event(MealieDb::table('recipe_timeline_events')->where('id', $id)->first());
    }

    /**
     * @return array<string, mixed>
     */
    public function webhooks(object $user, Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('webhook_urls')->where('household_id', $user->household_id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->webhook($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createWebhook(object $user, array $payload): array
    {
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('webhook_urls')->insert([
            'id' => $id,
            'group_id' => $user->group_id,
            'household_id' => $user->household_id,
            'enabled' => JsonShape::bool($payload['enabled'] ?? true) ? 1 : 0,
            'name' => $payload['name'] ?? '',
            'url' => $payload['url'] ?? '',
            'webhook_type' => $payload['webhookType'] ?? $payload['webhook_type'] ?? 'mealplan',
            'scheduled_time' => $this->clock($payload['scheduledTime'] ?? $payload['scheduled_time'] ?? '00:00:00'),
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->webhook(MealieDb::table('webhook_urls')->where('id', $id)->first());
    }

    /**
     * @return array<string, mixed>|null
     */
    public function webhookOne(object $user, string $id): ?array
    {
        $row = $this->ownedWebhook($user, $id);

        return $row === null ? null : $this->webhook($row);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateWebhook(object $user, string $id, array $payload): ?array
    {
        $row = $this->ownedWebhook($user, $id);
        if ($row === null) {
            return null;
        }
        MealieDb::table('webhook_urls')->where('id', $row->id)->update([
            'name' => (string) ($payload['name'] ?? $row->name),
            'url' => (string) ($payload['url'] ?? $row->url),
            'enabled' => array_key_exists('enabled', $payload) ? (JsonShape::bool($payload['enabled']) ? 1 : 0) : $row->enabled,
            'webhook_type' => (string) ($payload['webhookType'] ?? $payload['webhook_type'] ?? $row->webhook_type),
            'scheduled_time' => $this->clock($payload['scheduledTime'] ?? $payload['scheduled_time'] ?? $row->scheduled_time),
            'update_at' => MealieDb::now(),
        ]);

        return $this->webhook(MealieDb::table('webhook_urls')->where('id', $row->id)->first());
    }

    public function testWebhook(object $user, string $id): bool
    {
        $row = $this->ownedWebhook($user, $id);
        if ($row === null || ! is_string($row->url) || $row->url === '') {
            return false;
        }
        try {
            $response = Http::timeout(5)->post($row->url, [
                'title' => 'Mealie test',
                'body' => 'Webhook test from the PHP backend',
            ]);

            return $response->successful();
        } catch (\Throwable) {
            return false;
        }
    }

    /**
     * @return array<string, mixed>|null
     */
    public function updateTimeline(object $user, string $id, array $payload): ?array
    {
        $row = $this->ownedEvent($user, $id);
        if ($row === null) {
            return null;
        }
        MealieDb::table('recipe_timeline_events')->where('id', $row->id)->update([
            'subject' => (string) ($payload['subject'] ?? $row->subject),
            'message' => (string) ($payload['eventMessage'] ?? $payload['message'] ?? $row->message),
            'event_type' => (string) ($payload['eventType'] ?? $payload['event_type'] ?? $row->event_type),
            'timestamp' => $payload['timestamp'] ?? $row->timestamp,
            'update_at' => MealieDb::now(),
        ]);

        return $this->event(MealieDb::table('recipe_timeline_events')->where('id', $row->id)->first());
    }

    /**
     * @return array<string, mixed>|null
     */
    public function saveTimelineImage(object $user, string $id, string $bytes): ?array
    {
        $row = $this->ownedEvent($user, $id);
        if ($row === null || $bytes === '') {
            return null;
        }
        $dir = rtrim((string) config('mealie.data_dir'), '/').'/recipes/'.Guid::dashed($row->recipe_id).'/images/timeline/'.Guid::dashed($row->id);
        Images::writeSet($dir, $bytes);
        MealieDb::table('recipe_timeline_events')->where('id', $row->id)->update([
            'image' => 'timeline',
            'update_at' => MealieDb::now(),
        ]);

        return $this->event(MealieDb::table('recipe_timeline_events')->where('id', $row->id)->first());
    }

    public function deleteTimeline(object $user, string $id): bool
    {
        $row = $this->ownedEvent($user, $id);
        if ($row === null) {
            return false;
        }

        return MealieDb::table('recipe_timeline_events')->where('id', $row->id)->delete() > 0;
    }

    public function deleteWebhook(object $user, string $id): bool
    {
        $hex = Guid::hex($id);

        return $hex !== null && MealieDb::table('webhook_urls')->where('id', $hex)->where('household_id', $user->household_id)->delete() > 0;
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function invitations(object $user): array
    {
        return MealieDb::table('invite_tokens')->where('household_id', $user->household_id)->get()
            ->map(fn ($row) => [
                'token' => $row->token,
                'usesLeft' => (int) $row->uses_left,
                'groupId' => Guid::dashed($row->group_id),
                'householdId' => Guid::dashed($row->household_id),
            ])->all();
    }

    /**
     * @return array<string, mixed>
     */
    public function createInvitation(object $user, int $uses): array
    {
        $now = MealieDb::now();
        $id = MealieDb::table('invite_tokens')->insertGetId([
            'token' => bin2hex(random_bytes(16)),
            'uses_left' => max(1, $uses),
            'group_id' => $user->group_id,
            'household_id' => $user->household_id,
            'created_at' => $now,
            'update_at' => $now,
        ]);
        $row = MealieDb::table('invite_tokens')->where('id', $id)->first();

        return [
            'token' => $row->token,
            'usesLeft' => (int) $row->uses_left,
            'groupId' => Guid::dashed($row->group_id),
            'householdId' => Guid::dashed($row->household_id),
        ];
    }

    private function ownedWebhook(object $user, string $id): ?object
    {
        $hex = Guid::hex($id);

        return $hex === null ? null : MealieDb::table('webhook_urls')->where('id', $hex)->where('household_id', $user->household_id)->first();
    }

    private function ownedEvent(object $user, string $id): ?object
    {
        $hex = Guid::hex($id);
        if ($hex === null) {
            return null;
        }
        $row = MealieDb::table('recipe_timeline_events')->where('id', $hex)->first();
        if ($row === null) {
            return null;
        }
        $recipe = MealieDb::table('recipes')->where('id', $row->recipe_id)->where('group_id', $user->group_id)->first();

        return $recipe === null ? null : $row;
    }

    private function clock(mixed $value): string
    {
        $time = substr((string) $value, 0, 8);

        return strlen($time) === 5 ? $time.':00' : $time;
    }

    /**
     * @return array<string, mixed>
     */
    private function event(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'recipeId' => Guid::dashed($row->recipe_id),
            'userId' => Guid::dashed($row->user_id),
            'subject' => $row->subject,
            'eventMessage' => $row->message,
            'eventType' => $row->event_type,
            'image' => $row->image,
            'timestamp' => JsonShape::dateTime($row->timestamp),
            'createdAt' => JsonShape::dateTime($row->created_at),
            'updatedAt' => JsonShape::dateTime($row->update_at),
        ];
    }

    /**
     * @return array<string, mixed>
     */
    private function webhook(object $row): array
    {
        return [
            'id' => Guid::dashed($row->id),
            'enabled' => JsonShape::bool($row->enabled),
            'name' => $row->name,
            'url' => $row->url,
            'webhookType' => $row->webhook_type,
            'scheduledTime' => $row->scheduled_time,
            'groupId' => Guid::dashed($row->group_id),
            'householdId' => Guid::dashed($row->household_id),
        ];
    }
}
