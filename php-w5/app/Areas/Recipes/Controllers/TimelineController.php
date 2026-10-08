<?php

namespace App\Areas\Recipes\Controllers;

use App\Areas\Recipes\Support\Db;
use App\Areas\Recipes\Support\Input;
use App\Areas\Recipes\Support\Map;
use App\Support\CurrentUser;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Pagination;
use Illuminate\Http\Request;

/**
 * mealie/routes/recipe/timeline_events.py (group-scoped repo through the recipe)
 */
class TimelineController extends Base
{
    private const TYPES = ['system', 'info', 'comment'];

    private const IMAGES = ['has image', 'does not have image'];

    private function find(string $id): ?object
    {
        return Map::timelineQuery($this->groupId())->where('recipe_timeline_events.id', $id)->first();
    }

    public function index(Request $request)
    {
        $query = Map::timelineQuery($this->groupId());
        $result = Pagination::page($request, $query, fn ($rows) => array_map([Map::class, 'timeline'], $rows), '/timeline/events', [
            'table' => 'recipe_timeline_events',
            'columns' => [
                'created_at' => false, 'update_at' => false, 'id' => false, 'recipe_id' => false, 'user_id' => false,
                'subject' => true, 'message' => true, 'event_type' => true, 'image' => true, 'timestamp' => false,
            ],
            'search' => null,
        ]);

        return $this->json($result);
    }

    /** `message` has the explicit alias eventMessage; populate_by_name also accepts "message". */
    private function message(Input $in): array
    {
        foreach (['eventMessage', 'message'] as $k) {
            if (array_key_exists($k, $in->data)) {
                $v = $in->data[$k];
                if ($v !== null && ! is_string($v)) {
                    $in->error('eventMessage', 'string_type', 'Input should be a valid string');

                    return [true, null];
                }

                return [true, $v];
            }
        }

        return [false, null];
    }

    private function enum(Input $in, string $field, array $allowed, bool $required, mixed $default): mixed
    {
        if (! $in->has($field)) {
            if ($required) {
                $in->error($field, 'missing', 'Field required');
            }

            return $default;
        }
        $v = $in->raw($field);
        if ($v === null && ! $required) {
            return null;
        }
        if (! in_array($v, $allowed, true)) {
            $in->error($field, 'enum', 'Input should be '.implode(' or ', array_map(fn ($a) => "'{$a}'", $allowed)));

            return $default;
        }

        return $v;
    }

    private function parseTimestamp(Input $in): ?string
    {
        if (! $in->has('timestamp')) {
            return null;
        }
        $v = $in->raw('timestamp');
        try {
            if (is_int($v) || is_float($v)) {
                $dt = (new \DateTimeImmutable('@'.$v));
            } elseif (is_string($v) && preg_match('/^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?)?(Z|[+-]\d{2}:?\d{2})?$/', $v)) {
                $dt = new \DateTimeImmutable($v, new \DateTimeZone('UTC'));
            } else {
                throw new \Exception;
            }
        } catch (\Throwable) {
            $in->error('timestamp', 'datetime_parsing', 'Input should be a valid datetime');

            return null;
        }

        return $dt->setTimezone(new \DateTimeZone('UTC'))->format('Y-m-d H:i:s.u');
    }

    public function store(Request $request)
    {
        $in = Input::fromRequest($request);
        $recipeId = $in->uuid4('recipe_id');
        $userId = $in->uuid4('user_id', false, true);
        $subject = $in->str('subject');
        $type = $this->enum($in, 'event_type', self::TYPES, true, null);
        [, $message] = $this->message($in);
        $image = $this->enum($in, 'image', self::IMAGES, false, 'does not have image');
        $timestamp = $this->parseTimestamp($in);
        $in->check();

        $userId ??= CurrentUser::id();
        $recipe = Db::table('recipes')->where('group_id', $this->groupId())->where('id', $recipeId)->first();
        if (! $recipe) {
            Errors::http(404, 'recipe not found');
        }

        $id = Guid::new();
        $now = $this->now();
        $this->write(fn () => Db::table('recipe_timeline_events')->insert([
            'created_at' => $now, 'update_at' => $this->now(), 'id' => $id, 'recipe_id' => $recipeId,
            'user_id' => $userId, 'subject' => $subject, 'message' => $message, 'event_type' => $type,
            'image' => $image, 'timestamp' => $timestamp ?? $now,
        ]), self::SERVER_ERROR_MSG, 'Database integrity error');

        return $this->crud(Map::timeline(Map::timelineQuery(null)->where('recipe_timeline_events.id', $id)->first(), false), 201);
    }

    public function show(string $item_id)
    {
        $id = Input::pathUuid4($item_id);

        return $this->crud(Map::timeline($this->find($id) ?? Errors::notFound()));
    }

    /** HttpRepo.patch_one: only fields that were set and differ from their defaults are applied. */
    public function update(Request $request, string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $in = Input::fromRequest($request);
        $subject = $in->str('subject');
        [$hasMsg, $message] = $this->message($in);
        $image = $this->enum($in, 'image', self::IMAGES, false, null);
        $in->check();
        if (! $this->find($id)) {
            Errors::notFound();
        }

        $values = ['subject' => $subject, 'update_at' => $this->now()];
        if ($hasMsg && $message !== null) {
            $values['message'] = $message;
        }
        if ($image !== null) {
            $values['image'] = $image;
        }
        Db::table('recipe_timeline_events')->where('id', $id)->update($values);

        return $this->crud(Map::timeline($this->find($id), false));
    }

    public function destroy(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $row = $this->find($id);
        if (! $row) {
            Errors::errorResponse(404, self::SERVER_ERROR_MSG, self::NO_RESULT);
        }
        $out = Map::timeline($row, false);
        Db::table('recipe_timeline_events')->where('id', $id)->delete();

        return $this->crud($out);
    }
}
