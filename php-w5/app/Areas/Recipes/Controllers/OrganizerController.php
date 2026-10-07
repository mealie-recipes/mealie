<?php

namespace App\Areas\Recipes\Controllers;

use App\Areas\Recipes\Support\Db;
use App\Areas\Recipes\Support\Input;
use App\Areas\Recipes\Support\Map;
use App\Areas\Recipes\Support\Out;
use App\Areas\Recipes\Support\Paginator;
use App\Areas\Recipes\Support\RecipeMap;
use App\Areas\Recipes\Support\Text;
use App\Support\Errors;
use App\Support\Guid;
use Illuminate\Database\Query\Builder;
use Illuminate\Http\Request;

/**
 * mealie/routes/organizers/controller_categories.py, controller_tags.py, controller_tools.py
 */
class OrganizerController extends Base
{
    private const COLUMNS = ['created_at' => 'other', 'update_at' => 'other', 'id' => 'other', 'group_id' => 'other', 'name' => 'string', 'slug' => 'string'];

    /** categories / tags with the recipe_count expression (RepositoryCategories._query, repository_factory.py:93) */
    private function countedQuery(string $table): Builder
    {
        [$link, $fk] = $table === 'categories' ? ['recipes_to_categories', 'category_id'] : ['recipes_to_tags', 'tag_id'];

        return Db::table($table)
            ->select("{$table}.*")
            ->selectRaw("(SELECT count({$link}.recipe_id) FROM {$link} WHERE {$link}.{$fk} = {$table}.id) AS recipe_count")
            ->where("{$table}.group_id", $this->groupId());
    }

    private function findCounted(string $table, string $id): ?object
    {
        return $this->countedQuery($table)->where("{$table}.id", $id)->first();
    }

    // ===================================================================== list

    private function listOrganizer(Request $request, string $table, string $route)
    {
        $query = $table === 'tools'
            ? Db::table('tools')->select('tools.*')->where('tools.group_id', $this->groupId())
            : $this->countedQuery($table);

        $households = [];
        $result = Paginator::page($request, $query, fn ($r) => $r, $route, [
            'table' => $table,
            'columns' => self::COLUMNS + ($table === 'tools' ? ['on_hand' => 'other'] : []),
            'search' => ["{$table}.name"],
        ]);
        if ($table === 'tools') {
            $households = Map::toolHouseholds(array_map(fn ($r) => $r->id, $result['items']));
            $result['items'] = array_map(fn ($r) => Map::recipeTool($r, $households), $result['items']);
        } else {
            $result['items'] = array_map(fn ($r) => Map::recipeTag($r), $result['items']);
        }

        return $this->json($result);
    }

    public function categoriesIndex(Request $request)
    {
        return $this->listOrganizer($request, 'categories', '/categories');
    }

    public function tagsIndex(Request $request)
    {
        return $this->listOrganizer($request, 'tags', '/tags');
    }

    public function toolsIndex(Request $request)
    {
        return $this->listOrganizer($request, 'tools', '/tools');
    }

    // ===================================================================== create / update (categories, tags)

    /** Category/Tag __init__: name stripped, slug = slugify(name), name must not be "" */
    private function saveNamed(string $table, Request $request, ?string $id): object
    {
        $in = Input::fromRequest($request);
        $name = $in->str('name');
        $in->check();
        $this->canOrganize();

        $stripped = trim($name);
        $slug = Text::slugify($table === 'tags' ? $stripped : $name);

        return $this->write(function () use ($table, $id, $stripped, $slug) {
            if ($stripped === '') {
                Errors::errorResponse(400, self::DEFAULT_MSG, '');
            }
            $now = $this->now();
            if ($id === null) {
                $id = Guid::new();
                Db::table($table)->insert([
                    'created_at' => $now, 'update_at' => $this->now(), 'id' => $id,
                    'group_id' => $this->groupId(), 'name' => $stripped, 'slug' => $slug,
                ]);
            } else {
                Db::table($table)->where('id', $id)->update(['name' => $stripped, 'slug' => $slug, 'update_at' => $now]);
            }

            return $this->findCounted($table, $id);
        }, self::DEFAULT_MSG);
    }

    public function categoriesStore(Request $request)
    {
        $row = $this->saveNamed('categories', $request, null);
        $row->recipe_count = 0;

        return $this->json(Map::categoryOut($row), 201);
    }

    public function tagsStore(Request $request)
    {
        $row = $this->saveNamed('tags', $request, null);
        $row->recipe_count = 0;

        return $this->json(Map::tagOut($row), 201);
    }

    public function categoriesUpdate(Request $request, string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $in = Input::fromRequest($request);
        $in->str('name');
        $in->check();
        $this->canOrganize();
        if (! $this->findCounted('categories', $id)) {
            $this->notFound();
        }
        $row = $this->saveNamed('categories', $request, $id);

        return $this->json(['id' => Out::id($row->id), 'slug' => $row->slug, 'name' => $row->name]);
    }

    public function tagsUpdate(Request $request, string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $in = Input::fromRequest($request);
        $in->str('name');
        $in->check();
        $this->canOrganize();
        // controller_tags.py:93 calls repo.update directly: a missing id raises NoResultFound (unhandled -> 500)
        if (! $this->findCounted('tags', $id)) {
            Db::serverError();
        }
        $row = $this->saveNamed('tags', $request, $id);

        return $this->json(Map::categoryBase($row) + ['recipes' => []]);
    }

    // ===================================================================== empty / merge

    public function categoriesEmpty()
    {
        // RepositoryCategories.get_empty is not group-filtered (repository_factory.py:103)
        $rows = Db::table('categories')
            ->whereNotExists(fn ($q) => $q->from('recipes_to_categories')->whereColumn('recipes_to_categories.category_id', 'categories.id'))
            ->orderBy('rowid')->get();

        return $this->json($rows->map(fn ($r) => Map::categoryBase($r))->all());
    }

    public function tagsEmpty()
    {
        // no response_model: FastAPI encodes the raw ORM objects (vars(obj)), keys in this order
        $rows = Db::table('tags')
            ->whereNotExists(fn ($q) => $q->from('recipes_to_tags')->whereColumn('recipes_to_tags.tag_id', 'tags.id'))
            ->orderBy('rowid')->get();

        return $this->json($rows->map(fn ($r) => [
            'recipe_count' => 0,
            'group_id' => Out::id($r->group_id),
            'slug' => $r->slug,
            'update_at' => Out::dtOrjson($r->update_at),
            'id' => Out::id($r->id),
            'name' => $r->name,
            'created_at' => Out::dtOrjson($r->created_at),
        ])->all());
    }

    private function merge(Request $request, string $table, string $noun)
    {
        $in = Input::fromRequest($request);
        $from = $in->uuid4('from_id');
        $to = $in->uuid4('to_id');
        $in->check();
        $this->canOrganize();

        if ($from === $to) {
            Errors::http(400, 'from_id and to_id must be different');
        }
        if (! $this->findCounted($table, $from)) {
            Errors::http(404, "from_id {$noun} not found");
        }
        if (! $this->findCounted($table, $to)) {
            Errors::http(404, "to_id {$noun} not found");
        }
        [$link, $fk] = $table === 'categories' ? ['recipes_to_categories', 'category_id'] : ['recipes_to_tags', 'tag_id'];

        Db::conn()->transaction(function () use ($link, $fk, $from, $to, $table) {
            Db::table($link)->where($fk, $from)
                ->whereNotIn('recipe_id', fn ($q) => $q->select('recipe_id')->from($link)->where($fk, $to))
                ->update([$fk => $to]);
            Db::table($link)->where($fk, $from)->delete();
            Db::table($table)->where('id', $from)->delete();
        });

        return $this->findCounted($table, $to);
    }

    public function categoriesMerge(Request $request)
    {
        return $this->json(Map::categoryOut($this->merge($request, 'categories', 'category')));
    }

    public function tagsMerge(Request $request)
    {
        return $this->json(Map::tagOut($this->merge($request, 'tags', 'tag')));
    }

    // ===================================================================== get one

    public function categoriesShow(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $row = $this->findCounted('categories', $id) ?? $this->notFound();

        return $this->json(['id' => Out::id($row->id), 'slug' => $row->slug, 'name' => $row->name]);
    }

    public function tagsShow(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $row = $this->findCounted('tags', $id) ?? $this->notFound();

        // TagOut validated into RecipeTagResponse: TagOut has no recipes, so the default [] is used
        return $this->json(Map::categoryBase($row) + ['recipes' => []]);
    }

    // ===================================================================== delete

    public function categoriesDestroy(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $this->canOrganize();
        if (! $this->findCounted('categories', $id)) {
            Errors::errorResponse(404, self::DEFAULT_MSG, self::NO_RESULT);
        }
        Db::conn()->transaction(function () use ($id) {
            Db::table('recipes_to_categories')->where('category_id', $id)->delete();
            Db::table('categories')->where('id', $id)->delete();
        });

        return response('null', 200, ['Content-Type' => 'application/json']);
    }

    public function tagsDestroy(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $this->canOrganize();
        if (! $this->findCounted('tags', $id)) {
            Errors::http(400, 'Bad Request');
        }
        Db::conn()->transaction(function () use ($id) {
            Db::table('recipes_to_tags')->where('tag_id', $id)->delete();
            Db::table('tags')->where('id', $id)->delete();
        });

        return response('null', 200, ['Content-Type' => 'application/json']);
    }

    // ===================================================================== by slug

    public function categoriesBySlug(string $category_slug)
    {
        $row = Db::table('categories')->where('group_id', $this->groupId())->where('slug', $category_slug)->first()
            ?? $this->notFound();

        // page_all(per_page=-1, query_filter='recipe_category.id IN [...]'), default order created_at desc
        $recipes = RecipeMap::query($this->groupId())
            ->whereExists(fn ($q) => $q->from('recipes_to_categories')
                ->whereColumn('recipes_to_categories.recipe_id', 'recipes.id')
                ->where('recipes_to_categories.category_id', $row->id))
            ->orderByDesc('recipes.created_at')->get();

        return $this->json([
            'name' => $row->name,
            'id' => Out::id($row->id),
            'groupId' => null,
            'slug' => $row->slug,
            'recipes' => RecipeMap::summaries($recipes),
        ]);
    }

    /** Tag.recipes / Tool.recipes relationship (all recipes linked, any household) */
    private function linkedRecipes(string $link, string $fk, string $id): array
    {
        $rows = RecipeMap::anyQuery(null)
            ->join($link, "{$link}.recipe_id", '=', 'recipes.id')
            ->where("{$link}.{$fk}", $id)
            ->orderBy("{$link}.rowid")->get();
        foreach ($rows as $r) {
            // RecipeSummary.household_id is a required UUID: a recipe without one fails validation (500)
            if ($r->r_household_id === null) {
                Db::serverError();
            }
        }

        return RecipeMap::summaries($rows);
    }

    public function tagsBySlug(string $tag_slug)
    {
        $row = Db::table('tags')->where('group_id', $this->groupId())->where('slug', $tag_slug)->first();
        if (! $row) {
            Db::serverError(); // None fails the RecipeTagResponse response model
        }

        $recipes = $this->linkedRecipes('recipes_to_tags', 'tag_id', $row->id);
        // the looked-up tag sits in the identity map with its recipe_count expression loaded,
        // so inside the nested recipes that one tag reports its real count
        $count = Db::table('recipes_to_tags')->where('tag_id', $row->id)->count();
        $tagId = Out::id($row->id);
        foreach ($recipes as &$recipe) {
            foreach ($recipe['tags'] as &$t) {
                if ($t['id'] === $tagId) {
                    $t['recipeCount'] = $count;
                }
            }
        }
        unset($recipe, $t);

        return $this->json(Map::categoryBase($row) + ['recipes' => $recipes]);
    }

    // ===================================================================== tools

    private function findTool(string $id): ?object
    {
        return Db::table('tools')->where('group_id', $this->groupId())->where('id', $id)->first();
    }

    private function toolOut(object $row): array
    {
        return Map::recipeTool($row, Map::toolHouseholds([$row->id]));
    }

    /** Tool.__init__ via auto_init: name, slug=slugify(name), households by slug within the group */
    private function saveTool(Request $request, ?string $id): object
    {
        $in = Input::fromRequest($request);
        $name = $in->str('name');
        $households = $in->strList('households_with_tool');
        $in->check();
        if ($id !== null && ! $this->findTool($id)) {
            $this->notFound();
        }

        return $this->write(function () use ($id, $name, $households) {
            $now = $this->now();
            if ($id === null) {
                $id = Guid::new();
                Db::table('tools')->insert([
                    'created_at' => $now, 'update_at' => $this->now(), 'id' => $id, 'group_id' => $this->groupId(),
                    'name' => $name, 'slug' => Text::slugify($name), 'on_hand' => 0,
                ]);
            } else {
                Db::table('tools')->where('id', $id)->update(['name' => $name, 'slug' => Text::slugify($name), 'update_at' => $now]);
                Db::table('households_to_tools')->where('tool_id', $id)->delete();
            }
            if ($households !== []) {
                $hids = Db::table('households')->where('group_id', $this->groupId())->whereIn('slug', $households)->orderBy('rowid')->pluck('id');
                foreach ($hids as $hid) {
                    Db::table('households_to_tools')->insert(['household_id' => $hid, 'tool_id' => $id]);
                }
            }

            return $this->findTool($id);
        }, self::DEFAULT_MSG);
    }

    public function toolsStore(Request $request)
    {
        return $this->json($this->toolOut($this->saveTool($request, null)), 201);
    }

    public function toolsShow(string $item_id)
    {
        $id = Input::pathUuid4($item_id);

        return $this->json($this->toolOut($this->findTool($id) ?? $this->notFound()));
    }

    public function toolsUpdate(Request $request, string $item_id)
    {
        $id = Input::pathUuid4($item_id);

        return $this->json($this->toolOut($this->saveTool($request, $id)));
    }

    public function toolsDestroy(string $item_id)
    {
        $id = Input::pathUuid4($item_id);
        $row = $this->findTool($id);
        if (! $row) {
            Errors::errorResponse(404, self::DEFAULT_MSG, self::NO_RESULT);
        }
        $out = $this->toolOut($row);
        Db::conn()->transaction(function () use ($id) {
            Db::table('recipes_to_tools')->where('tool_id', $id)->delete();
            Db::table('households_to_tools')->where('tool_id', $id)->delete();
            Db::table('tools')->where('id', $id)->delete();
        });

        return $this->json($out);
    }

    public function toolsBySlug(string $tool_slug)
    {
        $row = Db::table('tools')->where('group_id', $this->groupId())->where('slug', $tool_slug)->first();
        if (! $row) {
            Db::serverError();
        }
        $h = Map::toolHouseholds([$row->id]);

        return $this->json([
            'name' => $row->name,
            'householdsWithTool' => $h[$row->id] ?? [],
            'id' => Out::id($row->id),
            'groupId' => Out::id($row->group_id),
            'slug' => $row->slug,
            'recipes' => $this->linkedRecipes('recipes_to_tools', 'tool_id', $row->id),
        ]);
    }
}
