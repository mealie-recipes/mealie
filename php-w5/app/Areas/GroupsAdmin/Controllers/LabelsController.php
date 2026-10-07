<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Checks;
use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Out;
use App\Areas\GroupsAdmin\Support\Pager;
use App\Areas\GroupsAdmin\Support\Validator;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Database\QueryException;
use Illuminate\Http\Request;

/** mealie/routes/groups/controller_labels.py, services/group_services/labels_service.py */
class LabelsController
{
    private const SERVER_ERROR = 'An unexpected error occurred';

    private function find(string $id): ?object
    {
        return Db::table('multi_purpose_labels')->where('group_id', CurrentUser::groupId())->where('id', $id)->first();
    }

    /** HttpRepo.handle_exception for an IntegrityError */
    public static function integrity(QueryException $e, string $otherMessage = 'Database integrity error'): never
    {
        $msg = $e->getMessage();
        $unique = str_contains($msg, 'UNIQUE constraint failed');
        $detail = preg_match('/((?:UNIQUE|NOT NULL) constraint failed: [^ (]+(?:, [^ (]+)*)/', $msg, $m) ? $m[1] : 'constraint failed';
        Errors::errorResponse(409, $unique ? 'This item already exists.' : $otherMessage, "(sqlite3.IntegrityError) {$detail}");
    }

    public function index(Request $request)
    {
        $query = Db::table('multi_purpose_labels')->where('multi_purpose_labels.group_id', CurrentUser::groupId());

        return Json::respond(Pager::page(
            $request, $query, 'multi_purpose_labels', 'MultiPurposeLabel',
            ['id' => false, 'name' => true, 'color' => true, 'group_id' => false],
            fn ($rows) => array_map([Out::class, 'label'], $rows),
            '/groups/labels',
            'plain', ['name'],
        ));
    }

    public function store(Request $request)
    {
        $v = Validator::body($request);
        $name = $v->str('name');
        $color = $v->str('color', false, '#959595');
        $v->check();

        $groupId = CurrentUser::groupId();
        $id = Guid::new();
        $now = Dates::nowDb();
        try {
            Db::table('multi_purpose_labels')->insert([
                'id' => $id, 'name' => $name, 'color' => $color, 'group_id' => $groupId,
                'created_at' => $now, 'update_at' => $now,
            ]);
        } catch (QueryException $e) {
            self::integrity($e);
        }

        // _update_shopping_list_label_references: add the label to every shopping list of the group
        foreach (Db::table('shopping_lists')->where('group_id', $groupId)->orderBy('created_at', 'desc')->get(['id']) as $list) {
            $position = Db::table('shopping_lists_multi_purpose_labels')->where('shopping_list_id', $list->id)->count();
            Db::table('shopping_lists_multi_purpose_labels')->insert([
                'id' => Guid::new(), 'shopping_list_id' => $list->id, 'label_id' => $id, 'position' => $position,
                'created_at' => $now, 'update_at' => $now,
            ]);
        }

        return Json::respond(Out::label($this->find($id)));
    }

    public function show(string $itemId)
    {
        $label = $this->find(Guid::requireUuid4($itemId));
        if ($label === null) {
            Checks::notFound();
        }

        return Json::respond(Out::label($label));
    }

    public function update(Request $request, string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $v = Validator::body($request);
        $name = $v->str('name');
        $color = $v->str('color', false, '#959595');
        $groupId = $v->uuid('group_id');
        $v->uuid('id');
        $v->check();

        if ($this->find($id) === null) {
            Checks::notFound();
        }
        try {
            Db::table('multi_purpose_labels')->where('id', $id)->update([
                'name' => $name, 'color' => $color, 'group_id' => $groupId, 'update_at' => Dates::nowDb(),
            ]);
        } catch (QueryException $e) {
            self::integrity($e);
        }

        return Json::respond(Out::label(Db::table('multi_purpose_labels')->where('id', $id)->first()));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        $label = $this->find($id);
        if ($label === null) {
            Checks::noResult(self::SERVER_ERROR);
        }

        Db::conn()->transaction(function () use ($id) {
            Db::table('shopping_lists_multi_purpose_labels')->where('label_id', $id)->delete();
            Db::table('ingredient_foods')->where('label_id', $id)->update(['label_id' => null]);
            Db::table('shopping_list_items')->where('label_id', $id)->update(['label_id' => null]);
            Db::table('multi_purpose_labels')->where('id', $id)->delete();
        });

        return Json::respond(Out::label($label));
    }
}
