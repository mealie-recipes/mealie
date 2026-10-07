<?php

namespace App\Areas\GroupsAdmin\Support;

use App\Support\Errors;
use Illuminate\Database\Query\Builder;
use Illuminate\Http\Request;

/**
 * Port of RepositoryGeneric.page_all / add_pagination_to_query / add_order_by_to_query
 * (mealie/repos/repository_generic.py) for one table without the queryFilter language.
 */
class Pager
{
    /**
     * @param  string  $table  base table (columns are qualified with it)
     * @param  string  $model  SQLAlchemy model name, used in "Cannot filter on" messages
     * @param  array<string, bool>  $filterable  FilterableColumn names => is string column
     * @param  callable(list<object>): list<array>  $map  maps the whole page (so relations can be batch-loaded)
     * @param  string  $route  router-local path used for next/previous
     * @param  string|null  $searchMode  null (no search support) | 'plain' | 'normalized'
     * @param  list<string>  $searchColumns  `_searchable_properties`, first one drives the relevance order
     */
    public static function page(
        Request $request,
        Builder $query,
        string $table,
        string $model,
        array $filterable,
        callable $map,
        string $route,
        ?string $searchMode = null,
        array $searchColumns = [],
    ): array {
        $q = self::query($request);

        $search = $searchMode !== null ? $request->query('search') : null;
        $searchOrder = null;
        if (is_string($search) && $search !== '') {
            [$where, $searchOrder] = Search::tokenized($search, $searchMode === 'normalized', $table, $searchColumns);
            $query->where($where);
        }

        $orderBy = $q['orderBy'];
        if (! $orderBy && $searchOrder === null) {
            $orderBy = 'created_at';
        }

        $count = (clone $query)->count();

        $perPage = $q['perPage'];
        $limit = $perPage;
        if ($perPage === -1) {
            $perPage = $count;
            $limit = null;
        }
        $totalPages = $perPage === 0 ? 0 : (int) ceil($count / $perPage);

        $page = $q['page'];
        if ($page === -1) {
            $page = $totalPages;
        }
        if ($page < 1) {
            $page = 1;
        }

        if ($searchOrder !== null) {
            $query->orderByRaw($searchOrder[0], $searchOrder[1]);
        }
        if ($orderBy) {
            self::applyOrder($query, $orderBy, $q['orderDirection'], $q['orderByNullPosition'], $table, $model, $filterable);
        }

        // SQLite needs a LIMIT before OFFSET
        $query->limit($limit ?? PHP_INT_MAX);
        if ($page > 1 && $perPage > 0) {
            $query->offset(($page - 1) * $perPage);
        }

        $rows = $query->get();

        $params = [
            'orderBy' => $q['orderBy'] ?? 'None',
            'orderByNullPosition' => $q['orderByNullPosition'] ?? 'None',
            'orderDirection' => $q['orderDirection'],
            'queryFilter' => $q['queryFilter'] ?? 'None',
            'paginationSeed' => $q['paginationSeed'] ?? 'None',
            'page' => $q['page'],
            'perPage' => $q['perPage'],
        ];

        return [
            'page' => $page,
            'per_page' => $perPage,
            'total' => $count,
            'total_pages' => $totalPages,
            'items' => array_values($map($rows->all())),
            'next' => $page >= $totalPages ? null : $route.'?'.self::encode(['page' => $page + 1] + $params),
            'previous' => $page <= 1 ? null : $route.'?'.self::encode(['page' => $page - 1] + $params),
        ];
    }

    /** urlencode(query, doseq=True) with Python's quote_plus. Keys keep the dump order; page stays in place. */
    private static function encode(array $params): string
    {
        $order = ['orderBy', 'orderByNullPosition', 'orderDirection', 'queryFilter', 'paginationSeed', 'page', 'perPage'];
        $out = [];
        foreach ($order as $key) {
            $out[] = urlencode($key).'='.urlencode((string) $params[$key]);
        }

        return implode('&', $out);
    }

    /** PaginationQuery validation (query params). */
    public static function query(Request $request): array
    {
        $v = Validator::query($request);
        $page = $v->int('page', false, 1);
        $perPage = $v->int('per_page', false, 50);
        $direction = $v->enum('order_direction', ['asc', 'desc'], false, 'desc');
        $nulls = $v->enum('order_by_null_position', ['first', 'last'], false, null);
        $orderBy = $v->str('order_by', false, null);
        $queryFilter = $v->str('query_filter', false, null);
        $seed = $v->str('pagination_seed', false, null);
        if ($orderBy === 'random' && ! $seed) {
            $v->custom('pagination_seed', 'paginationSeed is required when orderBy is random');
        }
        $v->check();

        return [
            'page' => $page,
            'perPage' => $perPage,
            'orderDirection' => $direction ?? 'desc',
            'orderByNullPosition' => $nulls,
            'orderBy' => $orderBy,
            'queryFilter' => $queryFilter,
            'paginationSeed' => $seed,
        ];
    }

    private static function applyOrder(Builder $query, string $orderBy, string $direction, ?string $nulls, string $table, string $model, array $filterable): void
    {
        if ($orderBy === 'random') {
            // Not supported (rule: no orderBy=random); keep the database order.
            return;
        }

        foreach (explode(',', $orderBy) as $val) {
            $val = trim($val);
            $dir = $direction;
            $attr = $val;
            if (str_contains($val, ':')) {
                $pieces = explode(':', $val);
                if (count($pieces) !== 2 || ! in_array($pieces[1], ['asc', 'desc'], true)) {
                    Errors::http(400, "Invalid order_by statement \"{$orderBy}\": \"{$val}\" is invalid");
                }
                [$attr, $dir] = $pieces;
            }

            $column = self::decamelize($attr);
            $allColumns = $filterable + ['created_at' => false, 'update_at' => false];
            if (! preg_match('/^[a-z_][a-z0-9_]*$/', $column) || ! self::columnExists($table, $column)) {
                Errors::http(400, "Invalid order_by statement \"{$orderBy}\": \"{$val}\" is invalid");
            }
            if (! array_key_exists($column, $allColumns)) {
                Errors::http(400, "Invalid order_by statement \"{$orderBy}\": Cannot filter on {$model}.{$column}");
            }

            $expr = $allColumns[$column] ? "lower({$table}.{$column})" : "{$table}.{$column}";
            $sql = $expr.' '.($dir === 'asc' ? 'ASC' : 'DESC');
            if ($nulls === 'first') {
                $sql .= ' NULLS FIRST';
            } elseif ($nulls === 'last') {
                $sql .= ' NULLS LAST';
            }
            $query->orderByRaw($sql);
        }
    }

    private static array $columns = [];

    private static function columnExists(string $table, string $column): bool
    {
        if (! isset(self::$columns[$table])) {
            self::$columns[$table] = array_map(fn ($c) => $c->name, Db::conn()->select("PRAGMA table_info(\"{$table}\")"));
        }

        return in_array($column, self::$columns[$table], true);
    }

    /** humps.decamelize */
    public static function decamelize(string $value): string
    {
        return strtolower(preg_replace('/(?<=[a-z0-9])([A-Z])|(?<=[A-Z])([A-Z])(?=[a-z])/', '_$1$2', $value));
    }
}
