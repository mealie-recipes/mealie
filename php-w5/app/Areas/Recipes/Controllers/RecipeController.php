<?php

namespace App\Areas\Recipes\Controllers;

use App\Areas\Recipes\Support\Db;
use App\Areas\Recipes\Support\Input;
use App\Areas\Recipes\Support\Out;
use App\Areas\Recipes\Support\RecipeMap;
use App\Support\CurrentUser;
use App\Support\Errors;
use App\Support\Guid;
use App\Support\Pagination;
use Illuminate\Database\Query\Builder;
use Illuminate\Http\Request;

/**
 * Read-side of mealie/routes/recipe/: exports.py, recipe_crud_routes.py (get_all, get_one),
 * shared_routes.py (get_shared_recipe), bulk_actions.py (get_exported_data).
 */
class RecipeController extends Base
{
    /** GET /api/recipes/exports — TemplateService.templates */
    public function formats()
    {
        return $this->json(['json' => ['raw'], 'zip' => ['zip']]);
    }

    /** list[UUID4 | str] query param: ids as given, slugs resolved to ids (RepositoryRecipes._uuids_for_items) */
    private function idsFor(Request $request, string $param, ?string $table): ?array
    {
        $values = $this->multi($request, $param);
        if ($values === []) {
            return null;
        }
        $ids = [];
        $slugs = [];
        foreach ($values as $v) {
            if (Guid::isUuid($v)) {
                $ids[] = Guid::toDb($v);
            } else {
                $slugs[] = $v;
            }
        }
        if ($slugs !== [] && $table !== null) {
            $ids = array_merge($ids, Db::table($table)->whereIn('slug', $slugs)->pluck('id')->all());
        }

        return $ids;
    }

    /** Repeated query params (?tags=a&tags=b) as Starlette sees them. */
    private function multi(Request $request, string $param): array
    {
        $out = [];
        foreach (explode('&', (string) $request->server('QUERY_STRING', '')) as $pair) {
            [$k, $v] = array_pad(explode('=', $pair, 2), 2, '');
            if (urldecode($k) === $param) {
                $out[] = urldecode($v);
            }
        }

        return $out;
    }

    private function boolParam(Request $request, string $name): bool
    {
        $v = $request->query($name);
        if ($v === null) {
            return false;
        }
        $l = strtolower((string) $v);
        if (in_array($l, ['1', 'true', 't', 'yes', 'y', 'on'], true)) {
            return true;
        }
        if (in_array($l, ['0', 'false', 'f', 'no', 'n', 'off'], true)) {
            return false;
        }
        Errors::validation("1 validation error: {'type': 'bool_parsing', 'loc': ('query', '{$name}'), 'msg': 'Input should be a valid boolean, unable to interpret input', 'input': '{$v}'}");
    }

    /** RepositoryRecipes._build_recipe_filter (mealie/repos/repository_recipes.py:308) */
    private function organizerFilter(Builder $q, ?array $ids, string $link, string $fk, bool $all): void
    {
        if (! $ids) {
            return;
        }
        $groups = $all ? array_map(fn ($id) => [$id], $ids) : [$ids];
        foreach ($groups as $set) {
            $q->whereExists(fn ($s) => $s->from($link)->whereColumn("{$link}.recipe_id", 'recipes.id')->whereIn("{$link}.{$fk}", $set));
        }
    }

    private function foodFilter(Builder $q, array $foods, bool $all): void
    {
        $groups = $all ? array_map(fn ($id) => [$id], $foods) : [$foods];
        foreach ($groups as $set) {
            $q->whereExists(fn ($s) => $s->from('recipes_ingredients as fi')
                ->whereColumn('fi.recipe_id', 'recipes.id')
                ->where(fn ($w) => $w->whereIn('fi.food_id', $set)
                    ->orWhereExists(fn ($x) => $x->from('recipes_ingredients_substitutions as fs')
                        ->whereColumn('fs.ingredient_id', 'fi.id')->whereIn('fs.substitute_food_id', $set))));
        }
    }

    /** GET /api/recipes — group-wide RecipeSummary page, serialised by orjson */
    public function index(Request $request)
    {
        $require = [
            'categories' => $this->boolParam($request, 'requireAllCategories'),
            'tags' => $this->boolParam($request, 'requireAllTags'),
            'tools' => $this->boolParam($request, 'requireAllTools'),
            'foods' => $this->boolParam($request, 'requireAllFoods'),
        ];
        $foods = array_map(fn ($f) => Guid::toDb($f) ?? $f, $this->multi($request, 'foods'));

        $q = RecipeMap::query($this->groupId());
        $this->organizerFilter($q, $this->idsFor($request, 'categories', 'categories'), 'recipes_to_categories', 'category_id', $require['categories']);
        $this->organizerFilter($q, $this->idsFor($request, 'tags', 'tags'), 'recipes_to_tags', 'tag_id', $require['tags']);
        $this->organizerFilter($q, $this->idsFor($request, 'tools', 'tools'), 'recipes_to_tools', 'tool_id', $require['tools']);
        if ($foods !== []) {
            $this->foodFilter($q, $foods, $require['foods']);
        }
        if (($households = $this->idsFor($request, 'households', 'households')) !== null) {
            $q->whereIn('ru.household_id', $households);
        }

        $uid = CurrentUser::id(); // hex from the users row
        $rating = "CAST(CASE WHEN EXISTS (SELECT 1 FROM users_to_recipes ur WHERE ur.recipe_id = recipes.id AND ur.user_id = '{$uid}' AND ur.rating IS NOT NULL AND ur.rating > 0) "
            ."THEN (SELECT max(ur2.rating) FROM users_to_recipes ur2 WHERE ur2.recipe_id = recipes.id AND ur2.user_id = '{$uid}') "
            .'ELSE (CASE WHEN recipes.rating = 0 THEN NULL ELSE recipes.rating END) END AS FLOAT)';
        $lastMade = "coalesce((SELECT hr.last_made FROM households_to_recipes hr WHERE hr.recipe_id = recipes.id AND hr.household_id = (SELECT u.household_id FROM users u WHERE u.id = '{$uid}')), '1900-01-01 00:00:00.000000')";

        $result = Pagination::page($request, $q, fn ($rows) => $rows, '/recipes', [
            'table' => 'recipes',
            'columns' => [
                'created_at' => false, 'update_at' => false, 'id' => false, 'slug' => true, 'group_id' => false,
                'user_id' => false, 'name' => true, 'description' => true, 'image' => true,
                'total_time' => true, 'prep_time' => true, 'perform_time' => true, 'cook_time' => true,
                'recipe_yield' => true, 'recipe_yield_quantity' => false, 'recipe_servings' => false,
                'rating' => $rating, 'org_url' => true, 'date_added' => false, 'date_updated' => false,
                'last_made' => $lastMade, 'name_normalized' => true, 'description_normalized' => true,
                'is_ocr_recipe' => false,
            ],
            'search' => ['recipes.name_normalized', 'recipes.description_normalized'],
            'normalizeSearch' => true,
            'searchExtra' => function (Builder $w, array $terms) {
                $w->orWhereExists(function ($s) use ($terms) {
                    $s->from('recipes_ingredients as si')->whereColumn('si.recipe_id', 'recipes.id')
                        ->where(function ($x) use ($terms) {
                            foreach ($terms as $t) {
                                $x->orWhere('si.note_normalized', 'like', "%{$t}%")->orWhere('si.original_text_normalized', 'like', "%{$t}%");
                            }
                        });
                });
            },
            'guides' => 'merge',
        ]);
        $result['items'] = RecipeMap::summaries($result['items'], true);

        return $this->json($result);
    }

    /** RecipeService.get_one: a parseable UUID (any version) is looked up by id, anything else by slug */
    public function show(string $slug)
    {
        $q = RecipeMap::anyQuery($this->groupId());
        if (Guid::isUuid($slug)) {
            $q->where('recipes.id', Guid::toDb($slug));
        } else {
            $q->where('recipes.slug', $slug);
        }
        $row = $q->first();
        if (! $row) {
            Errors::errorResponse(404, 'No Entry Found');
        }

        return $this->crud(RecipeMap::full($row));
    }

    /** GET /api/recipes/shared/{token_id} — public */
    public function shared(string $token_id)
    {
        $id = Input::pathUuid4($token_id, 'token_id');
        $token = Db::table('recipe_share_tokens')->where('id', $id)->first();
        if ($token && strtotime($token->expires_at.' UTC') < time()) {
            Db::table('recipe_share_tokens')->where('id', $id)->delete();
            $token = null;
        }
        $row = $token ? RecipeMap::anyQuery(null)->where('recipes.id', $token->recipe_id)->first() : null;
        if (! $row) {
            Errors::errorResponse(404, 'Token Not Found');
        }

        return $this->json(RecipeMap::full($row));
    }

    /** GET /api/recipes/bulk-actions/export — group_exports.page_all(per_page=-1), created_at desc */
    public function exports()
    {
        $rows = Db::table('group_data_exports')->where('group_id', $this->groupId())->orderByDesc('created_at')->get();

        return $this->json($rows->map(fn ($r) => [
            'id' => Out::id($r->id),
            'groupId' => Out::id($r->group_id),
            'name' => $r->name,
            'filename' => $r->filename,
            'path' => $r->path,
            'size' => $r->size,
            'expires' => Out::dt($r->expires),
        ])->all());
    }
}
