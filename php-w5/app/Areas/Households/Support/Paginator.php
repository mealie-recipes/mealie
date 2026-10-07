<?php

namespace App\Areas\Households\Support;

use App\Support\Errors;
use App\Support\Pagination;
use Illuminate\Database\Query\Builder;
use Illuminate\Http\Request;

/**
 * RepositoryGeneric.page_all + PaginationBase.set_pagination_guides (mealie/repos/repository_generic.py,
 * mealie/schema/response/pagination.py). Own copy because the shared helper differs on perPage=-1,
 * cannot echo a fixed queryFilter and does not validate orderBy.
 * The user-supplied queryFilter is NOT applied (out of scope).
 */
class Paginator
{
    /**
     * @param  callable(object):array  $map
     * @param  string[]  $columns  FilterableColumn names of the model (the only ones orderBy accepts)
     * @param  string[]  $stringColumns  columns ordered by lower() (QueryFilterBuilder._transform_model_attr)
     * @param  string|null  $route  path (without /api) for next/previous; null = Python does not set them
     * @param  string|null  $extraFilter  filter Python combines into q.query_filter before dumping it
     * @param  string  $model  SQLAlchemy class name, for "Cannot filter on Model.column"
     * @param  string[]  $nonFilterable  other mapped columns of the model
     */
    public static function page(
        Request $request,
        Builder $query,
        callable $map,
        string $table,
        array $columns,
        array $stringColumns = [],
        ?string $route = null,
        ?string $extraFilter = null,
        string $model = '',
        array $nonFilterable = [],
    ): array {
        $q = self::query($request);
        if ($extraFilter !== null) {
            $q['query_filter'] = $q['query_filter'] ? "({$q['query_filter']}) AND ({$extraFilter})" : "({$extraFilter})";
        }

        $total = (clone $query)->count();

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

        $orderBy = $q['order_by'] ?? 'created_at';
        foreach (explode(',', $orderBy) as $part) {
            $part = trim($part);
            $dir = $q['order_direction'];
            if (str_contains($part, ':')) {
                $pieces = explode(':', $part);
                if (count($pieces) !== 2 || ! in_array($pieces[1], ['asc', 'desc'], true)) {
                    Errors::http(400, "Invalid order_by statement \"{$orderBy}\": \"{$part}\" is invalid");
                }
                [$part, $dir] = $pieces;
            }
            $col = Pagination::snake($part);
            if (! in_array($col, $columns, true)) {
                if (in_array($col, $nonFilterable, true)) {
                    Errors::http(400, "Invalid order_by statement \"{$orderBy}\": Cannot filter on {$model}.{$col}");
                }
                Errors::http(400, "Invalid order_by statement \"{$orderBy}\": \"{$part}\" is invalid");
            }
            $expr = in_array($col, $stringColumns, true) ? "lower({$table}.{$col})" : "{$table}.{$col}";
            $nulls = match ($q['order_by_null_position']) {
                'first' => ' NULLS FIRST',
                'last' => ' NULLS LAST',
                default => '',
            };
            $query->orderByRaw("{$expr} {$dir}{$nulls}");
        }

        $offset = ($page - 1) * $perPage;
        if ($limit !== null) {
            $query->limit($limit)->offset($offset);
            $rows = $query->get();
        } else {
            // per_page=-1: no LIMIT; any page past the first is beyond the end
            $rows = $offset > 0 ? collect() : $query->get();
        }

        $items = $rows->map(fn ($row) => $map($row))->values()->all();

        $out = [
            'page' => $page,
            'per_page' => $perPage,
            'total' => $total,
            'total_pages' => $totalPages,
            'items' => $items,
            'next' => null,
            'previous' => null,
        ];

        if ($route !== null) {
            $params = [
                'orderBy' => $q['order_by'] ?? 'None',
                'orderByNullPosition' => $q['order_by_null_position'] ?? 'None',
                'orderDirection' => $q['order_direction'],
                'queryFilter' => $q['query_filter'] ?? 'None',
                'paginationSeed' => $q['pagination_seed'] ?? 'None',
                'page' => $q['page'],
                'perPage' => $q['per_page'],
            ];
            if ($page < $totalPages) {
                $out['next'] = $route.'?'.http_build_query(array_merge($params, ['page' => $page + 1]));
            }
            if ($page > 1) {
                $out['previous'] = $route.'?'.http_build_query(array_merge($params, ['page' => $page - 1]));
            }
        }

        return $out;
    }

    /** PaginationQuery parsed from query string (camelCase alias or snake_case name). */
    public static function query(Request $request): array
    {
        $get = function (string $snake) use ($request) {
            $camel = lcfirst(str_replace('_', '', ucwords($snake, '_')));

            return $request->query($camel, $request->query($snake));
        };

        $int = function (string $snake, int $default) use ($get) {
            $v = $get($snake);
            if ($v === null) {
                return $default;
            }
            $i = is_string($v) ? Input::toInt($v) : null;
            if ($i === null) {
                Errors::validation("Input should be a valid integer, unable to parse string as an integer at query.{$snake}");
            }

            return $i;
        };

        $dir = $get('order_direction') ?? 'desc';
        if (! in_array($dir, ['asc', 'desc'], true)) {
            Errors::validation("Input should be 'asc' or 'desc' at query.order_direction");
        }
        $nulls = $get('order_by_null_position');
        if ($nulls !== null && ! in_array($nulls, ['first', 'last'], true)) {
            Errors::validation("Input should be 'first' or 'last' at query.order_by_null_position");
        }
        $orderBy = $get('order_by');
        $seed = $get('pagination_seed');
        if ($orderBy === 'random' && ! $seed) {
            Errors::validation('Value error, paginationSeed is required when orderBy is random at query.pagination_seed');
        }

        return [
            'order_by' => $orderBy === null || $orderBy === '' ? null : (string) $orderBy,
            'order_by_null_position' => $nulls,
            'order_direction' => $dir,
            'query_filter' => $get('query_filter') === '' ? null : $get('query_filter'),
            'pagination_seed' => $seed,
            'page' => $int('page', 1),
            'per_page' => $int('per_page', 50),
        ];
    }
}
