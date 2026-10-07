<?php

namespace App\Areas\GroupsAdmin\Support;

use Illuminate\Support\Str;

/**
 * SearchFilter (mealie/schema/response/query_search.py) with SearchType.tokenized (SQLite)
 * and MealieModel.filter_search_query (mealie/schema/_mealie/mealie_model.py).
 */
class Search
{
    /** string.punctuation minus ' and " (mealie/db/models/_model_base.py NORMALIZE_PUNCTUATION) */
    private const PUNCTUATION = '!#$%&()*+,-./:;<=>?@[\\]^_`{|}~';

    private const QUOTED = '/(["\'])(?:(?=(\\\\?))\2.)*?\1/';

    public static function punctuationToSpaces(string $value): string
    {
        return strtr($value, self::PUNCTUATION, str_repeat(' ', strlen(self::PUNCTUATION)));
    }

    /** text_unidecode approximation */
    public static function unidecode(string $value): string
    {
        return Str::ascii($value);
    }

    public static function normalize(string $search, bool $normalizeCharacters): string
    {
        $search = self::punctuationToSpaces($search);

        return $normalizeCharacters ? trim(strtolower(self::unidecode($search))) : trim($search);
    }

    /** @return list<string> */
    public static function buildList(string $search): array
    {
        if (preg_match(self::QUOTED, $search)) {
            preg_match_all(self::QUOTED, $search, $m);
            $quoted = array_map(fn ($x) => preg_replace('/[\'"](.*)[\'"]/', '$1', $x), $m[0]);
            $rest = self::punctuationToSpaces(preg_replace(self::QUOTED, '', $search));
            $list = array_merge($quoted, preg_split('/\s+/', trim($rest), -1, PREG_SPLIT_NO_EMPTY));
        } else {
            $list = preg_split('/\s+/', trim(self::punctuationToSpaces($search)), -1, PREG_SPLIT_NO_EMPTY);
        }

        return array_map('trim', $list);
    }

    /**
     * @param  list<string>  $columns
     * @return array{0: \Closure, 1: array{0: string, 1: list<string>}}
     */
    public static function tokenized(string $raw, bool $normalizeCharacters, string $table, array $columns): array
    {
        $search = self::normalize($raw, $normalizeCharacters);
        $tokens = self::buildList($search);

        // An empty token list gives an empty or_(), which SQLAlchemy drops (no filter).
        $where = function ($q) use ($tokens, $columns, $table) {
            foreach ($columns as $column) {
                foreach ($tokens as $token) {
                    $q->orWhereRaw("{$table}.{$column} LIKE ?", ['%'.$token.'%']);
                }
            }
        };

        return [$where, ["({$table}.{$columns[0]} LIKE ?) DESC", ['%'.$search.'%']]];
    }
}
