<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;

final class ExploreService
{
    public function __construct(private readonly RecipeService $recipes) {}

    /**
     * @return array<string, mixed>|null
     */
    public function recipes(string $groupSlug, Request $request): ?array
    {
        $group = $this->publicGroup($groupSlug);
        if ($group === null) {
            return null;
        }

        $query = Pages::query($request);
        $builder = MealieDb::table('recipes')
            ->join('users', 'users.id', '=', 'recipes.user_id')
            ->join('household_preferences', 'household_preferences.household_id', '=', 'users.household_id')
            ->join('recipe_settings', 'recipe_settings.recipe_id', '=', 'recipes.id')
            ->where('recipes.group_id', $group->id)
            ->where('household_preferences.private_household', 0)
            ->where('recipe_settings.public', 1)
            ->select('recipes.*');
        if (is_string($query['search']) && $query['search'] !== '') {
            $builder->where('recipes.name', 'like', '%'.$query['search'].'%');
        }
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('recipes.created_at', 'desc')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->recipes->card($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function recipe(string $groupSlug, string $slug): ?array
    {
        $group = $this->publicGroup($groupSlug);
        if ($group === null) {
            return null;
        }
        $row = MealieDb::table('recipes')->where('group_id', $group->id)->where('slug', $slug)->first();
        if ($row === null || ! $this->recipeIsPublic($row)) {
            return null;
        }

        return $this->recipes->detailRow($row);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function organizers(string $groupSlug, string $table, Request $request): ?array
    {
        $group = $this->publicGroup($groupSlug);
        if ($group === null) {
            return null;
        }
        $query = Pages::query($request);
        $builder = MealieDb::table($table)->where('group_id', $group->id);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => [
            'id' => Guid::dashed($row->id),
            'groupId' => Guid::dashed($row->group_id),
            'name' => $row->name,
            'slug' => $row->slug,
        ])->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>|null
     */
    /**
     * @return array<string, mixed>|null
     */
    public function foods(string $groupSlug, Request $request): ?array
    {
        return $this->organizers($groupSlug, 'ingredient_foods', $request);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function cookbooks(string $groupSlug, string $householdSlug, Request $request): ?array
    {
        $group = $this->publicGroup($groupSlug);
        if ($group === null) {
            return null;
        }
        $household = MealieDb::table('households')->where('group_id', $group->id)->where('slug', $householdSlug)->first();
        if ($household === null) {
            return null;
        }
        $query = Pages::query($request);
        $builder = MealieDb::table('cookbooks')->where('household_id', $household->id)->where('public', 1);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('position')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'slug' => $row->slug,
            'description' => $row->description ?? '',
            'public' => true,
        ])->all(), $query['page'], $query['perPage'], $total);
    }

    public function households(string $groupSlug, Request $request): ?array
    {
        $group = $this->publicGroup($groupSlug);
        if ($group === null) {
            return null;
        }
        $query = Pages::query($request);
        $ids = MealieDb::table('household_preferences')->where('private_household', 0)->pluck('household_id');
        $builder = MealieDb::table('households')->where('group_id', $group->id)->whereIn('id', $ids);
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'slug' => $row->slug,
            'groupId' => Guid::dashed($row->group_id),
        ])->all(), $query['page'], $query['perPage'], $total);
    }

    private function publicGroup(string $slug): ?object
    {
        $group = MealieDb::table('groups')->where('slug', $slug)->first();
        $hex = Guid::hex($slug);
        if ($group === null && $hex !== null) {
            $group = MealieDb::table('groups')->where('id', $hex)->first();
        }
        if ($group === null) {
            return null;
        }
        $preferences = MealieDb::table('group_preferences')->where('group_id', $group->id)->first();
        if ($preferences && JsonShape::bool($preferences->private_group)) {
            return null;
        }

        return $group;
    }

    private function recipeIsPublic(object $recipe): bool
    {
        $settings = MealieDb::table('recipe_settings')->where('recipe_id', $recipe->id)->first();
        if ($settings === null || ! JsonShape::bool($settings->public)) {
            return false;
        }
        $owner = MealieDb::table('users')->where('id', $recipe->user_id)->first();
        if ($owner === null) {
            return false;
        }
        $preferences = MealieDb::table('household_preferences')->where('household_id', $owner->household_id)->first();

        return $preferences !== null && ! JsonShape::bool($preferences->private_household);
    }
}
