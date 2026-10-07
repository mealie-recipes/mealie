<?php

namespace App\Areas\Households\Support;

use App\Support\Dates;
use App\Support\Guid;
use Illuminate\Database\Connection;
use Illuminate\Support\Facades\DB;

/** Row -> JSON for this area's Pydantic response models (field order = schema order). */
class Out
{
    public static function db(): Connection
    {
        return DB::connection('mealie');
    }

    // ---------------------------------------------------------------- users

    /** mealie/schema/user/user.py UserOut */
    public static function user(object $u): array
    {
        $db = self::db();
        $group = $db->table('groups')->where('id', $u->group_id)->first();
        $household = $u->household_id ? $db->table('households')->where('id', $u->household_id)->first() : null;
        $tokens = $db->table('long_live_tokens')->where('user_id', $u->id)->orderBy('id')->get()
            ->map(fn ($t) => ['name' => $t->name, 'id' => (int) $t->id, 'createdAt' => Dates::out($t->created_at)])->all();

        return [
            'id' => Guid::fromDb($u->id),
            'username' => $u->username,
            'fullName' => $u->full_name,
            'email' => $u->email,
            'authMethod' => match ($u->auth_method) {
                'LDAP' => 'LDAP',
                'OIDC' => 'OIDC',
                default => 'Mealie',
            },
            'admin' => (bool) $u->admin,
            'group' => $group?->name,
            'household' => $household?->name,
            'advanced' => (bool) $u->advanced,
            'showAnnouncements' => (bool) $u->show_announcements,
            'lastReadAnnouncement' => $u->last_read_announcement,
            'canInvite' => (bool) $u->can_invite,
            'canManage' => (bool) $u->can_manage,
            'canManageHousehold' => (bool) $u->can_manage_household,
            'canOrganize' => (bool) $u->can_organize,
            'groupId' => Guid::fromDb($u->group_id),
            'groupSlug' => $group?->slug,
            'householdId' => Guid::fromDb($u->household_id),
            'householdSlug' => $household?->slug,
            'tokens' => $tokens,
            'cacheKey' => $u->cache_key,
        ];
    }

    // ---------------------------------------------------------------- households

    /** mealie/schema/household/household_preferences.py ReadHouseholdPreferences */
    public static function preferences(?object $p): ?array
    {
        if ($p === null) {
            return null;
        }

        return [
            'privateHousehold' => (bool) ($p->private_household ?? true),
            'showAnnouncements' => (bool) ($p->show_announcements ?? true),
            'lockRecipeEditsFromOtherHouseholds' => (bool) ($p->lock_recipe_edits_from_other_households ?? true),
            'firstDayOfWeek' => (int) ($p->first_day_of_week ?? 0),
            'recipePublic' => (bool) ($p->recipe_public ?? true),
            'recipeShowNutrition' => (bool) ($p->recipe_show_nutrition ?? false),
            'recipeShowAssets' => (bool) ($p->recipe_show_assets ?? false),
            'recipeLandscapeView' => (bool) ($p->recipe_landscape_view ?? false),
            'recipeDisableComments' => (bool) ($p->recipe_disable_comments ?? false),
            'id' => Guid::fromDb($p->id),
        ];
    }

    /** HouseholdInDB */
    public static function household(object $h): array
    {
        $db = self::db();
        $prefs = $db->table('household_preferences')->where('household_id', $h->id)->first();
        $group = $db->table('groups')->where('id', $h->group_id)->first();
        $users = $db->table('users')->where('household_id', $h->id)->orderBy('rowid')->get()
            ->map(fn ($u) => ['id' => Guid::fromDb($u->id), 'fullName' => $u->full_name])->all();
        $webhooks = $db->table('webhook_urls')->where('household_id', $h->id)->orderBy('rowid')->get()
            ->map(fn ($w) => self::webhook($w))->all();

        return [
            'groupId' => Guid::fromDb($h->group_id),
            'name' => $h->name,
            'id' => Guid::fromDb($h->id),
            'slug' => $h->slug,
            'preferences' => self::preferences($prefs),
            'group' => $group?->name,
            'users' => $users,
            'webhooks' => $webhooks,
        ];
    }

    // ---------------------------------------------------------------- webhooks

    /** "13:05:00.000000" (SQLAlchemy Time on SQLite) -> Pydantic time "13:05:00" */
    public static function time(?string $v): ?string
    {
        if ($v === null) {
            return null;
        }
        if (preg_match('/^(\d{2}:\d{2}:\d{2})(?:\.(\d+))?$/', $v, $m)) {
            $frac = isset($m[2]) ? rtrim(str_pad($m[2], 6, '0'), '0') : '';

            return $frac === '' ? $m[1] : $m[1].'.'.str_pad($m[2], 6, '0');
        }

        return $v;
    }

    /** ReadWebhook */
    public static function webhook(object $w): array
    {
        return [
            'enabled' => (bool) $w->enabled,
            'name' => $w->name,
            'url' => $w->url,
            'webhookType' => $w->webhook_type,
            'scheduledTime' => self::time($w->scheduled_time),
            'groupId' => Guid::fromDb($w->group_id),
            'householdId' => Guid::fromDb($w->household_id),
            'id' => Guid::fromDb($w->id),
        ];
    }

    // ---------------------------------------------------------------- cookbooks / rules

    public static function queryFilterJson(?string $filter): array
    {
        // QueryFilterBuilder.as_json_model(); parsing non-empty filters is out of scope.
        return ['parts' => []];
    }

    /** ReadCookBook */
    public static function cookbook(object $c): array
    {
        $household = $c->household_id ? self::db()->table('households')->where('id', $c->household_id)->first() : null;

        return [
            'name' => $c->name,
            'description' => $c->description ?? '',
            'slug' => $c->slug,
            'position' => (int) $c->position,
            'public' => (bool) $c->public,
            'queryFilterString' => $c->query_filter_string,
            'groupId' => Guid::fromDb($c->group_id),
            'householdId' => Guid::fromDb($c->household_id),
            'id' => Guid::fromDb($c->id),
            'queryFilter' => self::queryFilterJson($c->query_filter_string),
            'household' => $household ? ['id' => Guid::fromDb($household->id), 'name' => $household->name] : null,
        ];
    }

    /** PlanRulesOut */
    public static function planRule(object $r): array
    {
        return [
            'day' => $r->day,
            'entryType' => $r->entry_type,
            'queryFilterString' => $r->query_filter_string,
            'groupId' => Guid::fromDb($r->group_id),
            'householdId' => Guid::fromDb($r->household_id),
            'id' => Guid::fromDb($r->id),
            'queryFilter' => self::queryFilterJson($r->query_filter_string),
        ];
    }

    // ---------------------------------------------------------------- notifiers / actions / invites

    public const NOTIFIER_OPTIONS = [
        'test_message', 'webhook_task',
        'recipe_created', 'recipe_updated', 'recipe_deleted',
        'user_signup',
        'data_migrations', 'data_export', 'data_import',
        'mealplan_entry_created', 'mealplan_entry_updated', 'mealplan_entry_deleted',
        'shopping_list_created', 'shopping_list_updated', 'shopping_list_deleted',
        'cookbook_created', 'cookbook_updated', 'cookbook_deleted',
        'tag_created', 'tag_updated', 'tag_deleted',
        'category_created', 'category_updated', 'category_deleted',
        'label_created', 'label_updated', 'label_deleted',
    ];

    /** GroupEventNotifierOut */
    public static function notifier(object $n): array
    {
        $o = self::db()->table('group_events_notifier_options')->where('event_notifier_id', $n->id)->first();
        $options = null;
        if ($o !== null) {
            $options = [];
            foreach (self::NOTIFIER_OPTIONS as $key) {
                $options[\App\Support\Json::camel($key)] = (bool) ($o->{$key} ?? false);
            }
            $options['id'] = Guid::fromDb($o->id);
        }

        return [
            'id' => Guid::fromDb($n->id),
            'name' => $n->name,
            'enabled' => (bool) $n->enabled,
            'groupId' => Guid::fromDb($n->group_id),
            'householdId' => Guid::fromDb($n->household_id),
            'options' => $options,
        ];
    }

    /** GroupRecipeActionOut */
    public static function recipeAction(object $a): array
    {
        return [
            'actionType' => $a->action_type,
            'title' => $a->title,
            'url' => $a->url,
            'groupId' => Guid::fromDb($a->group_id),
            'householdId' => Guid::fromDb($a->household_id),
            'id' => Guid::fromDb($a->id),
        ];
    }

    /** ReadInviteToken */
    public static function inviteToken(object $t): array
    {
        return [
            'token' => $t->token,
            'usesLeft' => (int) $t->uses_left,
            'groupId' => Guid::fromDb($t->group_id),
            'householdId' => Guid::fromDb($t->household_id),
        ];
    }

    // ---------------------------------------------------------------- meal plans

    /** ReadPlanEntry */
    public static function planEntry(object $m): array
    {
        $db = self::db();
        $user = $m->user_id ? $db->table('users')->where('id', $m->user_id)->first() : null;
        $recipe = $m->recipe_id ? $db->table('recipes')->where('id', $m->recipe_id)->first() : null;

        return [
            'date' => Dates::date($m->date),
            'entryType' => $m->entry_type,
            'title' => $m->title,
            'text' => $m->text,
            'recipeId' => Guid::fromDb($m->recipe_id),
            'id' => (int) $m->id,
            'groupId' => Guid::fromDb($m->group_id),
            'userId' => Guid::fromDb($m->user_id),
            'householdId' => Guid::fromDb($user?->household_id),
            'recipe' => $recipe ? self::recipeSummary($recipe) : null,
        ];
    }

    /** mealie/schema/recipe/recipe.py RecipeSummary (as embedded via a relationship: recipeCount is 0). */
    public static function recipeSummary(object $r): array
    {
        $db = self::db();
        $user = $r->user_id ? $db->table('users')->where('id', $r->user_id)->first() : null;

        $organizer = fn (object $row) => [
            'id' => Guid::fromDb($row->id),
            'groupId' => Guid::fromDb($row->group_id),
            'name' => $row->name,
            'slug' => $row->slug,
            'recipeCount' => 0,
        ];

        $categories = $db->table('recipes_to_categories as l')->join('categories as c', 'c.id', '=', 'l.category_id')
            ->where('l.recipe_id', $r->id)->orderBy('l.rowid')->select('c.*')->get()->map($organizer)->all();
        $tags = $db->table('recipes_to_tags as l')->join('tags as t', 't.id', '=', 'l.tag_id')
            ->where('l.recipe_id', $r->id)->orderBy('l.rowid')->select('t.*')->get()->map($organizer)->all();
        $tools = $db->table('recipes_to_tools as l')->join('tools as t', 't.id', '=', 'l.tool_id')
            ->where('l.recipe_id', $r->id)->orderBy('l.rowid')->select('t.*')->get()
            ->map(function ($t) use ($organizer, $db) {
                $out = $organizer($t);
                $out['householdsWithTool'] = $db->table('households_to_tools as ht')
                    ->join('households as h', 'h.id', '=', 'ht.household_id')
                    ->where('ht.tool_id', $t->id)->orderBy('ht.rowid')->pluck('h.slug')->all();

                return $out;
            })->all();

        $str = fn ($v) => $v === null ? null : (string) $v;

        return [
            'id' => Guid::fromDb($r->id),
            'userId' => Guid::fromDb($r->user_id),
            'householdId' => Guid::fromDb($user?->household_id),
            'groupId' => Guid::fromDb($r->group_id),
            'name' => $r->name,
            'slug' => $r->slug ?? '',
            'image' => $r->image,
            'recipeServings' => (float) ($r->recipe_servings ?: 0),
            'recipeYieldQuantity' => (float) ($r->recipe_yield_quantity ?: 0),
            'recipeYield' => $str($r->recipe_yield),
            'totalTime' => $str($r->total_time),
            'prepTime' => $str($r->prep_time),
            'cookTime' => $str($r->cook_time),
            'performTime' => $str($r->perform_time),
            'description' => $r->description,
            'recipeCategory' => $categories,
            'tags' => $tags,
            'tools' => $tools,
            'rating' => Http::float($r->rating),
            'orgURL' => $r->org_url,
            'dateAdded' => Dates::date($r->date_added),
            'dateUpdated' => Dates::out($r->date_updated),
            'createdAt' => Dates::out($r->created_at),
            'updatedAt' => Dates::out($r->update_at),
            'lastMade' => Dates::out($r->last_made),
        ];
    }

    // ---------------------------------------------------------------- shared

    /** RecipeShareTokenSummary */
    public static function shareTokenSummary(object $t): array
    {
        return [
            'recipeId' => Guid::fromDb($t->recipe_id),
            'expiresAt' => Dates::out($t->expires_at),
            'groupId' => Guid::fromDb($t->group_id),
            'id' => Guid::fromDb($t->id),
            'createdAt' => Dates::out($t->created_at),
        ];
    }
}
