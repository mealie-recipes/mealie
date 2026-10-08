<?php

namespace App\Support;

use Illuminate\Database\Query\Builder;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * RepositoryGeneric.page_all / add_order_by_to_query + PaginationBase.set_pagination_guides
 * (mealie/repos/repository_generic.py, mealie/schema/response/pagination.py).
 * Envelope keys stay snake_case (per_page, total_pages) because PaginationBase is not a MealieModel.
 *
 * Not implemented: the queryFilter language (the value is only echoed in next/previous), orderBy on
 * related fields, and orderBy=random (accepted, keeps the database order).
 */
class Pagination
{
    /**
     * @param  callable(list<object>):list<array>  $map  maps the whole page (so relations can be batch-loaded)
     * @param  string|null  $route  path (without /api) for next/previous; null = Python does not set them
     * @param  array  $opt  table: base table;
     *                      columns: FilterableColumn names => true (string, ordered by lower()), false, or a raw SQL expression
     *                      (created_at and update_at are always allowed);
     *                      model: SQLAlchemy class name; when set, other columns of the table give "Cannot filter on Model.col";
     *                      search: qualified columns `_searchable_properties` (first one drives the relevance order), null = no search;
     *                      normalizeSearch: bool; searchExtra: callable(Builder, list<string> $terms, string $normalized): void;
     *                      queryFilter: fixed filter Python combines into q.query_filter before dumping it;
     *                      guides: 'standard' | 'merge' (`q.model_dump() | request.query_params`, GET /api/recipes)
     */
    public static function page(Request $request, Builder $query, callable $map, ?string $route, array $opt): array
    {
        $q = self::query($request);
        if (isset($opt['queryFilter'])) {
            $q['query_filter'] = $q['query_filter'] ? "({$q['query_filter']}) AND ({$opt['queryFilter']})" : "({$opt['queryFilter']})";
        }
        $table = $opt['table'];
        $search = $request->query('search');
        $search = is_string($search) && $search !== '' && ! empty($opt['search']) ? $search : null;

        if ($search !== null) {
            [$normalized, $terms] = self::searchTerms($search, (bool) ($opt['normalizeSearch'] ?? false));
            $cols = $opt['search'];
            $query->where(function (Builder $w) use ($cols, $terms, $opt, $normalized) {
                foreach ($cols as $col) {
                    foreach ($terms as $t) {
                        $w->orWhere($col, 'like', '%'.$t.'%');
                    }
                }
                if (isset($opt['searchExtra'])) {
                    ($opt['searchExtra'])($w, $terms, $normalized);
                }
            });
            $query->orderByRaw("({$cols[0]} LIKE ?) DESC", ['%'.$normalized.'%']);
        }

        $total = (clone $query)->reorder()->count();

        $perPage = $q['per_page'];
        $limit = $perPage;
        if ($perPage === -1) {
            $perPage = $total;
            $limit = null;
        }
        $totalPages = $perPage === 0 ? 0 : (int) ceil($total / $perPage);
        $page = $q['page'];
        if ($page === -1) {
            $page = $totalPages;
        }
        if ($page < 1) {
            $page = 1;
        }

        $orderBy = $q['order_by'];
        if (($orderBy === null || $orderBy === '') && $search === null) {
            $orderBy = 'created_at';
        }
        if ($orderBy !== null && $orderBy !== '' && $orderBy !== 'random') {
            self::applyOrder($query, $orderBy, $q, $opt);
        }

        $query->limit($limit ?? PHP_INT_MAX); // SQLite needs LIMIT before OFFSET
        if ($page > 1 && $perPage > 0) {
            $query->offset(($page - 1) * $perPage);
        }

        $result = [
            'page' => $page,
            'per_page' => $perPage,
            'total' => $total,
            'total_pages' => $totalPages,
            'items' => array_values($map($query->get()->all())),
            'next' => null,
            'previous' => null,
        ];

        if ($route !== null) {
            $params = ($opt['guides'] ?? 'standard') === 'merge' ? self::mergedParams($request, $q) : self::standardParams($q);
            if ($page < $totalPages) {
                $result['next'] = $route.'?'.self::encode(array_merge($params, ['page' => $page + 1]));
            }
            if ($page > 1) {
                $result['previous'] = $route.'?'.self::encode(array_merge($params, ['page' => $page - 1]));
            }
        }

        return $result;
    }

    /** Parse PaginationQuery from the query string (422 on bad ints / enums). */
    public static function query(Request $request): array
    {
        $errors = [];
        $int = function (string $key, int $default) use ($request, &$errors): int {
            $v = $request->query($key);
            if ($v === null) {
                return $default;
            }
            if (! is_string($v) || ! preg_match('/^\s*[+-]?\d+\s*$/', $v)) {
                $errors[] = "{'type': 'int_parsing', 'loc': ('query', '{$key}'), 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': '".(is_string($v) ? $v : '')."'}";

                return $default;
            }

            return (int) trim($v);
        };
        $page = $int('page', 1);
        $perPage = $int('perPage', 50);

        $dir = $request->query('orderDirection', 'desc');
        if (! in_array($dir, ['asc', 'desc'], true)) {
            $errors[] = "{'type': 'enum', 'loc': ('query', 'orderDirection'), 'msg': \"Input should be 'asc' or 'desc'\", 'input': '{$dir}'}";
        }
        $nulls = $request->query('orderByNullPosition');
        if ($nulls !== null && ! in_array($nulls, ['first', 'last'], true)) {
            $errors[] = "{'type': 'enum', 'loc': ('query', 'orderByNullPosition'), 'msg': \"Input should be 'first' or 'last'\", 'input': '{$nulls}'}";
        }
        $orderBy = $request->query('orderBy');
        $seed = $request->query('paginationSeed');
        if ($orderBy === 'random' && ($seed === null || $seed === '')) {
            $errors[] = "{'type': 'value_error', 'loc': ('query', 'paginationSeed'), 'msg': 'Value error, paginationSeed is required when orderBy is random'}";
        }
        if ($errors !== []) {
            $n = count($errors);
            Errors::validation(($n === 1 ? '1 validation error: ' : "{$n} validation errors: ").implode(' ', $errors));
        }

        return [
            'order_by' => $orderBy,
            'order_by_null_position' => $nulls,
            'order_direction' => $dir,
            'query_filter' => $request->query('queryFilter'),
            'pagination_seed' => $seed,
            'page' => $page,
            'per_page' => $perPage,
        ];
    }

    /** SearchFilter (mealie/schema/response/query_search.py), tokenized mode only (SQLite). */
    public static function searchTerms(string $search, bool $normalize): array
    {
        $p = Text::PUNCTUATION;
        $s = strtr($search, $p, str_repeat(' ', strlen($p)));
        $s = $normalize ? trim(strtolower(Text::unidecode($s))) : trim($s);

        $quoted = '/(["\'])(?:(?=(\\\\?))\2.)*?\1/';
        if (preg_match($quoted, $s)) {
            preg_match_all($quoted, $s, $m);
            $list = array_map(fn ($x) => preg_replace('/[\'"](.*)[\'"]/', '$1', $x), $m[0]);
            $rest = preg_replace($quoted, '', $s);
            $rest = strtr($rest, $p, str_repeat(' ', strlen($p)));
            $list = array_merge($list, preg_split('/\s+/', trim($rest), -1, PREG_SPLIT_NO_EMPTY));
        } else {
            $list = preg_split('/\s+/', trim($s), -1, PREG_SPLIT_NO_EMPTY);
        }

        return [$s, array_map('trim', $list)];
    }

    /** humps.decamelize (strings that are all upper case are returned unchanged). */
    public static function decamelize(string $value): string
    {
        if (preg_match('/[A-Z]/', $value) && ! preg_match('/[a-z]/', $value)) {
            return $value;
        }

        return strtolower(preg_replace('/(?<=[a-z0-9])([A-Z])|(?<=[A-Z])([A-Z])(?=[a-z])/', '_$1$2', $value));
    }

    private static function applyOrder(Builder $query, string $orderBy, array $q, array $opt): void
    {
        $table = $opt['table'];
        $columns = $opt['columns'] + ['created_at' => false, 'update_at' => false];
        foreach (explode(',', $orderBy) as $part) {
            $part = trim($part);
            $dir = $q['order_direction'];
            $col = $part;
            if (str_contains($part, ':')) {
                $pieces = explode(':', $part);
                if (count($pieces) !== 2 || ! in_array($pieces[1], ['asc', 'desc'], true)) {
                    Errors::http(400, "Invalid order_by statement \"{$orderBy}\": \"{$part}\" is invalid");
                }
                [$col, $dir] = $pieces;
            }
            $snake = self::decamelize($col);
            if ($snake === 'updated_at') {
                $snake = 'update_at';
            }
            if (! array_key_exists($snake, $columns)) {
                if (isset($opt['model']) && in_array($snake, self::tableColumns($table), true)) {
                    Errors::http(400, "Invalid order_by statement \"{$orderBy}\": Cannot filter on {$opt['model']}.{$snake}");
                }
                Errors::http(400, "Invalid order_by statement \"{$orderBy}\": \"{$part}\" is invalid");
            }
            $kind = $columns[$snake];
            $expr = is_string($kind) ? $kind : ($kind ? "lower({$table}.{$snake})" : "{$table}.{$snake}");
            $sql = $expr.' '.strtoupper($dir);
            if ($q['order_by_null_position'] === 'first') {
                $sql .= ' NULLS FIRST';
            } elseif ($q['order_by_null_position'] === 'last') {
                $sql .= ' NULLS LAST';
            }
            $query->orderByRaw($sql);
        }
    }

    private static array $tableColumns = [];

    private static function tableColumns(string $table): array
    {
        return self::$tableColumns[$table] ??= array_map(
            fn ($c) => $c->name,
            DB::connection('mealie')->select("PRAGMA table_info(\"{$table}\")"),
        );
    }

    private static function standardParams(array $q): array
    {
        return [
            'orderBy' => $q['order_by'],
            'orderByNullPosition' => $q['order_by_null_position'],
            'orderDirection' => $q['order_direction'],
            'queryFilter' => $q['query_filter'],
            'paginationSeed' => $q['pagination_seed'],
            'page' => $q['page'],
            'perPage' => $q['per_page'],
        ];
    }

    /** `q.model_dump() | request.query_params`, Nones dropped, then camelized (GET /api/recipes). */
    private static function mergedParams(Request $request, array $q): array
    {
        $merged = [];
        foreach ($q as $k => $v) {
            $merged[$k] = $v;
        }
        $raw = $request->server('QUERY_STRING', '');
        foreach (explode('&', (string) $raw) as $pair) {
            if ($pair === '') {
                continue;
            }
            [$k, $v] = array_pad(explode('=', $pair, 2), 2, '');
            $merged[urldecode($k)] = urldecode($v);
        }
        $out = [];
        foreach ($merged as $k => $v) {
            if ($v === null) {
                continue;
            }
            $out[Json::camel((string) $k)] = $v;
        }

        return $out;
    }

    /** urlencode(query) with Python's quote_plus. */
    private static function encode(array $params): string
    {
        $parts = [];
        foreach ($params as $k => $v) {
            $v = $v === null ? 'None' : (is_bool($v) ? ($v ? 'True' : 'False') : (string) $v);
            $parts[] = urlencode((string) $k).'='.str_replace('%7E', '~', urlencode($v));
        }

        return implode('&', $parts);
    }
}
