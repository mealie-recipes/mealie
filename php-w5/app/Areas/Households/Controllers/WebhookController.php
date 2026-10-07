<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Http;
use App\Areas\Households\Support\Input;
use App\Areas\Households\Support\Out;
use App\Areas\Households\Support\Paginator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/households/controller_webhooks.py (CRUD only; rerun/test fire webhooks) */
class WebhookController
{
    private function query()
    {
        return Out::db()->table('webhook_urls')
            ->where('group_id', CurrentUser::groupId())->where('household_id', CurrentUser::householdId());
    }

    /** CreateWebhook */
    private function parse(array $data): array
    {
        $enabled = Input::bool($data, 'enabled', true);
        $name = Input::str($data, 'name', '');
        $url = Input::str($data, 'url', '');
        $type = Input::enum($data, 'webhook_type', ['mealplan'], 'mealplan');
        $raw = Input::raw($data, 'scheduled_time');
        if ($raw === Input::MISSING) {
            Errors::validation('Field required at body.scheduledTime');
        }
        $time = is_string($raw) ? self::parseTime($raw) : null;
        if ($time === null) {
            Errors::validation('Value error, Invalid scheduled time: '.(is_scalar($raw) ? $raw : json_encode($raw)).' at body.scheduledTime');
        }

        return ['enabled' => $enabled, 'name' => $name, 'url' => $url, 'webhook_type' => $type, 'scheduled_time' => $time];
    }

    /**
     * CreateWebhook.validate_scheduled_time: datetime -> converted to UTC time; plain time -> as is.
     * Returns the SQLite TIME storage form "HH:MM:SS.ffffff".
     */
    public static function parseTime(string $v): ?string
    {
        $v = trim($v);
        if (preg_match('/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}(:?\d{2})?)?$/', $v)) {
            try {
                $dt = new \DateTimeImmutable($v);
            } catch (\Exception) {
                return null;
            }

            return $dt->setTimezone(new \DateTimeZone('UTC'))->format('H:i:s.u');
        }
        if (preg_match('/^(\d{2}):?(\d{2})(?::?(\d{2})(?:[.,](\d+))?)?$/', $v, $m)) {
            [$h, $i, $s] = [(int) $m[1], (int) $m[2], (int) ($m[3] ?? 0)];
            if ($h > 23 || $i > 59 || $s > 59) {
                return null;
            }
            $frac = substr(str_pad($m[4] ?? '', 6, '0'), 0, 6);

            return sprintf('%02d:%02d:%02d.%s', $h, $i, $s, $frac);
        }

        return null;
    }

    public function index(Request $request)
    {
        return Json::respond(Paginator::page(
            $request, $this->query(), fn ($r) => Out::webhook($r), 'webhook_urls',
            ['id', 'group_id', 'household_id', 'enabled', 'name', 'url', 'time', 'webhook_type', 'scheduled_time', 'created_at', 'update_at'],
            ['name', 'url', 'time', 'webhook_type'], '/households/webhooks',
        ));
    }

    public function store(Request $request)
    {
        $values = $this->parse(Input::object($request));
        $id = Guid::new();
        $now = Dates::nowDb();
        Out::db()->table('webhook_urls')->insert($values + [
            'id' => $id,
            'group_id' => CurrentUser::groupId(),
            'household_id' => CurrentUser::householdId(),
            'time' => '00:00',
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return Json::respond(Out::webhook(Out::db()->table('webhook_urls')->where('id', $id)->first()), 201);
    }

    public function show(string $itemId)
    {
        $row = $this->query()->where('id', Guid::requireUuid4($itemId))->first();
        if (! $row) {
            Http::notFound();
        }

        return Json::respond(Out::webhook($row));
    }

    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $values = $this->parse(Input::object($request));
        if (! $this->query()->where('id', $id)->exists()) {
            Http::notFound();
        }
        Out::db()->table('webhook_urls')->where('id', $id)->update($values + ['update_at' => Dates::nowDb()]);

        return Json::respond(Out::webhook(Out::db()->table('webhook_urls')->where('id', $id)->first()));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $row = $this->query()->where('id', $id)->first();
        if (! $row) {
            Http::deleteNotFound('An unexpected error occurred.');
        }
        Out::db()->table('webhook_urls')->where('id', $id)->delete();

        return Json::respond(Out::webhook($row));
    }
}
