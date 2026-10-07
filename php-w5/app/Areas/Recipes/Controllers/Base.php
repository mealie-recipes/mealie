<?php

namespace App\Areas\Recipes\Controllers;

use App\Areas\Recipes\Support\Db;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Json;
use Illuminate\Database\QueryException;
use Illuminate\Http\JsonResponse;

abstract class Base
{
    /** HttpRepo default message for routers that pass no exception_msgs. */
    public const DEFAULT_MSG = 'An unexpected error occurred.';

    /** BaseUserController.registered_exceptions fallback (t("generic.server-error")). */
    public const SERVER_ERROR_MSG = 'An unexpected error occurred';

    public const NO_RESULT = 'No row was found when one was required';

    /**
     * Laravel's ControllerDispatcher calls this. Errors::* throw HttpResponseException, which the shared
     * catch-all Throwable renderer in bootstrap/app.php would turn into a 500, so unwrap it here.
     */
    public function callAction($method, $parameters)
    {
        try {
            return $this->{$method}(...array_values($parameters));
        } catch (\Illuminate\Http\Exceptions\HttpResponseException $e) {
            return $e->getResponse();
        }
    }

    protected function groupId(): string
    {
        return CurrentUser::groupId();
    }

    /** OperationChecks.can_organize (mealie/routes/_base/checks.py:38) */
    protected function canOrganize(): void
    {
        if (! (bool) (CurrentUser::get()->can_organize ?? false)) {
            Errors::http(403, 'Forbidden');
        }
    }

    protected function json(mixed $data, int $status = 200): JsonResponse
    {
        return Json::respond($data, $status);
    }

    /** MealieCrudRoute (mealie/routes/_base/routers.py:27): last-modified + no-cache when the body has updatedAt */
    protected function crud(array $data, int $status = 200): JsonResponse
    {
        $res = $this->json($data, $status);
        if (! empty($data['updatedAt']) && ! array_is_list($data)) {
            $res->headers->set('last-modified', $data['updatedAt']);
            $res->headers->set('Cache-Control', 'no-cache, no-store, must-revalidate');
        }

        return $res;
    }

    /** HttpRepo.get_one / update_one 404 */
    protected function notFound(): never
    {
        Errors::errorResponse(404, 'Not found.');
    }

    protected function now(): string
    {
        return Dates::nowDb();
    }

    /**
     * Run a write inside a transaction and map SQLite errors like HttpRepo.handle_exception
     * (mealie/routes/_base/mixins.py:71): unique violation -> 409 "This item already exists.",
     * other integrity errors -> 409 with $integrityMsg, anything else -> 400.
     */
    protected function write(callable $fn, string $defaultMsg, ?string $integrityMsg = null): mixed
    {
        $conn = Db::conn();
        try {
            return $conn->transaction($fn);
        } catch (QueryException $e) {
            $orig = $e->getPrevious()?->getMessage() ?? $e->getMessage();
            $detail = preg_replace('/^SQLSTATE\[\w+\]: [^:]+: \d+ /', '', $orig);
            if (str_contains($orig, 'constraint failed') || str_contains($orig, 'Integrity constraint')) {
                $msg = str_contains($orig, 'UNIQUE constraint failed') ? 'This item already exists.' : ($integrityMsg ?? $defaultMsg);
                Errors::errorResponse(409, $msg, '(sqlite3.IntegrityError) '.$detail);
            }
            Errors::errorResponse(400, $defaultMsg, $detail);
        }
    }
}
