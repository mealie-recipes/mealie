<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Checks;
use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Out;
use App\Areas\GroupsAdmin\Support\Validator;
use App\Support\CurrentUser;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/groups/controller_group_reports.py */
class ReportsController
{
    public function index(Request $request)
    {
        $v = Validator::query($request);
        $type = $v->enum('report_type', ['backup', 'restore', 'migration', 'bulk_import']);
        $v->check();

        // multi_query({"group_id": ..., "category": report_type}): a missing report_type filters on NULL
        $query = Db::table('group_reports')->where('group_id', CurrentUser::groupId());
        $type === null ? $query->whereNull('category') : $query->where('category', $type);

        return Json::respond($query->orderByRaw('rowid')->limit(9999)->get()->map(fn ($r) => Out::reportSummary($r))->all());
    }

    private function find(string $id): ?object
    {
        return Db::table('group_reports')->where('group_id', CurrentUser::groupId())->where('id', $id)->first();
    }

    public function show(string $itemId)
    {
        $report = $this->find(Guid::requireUuid4($itemId));
        if ($report === null) {
            Checks::notFound();
        }

        return Json::respond(Out::reportOut($report));
    }

    public function destroy(string $itemId)
    {
        $id = Guid::requireUuid4($itemId);
        if ($this->find($id) === null) {
            // the HttpRepo 404 is caught by the handler's `except Exception` and re-raised as a 500
            Errors::errorResponse(500, 'Failed to delete report');
        }
        Db::conn()->transaction(function () use ($id) {
            Db::table('report_entries')->where('report_id', $id)->delete();
            Db::table('group_reports')->where('id', $id)->delete();
        });

        return Json::respond(['message' => 'Report deleted.', 'error' => false]);
    }
}
