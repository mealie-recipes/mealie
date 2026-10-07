<?php

namespace App\Areas\GroupsAdmin\Support;

/**
 * Deletes rows together with the rows that reference them, following the SQLite foreign keys.
 * Stands in for the SQLAlchemy `cascade="all, delete-orphan"` chains of Group (mealie/db/models/group/group.py).
 * The users table is never deleted through this; references to deleted rows from users are nulled.
 */
class Cascade
{
    /** @var array<string, list<array{table: string, from: string, to: string}>>|null */
    private static ?array $referencing = null;

    private static function referencing(string $table): array
    {
        if (self::$referencing === null) {
            self::$referencing = [];
            foreach (Db::conn()->select("SELECT name FROM sqlite_master WHERE type = 'table'") as $t) {
                foreach (Db::conn()->select("PRAGMA foreign_key_list(\"{$t->name}\")") as $fk) {
                    self::$referencing[$fk->table][] = ['table' => $t->name, 'from' => $fk->from, 'to' => $fk->to ?? 'id'];
                }
            }
        }

        return self::$referencing[$table] ?? [];
    }

    /** Delete rows of $table where $column is in $values, children first. */
    public static function delete(string $table, string $column, array $values, int $depth = 0): void
    {
        if (! $values || $depth > 12) {
            return;
        }
        foreach (self::referencing($table) as $ref) {
            if ($ref['table'] === $table) {
                continue;
            }
            $keys = Db::table($table)->whereIn($column, $values)->pluck($ref['to'])->filter(fn ($v) => $v !== null)->all();
            if (! $keys) {
                continue;
            }
            if ($ref['table'] === 'users') {
                Db::table('users')->whereIn($ref['from'], $keys)->update([$ref['from'] => null]);

                continue;
            }
            self::delete($ref['table'], $ref['from'], $keys, $depth + 1);
        }
        Db::table($table)->whereIn($column, $values)->delete();
    }
}
