<?php

namespace App\Support;

use Illuminate\Database\Query\Builder;
use Illuminate\Http\Request;

/**
 * PaginationBase / PaginationQuery from mealie/schema/response/pagination.py.
 * Envelope keys stay snake_case (per_page, total_pages) because PaginationBase is not a MealieModel;
 * items are whatever the caller maps them to.
 *
 * Not implemented here: queryFilter language (mealie/services/query_filter), orderBy on related
 * fields, random order with paginationSeed. Areas that need them must list them as not implemented.
 */
class Pagination
{
    /**
     * @param  callable(object):array  $map  row -> API item
     * @param  string  $route  path used for next/previous, without the /api prefix (e.g. "/foods")
     */
    public static function page(Request $request, Builder $query, callable $map, string $route, ?string $defaultOrder = null): array
    {
        $page = (int) ($request->query('page', 1));
        $perPage = (int) ($request->query('perPage', $request->query('per_page', 50)));
        $orderBy = $request->query('orderBy');
        $direction = strtolower((string) $request->query('orderDirection', 'desc')) === 'asc' ? 'asc' : 'desc';

        $total = (clone $query)->count();
        if ($perPage === -1) {
            $perPage = max($total, 1);
        }
        $perPage = max($perPage, 1);
        $totalPages = (int) ceil($total / $perPage);
        $page = max($page, 1);

        if (is_string($orderBy) && $orderBy !== '' && preg_match('/^[A-Za-z_]+$/', $orderBy)) {
            $query->orderBy(self::snake($orderBy), $direction);
        } elseif ($defaultOrder !== null) {
            $query->orderBy($defaultOrder, $direction);
        }

        $rows = $query->offset(($page - 1) * $perPage)->limit($perPage)->get();

        $params = [
            'orderBy' => $orderBy ?? 'None',
            'orderByNullPosition' => $request->query('orderByNullPosition', 'None'),
            'orderDirection' => $direction,
            'queryFilter' => $request->query('queryFilter', 'None'),
            'paginationSeed' => $request->query('paginationSeed', 'None'),
        ];

        return [
            'page' => $page,
            'per_page' => $perPage,
            'total' => $total,
            'total_pages' => $totalPages,
            'items' => $rows->map(fn ($row) => $map($row))->values()->all(),
            'next' => $page >= $totalPages ? null : $route.'?'.http_build_query($params + ['page' => $page + 1, 'perPage' => $perPage]),
            'previous' => $page <= 1 ? null : $route.'?'.http_build_query($params + ['page' => $page - 1, 'perPage' => $perPage]),
        ];
    }

    public static function snake(string $camel): string
    {
        return strtolower(preg_replace('/(?<!^)[A-Z]/', '_$0', $camel));
    }
}
