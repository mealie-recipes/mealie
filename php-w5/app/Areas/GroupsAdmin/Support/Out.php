<?php

namespace App\Areas\GroupsAdmin\Support;

use App\Support\Dates;
use App\Support\Guid;

/**
 * Serializers for the Pydantic response models of this area (camelCase keys, field order as declared).
 * Functions named *Many take a list of rows and batch-load relations.
 */
class Out
{
    private static function g(?string $hex): ?string
    {
        return Guid::fromDb($hex);
    }

    /** @return array<string, list<object>> */
    private static function groupBy(string $table, string $key, array $values, string $order = 'rowid'): array
    {
        $out = [];
        if (! $values) {
            return $out;
        }
        foreach (array_chunk(array_values(array_unique($values)), 500) as $chunk) {
            foreach (Db::table($table)->whereIn($key, $chunk)->orderByRaw($order)->get() as $row) {
                $out[$row->{$key}][] = $row;
            }
        }

        return $out;
    }

    // ---------------------------------------------------------------- groups

    /** ReadGroupPreferences */
    public static function groupPreferences(?object $p): ?array
    {
        if ($p === null) {
            return null;
        }

        return [
            'privateGroup' => Db::bool($p->private_group),
            'showAnnouncements' => Db::bool($p->show_announcements),
            'groupId' => self::g($p->group_id),
            'id' => self::g($p->id),
        ];
    }

    /** AIProviderSettingsOut for a group (null when the group has no settings row). */
    public static function aiSettings(string $groupId): ?array
    {
        $s = Db::table('ai_provider_settings')->where('group_id', $groupId)->first();
        if ($s === null) {
            return null;
        }
        $providers = Db::table('ai_providers')->where('settings_id', $s->id)->orderByRaw('rowid')->get(['id', 'name']);
        $ids = $providers->pluck('id')->all();
        $pick = fn (?string $id) => $id !== null && in_array($id, $ids, true) ? self::g($id) : null;
        $default = $pick($s->default_provider_id);
        $audio = $pick($s->audio_provider_id);
        $image = $pick($s->image_provider_id);

        return [
            'defaultProviderId' => $default,
            'audioProviderId' => $audio,
            'imageProviderId' => $image,
            'providers' => $providers->map(fn ($p) => ['id' => self::g($p->id), 'name' => $p->name])->all(),
            'aiEnabled' => $default !== null,
            'audioProviderEnabled' => $default !== null && $audio !== null,
            'imageProviderEnabled' => $default !== null && $image !== null,
        ];
    }

    /** GroupSummary */
    public static function groupSummary(object $group): array
    {
        return [
            'name' => $group->name,
            'id' => self::g($group->id),
            'slug' => $group->slug,
            'preferences' => self::groupPreferences(Db::table('group_preferences')->where('group_id', $group->id)->first()),
            'aiProviderSettings' => self::aiSettings($group->id),
        ];
    }

    /** ReadWebhook */
    public static function webhook(object $w): array
    {
        $time = $w->scheduled_time;
        if (is_string($time)) {
            $time = preg_replace('/\.0+$/', '', $time);
        }

        return [
            'enabled' => Db::bool($w->enabled),
            'name' => $w->name,
            'url' => $w->url,
            'webhookType' => $w->webhook_type,
            'scheduledTime' => $time,
            'groupId' => self::g($w->group_id),
            'householdId' => self::g($w->household_id),
            'id' => self::g($w->id),
        ];
    }

    /** UserSummary */
    public static function userSummary(object $u): array
    {
        return [
            'id' => self::g($u->id),
            'groupId' => self::g($u->group_id),
            'householdId' => self::g($u->household_id),
            'username' => $u->username,
            'fullName' => $u->full_name,
        ];
    }

    /** GroupInDB */
    public static function groupInDbMany(array $groups): array
    {
        $ids = array_map(fn ($g) => $g->id, $groups);
        $cats = [];
        if ($ids) {
            foreach (Db::table('group_to_categories')->join('categories', 'categories.id', '=', 'group_to_categories.category_id')
                ->whereIn('group_to_categories.group_id', $ids)->orderByRaw('group_to_categories.rowid')
                ->get(['group_to_categories.group_id as gid', 'categories.*']) as $c) {
                $cats[$c->gid][] = $c;
            }
        }
        $webhooks = self::groupBy('webhook_urls', 'group_id', $ids);
        $households = self::groupBy('households', 'group_id', $ids);
        $users = self::groupBy('users', 'group_id', $ids);
        $prefs = self::groupBy('group_preferences', 'group_id', $ids);

        return array_map(fn ($g) => [
            'name' => $g->name,
            'id' => self::g($g->id),
            'slug' => $g->slug,
            'categories' => array_map(fn ($c) => [
                'name' => $c->name,
                'id' => self::g($c->id),
                'groupId' => self::g($c->group_id),
                'slug' => $c->slug,
            ], $cats[$g->id] ?? []),
            'webhooks' => array_map([self::class, 'webhook'], $webhooks[$g->id] ?? []),
            'households' => array_map(fn ($h) => ['id' => self::g($h->id), 'name' => $h->name], $households[$g->id] ?? []),
            'users' => array_map([self::class, 'userSummary'], $users[$g->id] ?? []),
            'preferences' => self::groupPreferences($prefs[$g->id][0] ?? null),
            'aiProviderSettings' => self::aiSettings($g->id),
        ], $groups);
    }

    public static function groupInDb(object $group): array
    {
        return self::groupInDbMany([$group])[0];
    }

    // ---------------------------------------------------------------- households

    /** ReadHouseholdPreferences */
    public static function householdPreferences(?object $p): ?array
    {
        if ($p === null) {
            return null;
        }

        return [
            'privateHousehold' => Db::bool($p->private_household),
            'showAnnouncements' => Db::bool($p->show_announcements),
            'lockRecipeEditsFromOtherHouseholds' => Db::bool($p->lock_recipe_edits_from_other_households),
            'firstDayOfWeek' => (int) $p->first_day_of_week,
            'recipePublic' => Db::bool($p->recipe_public),
            'recipeShowNutrition' => Db::bool($p->recipe_show_nutrition),
            'recipeShowAssets' => Db::bool($p->recipe_show_assets),
            'recipeLandscapeView' => Db::bool($p->recipe_landscape_view),
            'recipeDisableComments' => Db::bool($p->recipe_disable_comments),
            'id' => self::g($p->id),
        ];
    }

    /** HouseholdSummary */
    public static function householdSummaryMany(array $households): array
    {
        $prefs = self::groupBy('household_preferences', 'household_id', array_map(fn ($h) => $h->id, $households));

        return array_map(fn ($h) => [
            'groupId' => self::g($h->group_id),
            'name' => $h->name,
            'id' => self::g($h->id),
            'slug' => $h->slug,
            'preferences' => self::householdPreferences($prefs[$h->id][0] ?? null),
        ], $households);
    }

    public static function householdSummary(object $h): array
    {
        return self::householdSummaryMany([$h])[0];
    }

    /** HouseholdInDB */
    public static function householdInDbMany(array $households): array
    {
        $ids = array_map(fn ($h) => $h->id, $households);
        $summaries = self::householdSummaryMany($households);
        $users = self::groupBy('users', 'household_id', $ids);
        $webhooks = self::groupBy('webhook_urls', 'household_id', $ids);
        $groupNames = Db::table('groups')->whereIn('id', array_map(fn ($h) => $h->group_id, $households) ?: [''])->pluck('name', 'id');

        $out = [];
        foreach ($households as $i => $h) {
            $out[] = $summaries[$i] + [
                'group' => $groupNames[$h->group_id] ?? null,
                'users' => array_map(fn ($u) => ['id' => self::g($u->id), 'fullName' => $u->full_name], $users[$h->id] ?? []),
                'webhooks' => array_map([self::class, 'webhook'], $webhooks[$h->id] ?? []),
            ];
        }

        return $out;
    }

    public static function householdInDb(object $h): array
    {
        return self::householdInDbMany([$h])[0];
    }

    // ---------------------------------------------------------------- users

    /** UserOut */
    public static function userOutMany(array $users): array
    {
        $ids = array_map(fn ($u) => $u->id, $users);
        $tokens = self::groupBy('long_live_tokens', 'user_id', $ids);
        $groups = Db::table('groups')->whereIn('id', array_map(fn ($u) => $u->group_id, $users) ?: [''])->get()->keyBy('id');
        $households = Db::table('households')->whereIn('id', array_filter(array_map(fn ($u) => $u->household_id, $users)) ?: [''])->get()->keyBy('id');

        return array_map(function ($u) use ($tokens, $groups, $households) {
            $group = $groups[$u->group_id] ?? null;
            $household = $u->household_id !== null ? ($households[$u->household_id] ?? null) : null;
            $auth = match ($u->auth_method) {
                'LDAP' => 'LDAP',
                'OIDC' => 'OIDC',
                default => 'Mealie',
            };

            return [
                'id' => self::g($u->id),
                'username' => $u->username,
                'fullName' => $u->full_name,
                'email' => $u->email,
                'authMethod' => $auth,
                'admin' => Db::bool($u->admin),
                'group' => $group?->name,
                'household' => $household?->name,
                'advanced' => Db::bool($u->advanced),
                'showAnnouncements' => Db::bool($u->show_announcements),
                'lastReadAnnouncement' => $u->last_read_announcement,
                'canInvite' => Db::bool($u->can_invite),
                'canManage' => Db::bool($u->can_manage),
                'canManageHousehold' => Db::bool($u->can_manage_household),
                'canOrganize' => Db::bool($u->can_organize),
                'groupId' => self::g($u->group_id),
                'groupSlug' => $group?->slug,
                'householdId' => self::g($u->household_id),
                'householdSlug' => $household?->slug,
                'tokens' => array_map(fn ($t) => [
                    'name' => $t->name,
                    'id' => (int) $t->id,
                    'createdAt' => Dates::out($t->created_at),
                ], $tokens[$u->id] ?? []),
                'cacheKey' => $u->cache_key,
            ];
        }, $users);
    }

    public static function userOut(object $u): array
    {
        return self::userOutMany([$u])[0];
    }

    // ---------------------------------------------------------------- labels / reports / ai

    /** MultiPurposeLabelSummary / MultiPurposeLabelOut */
    public static function label(object $l): array
    {
        return [
            'name' => $l->name,
            'color' => $l->color,
            'groupId' => self::g($l->group_id),
            'id' => self::g($l->id),
        ];
    }

    /** ReportSummary */
    public static function reportSummary(object $r): array
    {
        return [
            'timestamp' => Dates::out($r->timestamp),
            'category' => $r->category,
            'groupId' => self::g($r->group_id),
            'name' => $r->name,
            'status' => $r->status,
            'id' => self::g($r->id),
        ];
    }

    /** ReportOut */
    public static function reportOut(object $r): array
    {
        $entries = Db::table('report_entries')->where('report_id', $r->id)->orderByRaw('rowid')->get();

        return self::reportSummary($r) + [
            'entries' => $entries->map(fn ($e) => [
                'reportId' => self::g($e->report_id),
                'timestamp' => Dates::out($e->timestamp),
                'success' => Db::bool($e->success),
                'message' => $e->message,
                'exception' => $e->exception,
                'id' => self::g($e->id),
            ])->all(),
        ];
    }

    /** dict[str, str] that stays a JSON object when empty */
    private static function kv(string $table, string $providerId): array|object
    {
        $out = [];
        foreach (Db::table($table)->where('provider_id', $providerId)->orderByRaw('rowid')->get() as $row) {
            $out[(string) $row->key_name] = $row->value;
        }

        return $out ?: new \stdClass;
    }

    /** AIProviderOut (api_key is excluded from serialization) */
    public static function aiProvider(object $p): array
    {
        return [
            'name' => $p->name,
            'baseUrl' => $p->base_url,
            'model' => $p->model,
            'timeout' => (int) $p->timeout,
            'requestHeaders' => self::kv('ai_provider_headers', $p->id),
            'requestParams' => self::kv('ai_provider_params', $p->id),
            'id' => self::g($p->id),
        ];
    }

    // ---------------------------------------------------------------- explore

    /** IngredientFood */
    public static function foodMany(array $foods): array
    {
        $ids = array_map(fn ($f) => $f->id, $foods);
        $extras = self::groupBy('ingredient_food_extras', 'ingredient_food_id', $ids);
        $aliases = self::groupBy('ingredient_foods_aliases', 'food_id', $ids);
        $subs = self::groupBy('ingredient_foods_substitutions', 'food_id', $ids, 'position, rowid');
        $labelIds = array_filter(array_map(fn ($f) => $f->label_id, $foods));
        $labels = Db::table('multi_purpose_labels')->whereIn('id', $labelIds ?: [''])->get()->keyBy('id');
        $subFoodIds = [];
        foreach ($subs as $list) {
            foreach ($list as $s) {
                if ($s->substitute_food_id) {
                    $subFoodIds[] = $s->substitute_food_id;
                }
            }
        }
        $subFoods = Db::table('ingredient_foods')->whereIn('id', $subFoodIds ?: [''])->get(['id', 'name', 'plural_name'])->keyBy('id');
        $households = [];
        if ($ids) {
            foreach (array_chunk($ids, 500) as $chunk) {
                foreach (Db::table('households_to_ingredient_foods')->join('households', 'households.id', '=', 'households_to_ingredient_foods.household_id')
                    ->whereIn('households_to_ingredient_foods.food_id', $chunk)->orderByRaw('households_to_ingredient_foods.rowid')
                    ->get(['households_to_ingredient_foods.food_id', 'households.slug']) as $row) {
                    $households[$row->food_id][] = $row->slug;
                }
            }
        }

        return array_map(function ($f) use ($extras, $aliases, $subs, $labels, $subFoods, $households) {
            $extra = [];
            foreach ($extras[$f->id] ?? [] as $e) {
                $extra[(string) $e->key_name] = $e->value;
            }
            $label = $f->label_id !== null ? ($labels[$f->label_id] ?? null) : null;

            return [
                'id' => self::g($f->id),
                'name' => $f->name,
                'pluralName' => $f->plural_name,
                'description' => $f->description ?? '',
                'extras' => $extra ?: new \stdClass,
                'labelId' => self::g($f->label_id),
                'aliases' => array_map(fn ($a) => ['name' => $a->name], $aliases[$f->id] ?? []),
                'substitutions' => array_map(function ($s) use ($subFoods) {
                    $sf = $s->substitute_food_id ? ($subFoods[$s->substitute_food_id] ?? null) : null;

                    return [
                        'substituteFoodId' => self::g($s->substitute_food_id),
                        'note' => $s->note,
                        'substituteFood' => $sf ? ['id' => self::g($sf->id), 'name' => $sf->name, 'pluralName' => $sf->plural_name] : null,
                    ];
                }, $subs[$f->id] ?? []),
                'householdsWithIngredientFood' => $households[$f->id] ?? [],
                'label' => $label ? self::label($label) : null,
                'createdAt' => Dates::out($f->created_at),
                'updatedAt' => Dates::out($f->update_at),
            ];
        }, $foods);
    }

    /** recipe_count subquery used by RepositoryCategories / RepositoryTags */
    public static function recipeCountSql(string $table): string
    {
        return $table === 'categories'
            ? '(SELECT count(recipes_to_categories.recipe_id) FROM recipes_to_categories WHERE recipes_to_categories.category_id = categories.id) AS recipe_count'
            : '(SELECT count(recipes_to_tags.recipe_id) FROM recipes_to_tags WHERE recipes_to_tags.tag_id = tags.id) AS recipe_count';
    }

    /** RecipeTag / RecipeCategory (pagination items) */
    public static function recipeTag(object $t): array
    {
        return [
            'id' => self::g($t->id),
            'groupId' => self::g($t->group_id),
            'name' => $t->name,
            'slug' => $t->slug,
            'recipeCount' => (int) ($t->recipe_count ?? 0),
        ];
    }

    /** CategoryOut */
    public static function categoryOut(object $c): array
    {
        return [
            'name' => $c->name,
            'id' => self::g($c->id),
            'groupId' => self::g($c->group_id),
            'slug' => $c->slug,
            'recipeCount' => (int) ($c->recipe_count ?? 0),
        ];
    }

    /** TagOut */
    public static function tagOut(object $t): array
    {
        return [
            'name' => $t->name,
            'groupId' => self::g($t->group_id),
            'id' => self::g($t->id),
            'slug' => $t->slug,
            'recipeCount' => (int) ($t->recipe_count ?? 0),
        ];
    }

    /** @return array<string, list<string>> tool id => household slugs */
    private static function toolHouseholds(array $toolIds): array
    {
        $out = [];
        if (! $toolIds) {
            return $out;
        }
        foreach (Db::table('households_to_tools')->join('households', 'households.id', '=', 'households_to_tools.household_id')
            ->whereIn('households_to_tools.tool_id', $toolIds)->orderByRaw('households_to_tools.rowid')
            ->get(['households_to_tools.tool_id', 'households.slug']) as $row) {
            $out[$row->tool_id][] = $row->slug;
        }

        return $out;
    }

    /** RecipeTool (pagination items) */
    public static function recipeToolMany(array $tools): array
    {
        $hh = self::toolHouseholds(array_map(fn ($t) => $t->id, $tools));

        return array_map(fn ($t) => [
            'id' => self::g($t->id),
            'groupId' => self::g($t->group_id),
            'name' => $t->name,
            'slug' => $t->slug,
            'recipeCount' => 0,
            'householdsWithTool' => $hh[$t->id] ?? [],
        ], $tools);
    }

    /** RecipeToolOut */
    public static function recipeToolOut(object $t): array
    {
        $hh = self::toolHouseholds([$t->id]);

        return [
            'name' => $t->name,
            'householdsWithTool' => $hh[$t->id] ?? [],
            'id' => self::g($t->id),
            'groupId' => self::g($t->group_id),
            'slug' => $t->slug,
        ];
    }
}
