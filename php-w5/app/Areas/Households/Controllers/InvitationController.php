<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Http;
use App\Areas\Households\Support\Input;
use App\Areas\Households\Support\Out;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Json;
use Illuminate\Http\Request;

/** mealie/routes/households/controller_invitations.py (list + create; email is out of scope) */
class InvitationController
{
    /** GET /households/invitations — admins only; household-scoped page_all(per_page=-1), created_at desc */
    public function index()
    {
        $me = CurrentUser::get();
        if (! $me->admin) {
            Errors::http(403, 'Only admins can list invite tokens');
        }
        $rows = Out::db()->table('invite_tokens')
            ->where('group_id', $me->group_id)->where('household_id', $me->household_id)
            ->orderBy('created_at', 'desc')->get();

        return Json::respond($rows->map(fn ($t) => Out::inviteToken($t))->all());
    }

    /** POST /households/invitations (ALLOW_PASSWORD_LOGIN assumed true, the default) */
    public function store(Request $request)
    {
        $data = Input::object($request);
        $uses = Input::int($data, 'uses');
        $groupId = Input::uuid($data, 'group_id', false, null, true);
        $householdId = Input::uuid($data, 'household_id', false, null, true);

        $me = CurrentUser::get();
        if (! $me->can_invite) {
            Errors::http(403, 'User is not allowed to create invite tokens');
        }

        $groupId = $groupId ?: $me->group_id;
        $householdId = $householdId ?: $me->household_id;
        if (! $me->admin && ($groupId !== $me->group_id || $householdId !== $me->household_id)) {
            Errors::http(403, 'Only admins can create invite tokens for other groups or households');
        }

        $now = Dates::nowDb();
        $token = Http::urlSafeToken(24);
        $id = Out::db()->table('invite_tokens')->insertGetId([
            'token' => $token,
            'uses_left' => $uses,
            'group_id' => $groupId,
            'household_id' => $householdId,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return Json::respond(Out::inviteToken(Out::db()->table('invite_tokens')->where('id', $id)->first()), 201);
    }
}
