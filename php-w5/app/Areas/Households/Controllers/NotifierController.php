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

/** mealie/routes/households/controller_group_notifications.py (GroupEventNotifierOut, household-scoped repo) */
class NotifierController
{
    private const GENERIC = 'An unexpected error occurred';

    private function query()
    {
        return Out::db()->table('group_events_notifiers')
            ->where('group_id', CurrentUser::groupId())->where('household_id', CurrentUser::householdId());
    }

    /** GroupEventNotifierOptions body (all bools default False); test_message/webhook_task have no column */
    private function parseOptions(array $data): array
    {
        $raw = Input::raw($data, 'options');
        if ($raw === Input::MISSING) {
            $raw = [];
        }
        if (! is_array($raw) || (array_is_list($raw) && $raw !== [])) {
            Errors::validation('Input should be a valid dictionary or object to extract fields from at body.options');
        }
        $out = [];
        foreach (Out::NOTIFIER_OPTIONS as $key) {
            $v = Input::bool($raw, $key, false);
            if (! in_array($key, ['test_message', 'webhook_task'], true)) {
                $out[$key] = $v;
            }
        }

        return $out;
    }

    private function insertOptions(string $notifierId, array $options): void
    {
        $now = Dates::nowDb();
        Out::db()->table('group_events_notifier_options')->insert($options + [
            'id' => Guid::new(),
            'event_notifier_id' => $notifierId,
            'created_at' => $now,
            'update_at' => $now,
        ]);
    }

    public function index(Request $request)
    {
        return Json::respond(Paginator::page(
            $request, $this->query(), fn ($r) => Out::notifier($r), 'group_events_notifiers',
            ['id', 'name', 'enabled', 'apprise_url', 'group_id', 'household_id', 'created_at', 'update_at'],
            ['name', 'apprise_url'], '/households/events/notifications',
        ));
    }

    public function store(Request $request)
    {
        $data = Input::object($request);
        $name = Input::str($data, 'name');
        $url = Input::str($data, 'apprise_url', null, true);

        $id = Guid::new();
        $now = Dates::nowDb();

        if ($url === null) {
            // NOT NULL apprise_url -> IntegrityError in HttpRepo.create_one -> 409 (registered message)
            $params = "('{$id}', ".var_export($name, true).', 1, None, '
                ."'".CurrentUser::groupId()."', '".CurrentUser::householdId()."', '{$now}', '{$now}')";
            Errors::http(409, ['message' => 'Database integrity error', 'error' => true, 'exception' => "(sqlite3.IntegrityError) NOT NULL constraint failed: group_events_notifiers.apprise_url\n"
                .'[SQL: INSERT INTO group_events_notifiers (id, name, enabled, apprise_url, group_id, household_id, created_at, update_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)]'."\n"
                ."[parameters: {$params}]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)"]);
        }

        Out::db()->table('group_events_notifiers')->insert([
            'id' => $id,
            'name' => $name,
            'enabled' => true,
            'apprise_url' => $url,
            'group_id' => CurrentUser::groupId(),
            'household_id' => CurrentUser::householdId(),
            'created_at' => $now,
            'update_at' => $now,
        ]);
        $this->insertOptions($id, array_fill_keys(array_diff(Out::NOTIFIER_OPTIONS, ['test_message', 'webhook_task']), false));

        return Json::respond(Out::notifier(Out::db()->table('group_events_notifiers')->where('id', $id)->first()), 201);
    }

    public function show(string $itemId)
    {
        $row = $this->query()->where('id', Guid::requireUuid4($itemId))->first();
        if (! $row) {
            Http::notFound();
        }

        return Json::respond(Out::notifier($row));
    }

    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $data = Input::object($request);
        $name = Input::str($data, 'name');
        $url = Input::str($data, 'apprise_url', null, true);
        $enabled = Input::bool($data, 'enabled', true);
        $groupId = Input::uuid($data, 'group_id');
        $householdId = Input::uuid($data, 'household_id');
        $options = $this->parseOptions($data);
        Input::uuid($data, 'id');

        $row = $this->query()->where('id', $id)->first();
        if (! $row) {
            if ($url === null) {
                // current_data is None -> AttributeError, unhandled
                return response('Internal Server Error', 500, ['Content-Type' => 'text/plain; charset=utf-8']);
            }
            Http::notFound();
        }
        $url ??= $row->apprise_url;

        $db = Out::db();
        $db->table('group_events_notifiers')->where('id', $id)->update([
            'name' => $name,
            'apprise_url' => $url,
            'enabled' => $enabled,
            'group_id' => $groupId,
            'household_id' => $householdId,
            'update_at' => Dates::nowDb(),
        ]);
        // auto_init builds a new options row; the old one is deleted as an orphan
        $db->table('group_events_notifier_options')->where('event_notifier_id', $id)->delete();
        $this->insertOptions($id, $options);

        return Json::respond(Out::notifier($db->table('group_events_notifiers')->where('id', $id)->first()));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $row = $this->query()->where('id', $id)->first();
        if (! $row) {
            Http::deleteNotFound(self::GENERIC);
        }
        Out::db()->table('group_events_notifier_options')->where('event_notifier_id', $id)->delete();
        Out::db()->table('group_events_notifiers')->where('id', $id)->delete();

        return response()->noContent();
    }
}
