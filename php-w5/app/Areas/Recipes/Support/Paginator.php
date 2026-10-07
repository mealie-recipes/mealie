<?php

namespace App\Areas\Recipes\Support;

use App\Support\Errors;
use App\Support\Json;
use Illuminate\Database\Query\Builder;
use Illuminate\Http\Request;

/**
 * RepositoryGeneric.page_all + PaginationBase.set_pagination_guides
 * (mealie/repos/repository_generic.py, mealie/schema/response/pagination.py).
 *
 * Own copy of the shared App\Support\Pagination: see the area-2 contract for why.
 * queryFilter and orderBy on related fields are not implemented (queryFilter is ignored).
 */
class Paginator
{
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

    /**
     * @param  array  $opt  table (base table), columns (snake => 'string'|'other'), search (list of columns or null),
     *                      normalizeSearch (bool), searchExtra (callable(Builder, array $terms, string $search): void),
     *                      guides ('standard'|'merge')
     */
    public static function page(Request $request, Builder $query, callable $map, string $route, array $opt): array
    {
        $q = self::query($request);
        $table = $opt['table'];
        $search = $request->query('search');
        $search = is_string($search) && $search !== '' ? $search : null;

        if ($search !== null && ! empty($opt['search'])) {
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
            $first = $cols[0];
            $query->orderByRaw("({$first} LIKE ?) DESC", ['%'.$normalized.'%']);
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
        if ($orderBy !== null && $orderBy !== '') {
            self::applyOrder($query, $orderBy, $q, $opt['columns'], $table);
        }

        $query->limit($limit ?? PHP_INT_MAX); // SQLite needs LIMIT before OFFSET
        $query->offset(($page - 1) * $perPage);

        $rows = $query->get();

        $result = [
            'page' => $page,
            'per_page' => $perPage,
            'total' => $total,
            'total_pages' => $totalPages,
            'items' => $rows->map(fn ($r) => $map($r))->values()->all(),
            'next' => null,
            'previous' => null,
        ];

        $params = ($opt['guides'] ?? 'standard') === 'merge' ? self::mergedParams($request, $q) : self::standardParams($q);
        if ($page < $totalPages) {
            $result['next'] = $route.'?'.self::encode(array_merge($params, ['page' => $page + 1]));
        }
        if ($page > 1) {
            $result['previous'] = $route.'?'.self::encode(array_merge($params, ['page' => $page - 1]));
        }

        return $result;
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

    private static function applyOrder(Builder $query, string $orderBy, array $q, array $columns, string $table): void
    {
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
            $snake = Json::camel($col) === $col ? strtolower(preg_replace('/(?<!^)[A-Z]/', '_$0', $col)) : $col;
            if ($snake === 'updated_at') {
                $snake = 'update_at';
            }
            if (! array_key_exists($snake, $columns)) {
                Errors::http(400, "Invalid order_by statement \"{$orderBy}\": \"{$part}\" is invalid");
            }
            $kind = $columns[$snake];
            $expr = str_starts_with($kind, 'expr:') ? substr($kind, 5)
                : ($kind === 'string' ? "lower({$table}.{$snake})" : "{$table}.{$snake}");
            $sql = $expr.' '.strtoupper($dir);
            if ($q['order_by_null_position'] === 'first') {
                $sql .= ' NULLS FIRST';
            } elseif ($q['order_by_null_position'] === 'last') {
                $sql .= ' NULLS LAST';
            }
            $query->orderByRaw($sql);
        }
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
