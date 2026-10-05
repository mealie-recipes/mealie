<?php

namespace App\Support;

use Illuminate\Http\Request;

final class Pages
{
    /**
     * @param  list<array<string, mixed>>  $items
     * @return array<string, mixed>
     */
    public static function make(array $items, int $page, int $perPage, int $total): array
    {
        $totalPages = $perPage > 0 ? (int) ceil($total / $perPage) : ($total > 0 ? 1 : 0);

        return [
            'page' => $page,
            'perPage' => $perPage,
            'total' => $total,
            'totalPages' => $totalPages,
            'items' => JsonShape::camel($items),
            'next' => null,
            'previous' => null,
        ];
    }

    /**
     * @return array{page: int, perPage: int, orderBy: ?string, direction: string, search: ?string}
     */
    public static function query(Request $request): array
    {
        $perPage = (int) $request->query('perPage', $request->query('per_page', 50));
        if ($perPage === 0) {
            $perPage = 50;
        }

        $direction = strtolower((string) $request->query('orderDirection', $request->query('order_direction', 'desc')));

        return [
            'page' => max(1, (int) $request->query('page', 1)),
            'perPage' => $perPage,
            'orderBy' => $request->query('orderBy', $request->query('order_by')),
            'direction' => $direction === 'asc' ? 'asc' : 'desc',
            'search' => $request->query('search'),
        ];
    }
}
