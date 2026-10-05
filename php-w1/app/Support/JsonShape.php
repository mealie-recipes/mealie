<?php

namespace App\Support;

final class JsonShape
{
    public static function camel(mixed $value): mixed
    {
        if (! is_array($value)) {
            return $value;
        }

        $isList = array_is_list($value);
        $out = [];
        foreach ($value as $key => $item) {
            $out[$isList ? $key : self::key((string) $key)] = self::camel($item);
        }

        return $out;
    }

    public static function key(string $key): string
    {
        return match ($key) {
            'org_url' => 'orgURL',
            'update_at', 'updated_at' => 'updatedAt',
            default => lcfirst(str_replace(' ', '', ucwords(str_replace('_', ' ', $key)))),
        };
    }

    public static function bool(mixed $value): bool
    {
        return filter_var($value, FILTER_VALIDATE_BOOL);
    }

    public static function dateTime(mixed $value): ?string
    {
        if ($value === null || $value === '') {
            return null;
        }

        $text = str_replace(' ', 'T', (string) $value);
        if (! str_contains($text, 'Z') && ! preg_match('/[+-]\d{2}:?\d{0,2}$/', $text)) {
            $text .= 'Z';
        }

        return $text;
    }

    public static function date(mixed $value): ?string
    {
        if ($value === null || $value === '') {
            return null;
        }

        return substr((string) $value, 0, 10);
    }

    /**
     * @param  array<string, mixed>  $row
     * @param  list<string>  $bools
     * @param  list<string>  $dates
     * @param  list<string>  $dateTimes
     * @param  list<string>  $ids
     * @return array<string, mixed>
     */
    public static function row(array $row, array $bools = [], array $dates = [], array $dateTimes = [], array $ids = []): array
    {
        foreach ($ids as $column) {
            if (array_key_exists($column, $row)) {
                $row[$column] = Guid::dashed(is_string($row[$column]) ? $row[$column] : null);
            }
        }
        foreach ($bools as $column) {
            if (array_key_exists($column, $row)) {
                $row[$column] = self::bool($row[$column]);
            }
        }
        foreach ($dates as $column) {
            if (array_key_exists($column, $row)) {
                $row[$column] = self::date($row[$column]);
            }
        }
        foreach ($dateTimes as $column) {
            if (array_key_exists($column, $row)) {
                $row[$column] = self::dateTime($row[$column]);
            }
        }
        if (array_key_exists('update_at', $row)) {
            $row['updated_at'] = self::dateTime($row['update_at']);
            unset($row['update_at']);
        }

        return $row;
    }
}
