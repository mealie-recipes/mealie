<?php

namespace App\Areas\Households\Controllers;

use App\Areas\Households\Support\Http;
use App\Areas\Households\Support\Input;
use App\Areas\Households\Support\Out;
use App\Areas\Households\Support\Paginator;
use App\Areas\Households\Support\Slug;
use App\Support\CurrentUser;
use App\Support\Dates;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Json;
use Illuminate\Database\QueryException;
use Illuminate\Http\Request;

/** mealie/routes/households/controller_cookbooks.py + mealie/repos/repository_cookbooks.py */
class CookbookController
{
    private const COLUMNS = ['id', 'position', 'group_id', 'household_id', 'name', 'slug', 'description', 'public', 'require_all_categories', 'require_all_tags', 'require_all_tools', 'created_at', 'update_at'];

    private const STRING_COLUMNS = ['name', 'slug', 'description'];

    private function table()
    {
        return Out::db()->table('cookbooks');
    }

    /** household-scoped repo (self.repos.cookbooks) */
    private function householdQuery()
    {
        return $this->table()->where('group_id', CurrentUser::groupId())->where('household_id', CurrentUser::householdId());
    }

    /** CreateCookBook validation */
    private function parseCreate(array $data): array
    {
        $name = trim((string) Input::str($data, 'name'));
        if ($name === '' || Slug::make($name) === '') {
            Errors::validation('Value error, Name cannot be empty at body.name');
        }
        $public = Input::raw($data, 'public');

        return [
            'name' => $name,
            'description' => Input::str($data, 'description', ''),
            'slug' => Input::str($data, 'slug', null, true),
            'position' => Input::int($data, 'position', 1),
            'public' => $public === null ? false : Input::bool($data, 'public', false),
            'query_filter_string' => Input::str($data, 'query_filter_string', ''),
        ];
    }

    /** UpdateCookBook = SaveCookBook + id */
    private function parseUpdate(array $data): array
    {
        $out = $this->parseCreate($data);
        $out['group_id'] = Input::uuid($data, 'group_id');
        $out['household_id'] = Input::uuid($data, 'household_id');
        $out['id'] = Input::uuid($data, 'id');

        return $out;
    }

    private function isUniqueViolation(QueryException $e): bool
    {
        return str_contains($e->getMessage(), 'UNIQUE constraint failed');
    }

    /** RepositoryCookbooks.update slug rule + retry on unique violation */
    private function updateRow(object $existing, array $values): object
    {
        $newSlug = Slug::make($values['name']);
        $slug = $values['slug'] ?? null;
        if (! ($slug && preg_match('/^('.preg_quote($newSlug, '/').')(-\d+)?$/', $slug))) {
            $slug = $newSlug;
        }
        unset($values['slug'], $values['id']);

        for ($i = 0; $i < 10; $i++) {
            try {
                $this->table()->where('id', $existing->id)->update($values + ['slug' => $slug, 'update_at' => Dates::nowDb()]);

                return $this->table()->where('id', $existing->id)->first();
            } catch (QueryException $e) {
                if (! str_contains($e->getMessage(), 'constraint failed')) {
                    throw $e;
                }
                $slug = Slug::make("{$values['name']} (".($i + 1).')');
            }
        }

        Errors::http(409, ['message' => 'This item already exists.', 'error' => true, 'exception' => null]);
    }

    /** GET /households/cookbooks — whole group */
    public function index(Request $request)
    {
        $query = $this->table()->where('group_id', CurrentUser::groupId());

        return Json::respond(Paginator::page($request, $query, fn ($r) => Out::cookbook($r), 'cookbooks', self::COLUMNS, self::STRING_COLUMNS, '/households/cookbooks', null, 'CookBook', ['query_filter_string']));
    }

    /** POST /households/cookbooks */
    public function store(Request $request)
    {
        $values = $this->parseCreate(Input::object($request));
        $id = Guid::new();
        $now = Dates::nowDb();
        $slug = Slug::make($values['name']);
        unset($values['slug']);

        for ($i = 0; $i < 10; $i++) {
            try {
                $this->table()->insert($values + [
                    'id' => $id,
                    'slug' => $slug,
                    'group_id' => CurrentUser::groupId(),
                    'household_id' => CurrentUser::householdId(),
                    'require_all_categories' => true,
                    'require_all_tags' => true,
                    'require_all_tools' => true,
                    'created_at' => $now,
                    'update_at' => $now,
                ]);

                return Json::respond(Out::cookbook($this->table()->where('id', $id)->first()), 201);
            } catch (QueryException $e) {
                if (! $this->isUniqueViolation($e)) {
                    throw $e;
                }
                $slug = Slug::make("{$values['name']} (".($i + 1).')');
            }
        }

        Errors::http(409, ['message' => 'This item already exists.', 'error' => true, 'exception' => null]);
    }

    /** PUT /households/cookbooks */
    public function updateMany(Request $request)
    {
        $items = Input::listOfObjects($request);
        $parsed = [];
        foreach ($items as $item) {
            $parsed[] = $this->parseUpdate($item);
        }

        $out = [];
        foreach ($parsed as $values) {
            $existing = $this->householdQuery()->where('id', $values['id'])->first();
            if (! $existing) {
                Http::notFound();
            }
            $out[] = Out::cookbook($this->updateRow($existing, $values));
        }

        return Json::respond($out);
    }

    /** GET /households/cookbooks/{item_id} — whole group, by id (any UUID) or slug */
    public function show(string $itemId)
    {
        $query = $this->table()->where('group_id', CurrentUser::groupId());
        $row = self::looksLikeUuid($itemId)
            ? $query->where('id', Guid::toDb($itemId))->first()
            : $query->where('slug', $itemId)->first();
        if (! $row) {
            Errors::http(404, 'Not Found');
        }

        return Json::respond(Out::cookbook($row));
    }

    /** PUT /households/cookbooks/{item_id} */
    public function update(Request $request, string $itemId)
    {
        $values = $this->parseCreate(Input::object($request));
        if (! self::looksLikeUuid($itemId)) {
            // GUID bind of a non-UUID string raises outside HttpRepo's try -> unhandled
            return response('Internal Server Error', 500, ['Content-Type' => 'text/plain; charset=utf-8']);
        }
        $existing = $this->householdQuery()->where('id', Guid::toDb($itemId))->first();
        if (! $existing) {
            Http::notFound();
        }

        return Json::respond(Out::cookbook($this->updateRow($existing, $values)));
    }

    /** DELETE /households/cookbooks/{item_id} */
    public function destroy(string $itemId)
    {
        if (! self::looksLikeUuid($itemId)) {
            Errors::http(400, ['message' => 'An unexpected error occurred', 'error' => true, 'exception' => "(builtins.ValueError) badly formed hexadecimal UUID string\n"
                .'[SQL: SELECT cookbooks.id, cookbooks.position, cookbooks.group_id, cookbooks.household_id, cookbooks.name, cookbooks.slug, cookbooks.description, cookbooks.public, cookbooks.query_filter_string, cookbooks.require_all_categories, cookbooks.require_all_tags, cookbooks.require_all_tools, cookbooks.created_at, cookbooks.update_at, households_1.id AS id_1, households_1.name AS name_1, households_1.slug AS slug_1, households_1.group_id AS group_id_1, households_1.created_at AS created_at_1, households_1.update_at AS update_at_1 '
                ."\nFROM cookbooks LEFT OUTER JOIN households AS households_1 ON households_1.id = cookbooks.household_id \n"
                ."WHERE cookbooks.group_id = ? AND cookbooks.household_id = ? AND cookbooks.id = ?]\n[parameters: [{}]]"]);
        }
        $row = $this->householdQuery()->where('id', Guid::toDb($itemId))->first();
        if (! $row) {
            Http::deleteNotFound();
        }
        $out = Out::cookbook($row);
        $db = Out::db();
        foreach (['cookbooks_to_categories', 'cookbooks_to_tags', 'cookbooks_to_tools'] as $link) {
            $db->table($link)->where('cookbook_id', $row->id)->delete();
        }
        $this->table()->where('id', $row->id)->delete();

        return Json::respond($out);
    }

    /** Python uuid.UUID(str) acceptance */
    public static function looksLikeUuid(string $v): bool
    {
        $s = trim($v);
        if (str_starts_with(strtolower($s), 'urn:uuid:')) {
            $s = substr($s, 9);
        }
        $s = str_replace(['{', '}', '-'], '', $s);

        return (bool) preg_match('/^[0-9a-fA-F]{32}$/', $s);
    }
}
