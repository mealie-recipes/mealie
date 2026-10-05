<?php

namespace Tests\Feature;

use App\Auth\Jwt;
use App\Services\OpsService;
use App\Support\Guid;
use App\Support\Images;
use App\Support\MealieDb;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

class ApiTest extends TestCase
{
    public function test_microdata_import_and_archive_migration_roll_back(): void
    {
        $connection = DB::connection('mealie');
        $connection->beginTransaction();
        $zipPath = tempnam(sys_get_temp_dir(), 'mealie-mig');

        try {
            $user = MealieDb::table('users')->first();
            $token = Jwt::encode([
                'sub' => Guid::dashed($user->id),
                'rme' => false,
                'iss' => 'mealie',
                'iat' => time(),
                'exp' => time() + 3600,
            ], 'test-secret');
            $html = '<div itemscope itemtype="https://schema.org/Recipe"><span itemprop="name">Micro Soup</span><span itemprop="recipeIngredient">water</span><span itemprop="recipeInstructions">boil</span></div>';
            $this->withToken($token)->post('/api/recipes/create/html-or-json/stream', ['data' => $html])
                ->assertOk()
                ->assertSee('event: done');

            $zip = new \ZipArchive;
            $zip->open($zipPath, \ZipArchive::OVERWRITE);
            $zip->addFromString('soup/recipe.json', json_encode([
                'name' => 'PHP Soup',
                'recipeIngredient' => ['water'],
            ], JSON_THROW_ON_ERROR));
            $zip->close();
            $upload = new UploadedFile($zipPath, 'nextcloud.zip', 'application/zip', null, true);
            $this->withToken($token)->post('/api/groups/migrations', [
                'migration_type' => 'nextcloud',
                'archive' => $upload,
            ])->assertOk()->assertJsonPath('status', 'success');

            $this->assertArrayHasKey('users', app(OpsService::class)->databaseDump());
            $this->withToken($token)->postJson('/api/admin/email', ['email' => 'person@example.com'])
                ->assertStatus(400)
                ->assertJsonPath('success', false);
        } finally {
            $connection->rollBack();
            @unlink($zipPath);
        }
    }

    public function test_validators_and_oidc_status(): void
    {
        $user = MealieDb::table('users')->first();
        $this->getJson('/api/validators/user/name?name='.$user->username)->assertOk()->assertJsonPath('valid', false);
        $this->getJson('/api/validators/user/name?name=not-a-real-mealie-user')->assertOk()->assertJsonPath('valid', true);
        $this->getJson('/api/auth/oauth')->assertNotFound();
    }

    public function test_seed_and_notifier_roll_back(): void
    {
        $connection = DB::connection('mealie');
        $connection->beginTransaction();

        try {
            $user = MealieDb::table('users')->first();
            $token = Jwt::encode([
                'sub' => Guid::dashed($user->id),
                'rme' => false,
                'iss' => 'mealie',
                'iat' => time(),
                'exp' => time() + 3600,
            ], 'test-secret');

            $this->withToken($token)->postJson('/api/groups/seeders/foods', ['locale' => 'en-US'])->assertOk();
            $this->withToken($token)->postJson('/api/households/events/notifications', [
                'name' => 'PHP notifier',
                'appriseUrl' => 'json://localhost',
            ])->assertCreated()->assertJsonPath('name', 'PHP notifier');
            $this->withToken($token)->getJson('/api/groups/reports')->assertOk();
            $this->withToken($token)->getJson('/api/groups/households')->assertOk();
            $this->withToken($token)->postJson('/api/recipes/test-scrape-url', ['url' => 'https://example.com'])->assertOk();
            $this->withToken($token)->post('/api/recipes/create/ai/stream', [])
                ->assertOk()
                ->assertSee('event: error');
        } finally {
            $connection->rollBack();
        }
    }

    public function test_about_is_public_and_camel_cased(): void
    {
        $this->getJson('/api/app/about')
            ->assertOk()
            ->assertJsonStructure(['version', 'allowSignup', 'allowPasswordLogin', 'tokenTime']);
    }

    public function test_self_requires_a_token(): void
    {
        $this->getJson('/api/users/self')->assertUnauthorized();
    }

    public function test_signed_token_returns_the_user_and_recipes(): void
    {
        $user = MealieDb::table('users')->first();
        $this->assertNotNull($user);

        $now = time();
        $token = Jwt::encode([
            'sub' => Guid::dashed($user->id),
            'rme' => false,
            'iss' => 'mealie',
            'iat' => $now,
            'exp' => $now + 3600,
        ], 'test-secret');

        $this->withToken($token)->getJson('/api/users/self')
            ->assertOk()
            ->assertJsonPath('id', Guid::dashed($user->id))
            ->assertJsonPath('groupId', Guid::dashed($user->group_id));

        $this->withToken($token)->getJson('/api/recipes')
            ->assertOk()
            ->assertJsonStructure(['page', 'perPage', 'items', 'total']);

        $this->withToken($token)->getJson('/api/households/self')->assertOk();
        $this->withToken($token)->getJson('/api/groups/self')->assertOk();
        $this->withToken($token)->getJson('/api/categories')->assertOk();
        $this->withToken($token)->getJson('/api/households/shopping/lists')->assertOk();
    }

    public function test_missing_recipe_image_is_not_found(): void
    {
        $this->get('/api/media/recipes/00000000-0000-4000-8000-000000000000/images/original.webp')
            ->assertNotFound();
    }

    public function test_shopping_item_can_be_checked_and_removed(): void
    {
        $connection = DB::connection('mealie');
        $connection->beginTransaction();

        try {
            $user = MealieDb::table('users')->first();
            $list = MealieDb::table('shopping_lists')->where('group_id', $user->group_id)->first();
            $this->assertNotNull($list);

            $token = Jwt::encode([
                'sub' => Guid::dashed($user->id),
                'rme' => false,
                'iss' => 'mealie',
                'iat' => time(),
                'exp' => time() + 3600,
            ], 'test-secret');

            $created = $this->withToken($token)->postJson('/api/households/shopping/items', [
                'shoppingListId' => Guid::dashed($list->id),
                'note' => 'php skeleton item',
                'quantity' => 2,
            ])->assertCreated();

            $id = $created->json('createdItems.0.id');
            $this->assertNotEmpty($id);

            $this->withToken($token)->putJson('/api/households/shopping/items/'.$id, [
                'checked' => true,
            ])->assertOk()->assertJsonPath('updatedItems.0.checked', true);

            $this->withToken($token)->delete('/api/households/shopping/items/'.$id)->assertOk();
        } finally {
            $connection->rollBack();
        }
    }

    public function test_rules_cookbooks_and_shares_roll_back(): void
    {
        $connection = DB::connection('mealie');
        $connection->beginTransaction();

        try {
            $user = MealieDb::table('users')->first();
            $recipe = MealieDb::table('recipes')->where('group_id', $user->group_id)->first();
            $token = Jwt::encode([
                'sub' => Guid::dashed($user->id),
                'rme' => false,
                'iss' => 'mealie',
                'iat' => time(),
                'exp' => time() + 3600,
            ], 'test-secret');

            $this->withToken($token)->postJson('/api/households/mealplans/rules', [
                'day' => 'monday',
                'entryType' => 'dinner',
                'queryFilterString' => '',
            ])->assertCreated()->assertJsonPath('day', 'monday');

            $this->withToken($token)->postJson('/api/households/cookbooks', [
                'name' => 'PHP Cookbook',
            ])->assertCreated()->assertJsonPath('name', 'PHP Cookbook');

            $share = $this->withToken($token)->postJson('/api/shared/recipes', [
                'recipeId' => Guid::dashed($recipe->id),
            ])->assertCreated();
            $this->getJson('/api/recipes/shared/'.$share->json('id'))->assertOk()->assertJsonPath('slug', $recipe->slug);
        } finally {
            $connection->rollBack();
        }
    }

    public function test_recipe_image_upload_writes_webp_and_rolls_back(): void
    {
        $connection = DB::connection('mealie');
        $connection->beginTransaction();
        $directory = null;

        try {
            $user = MealieDb::table('users')->first();
            $token = Jwt::encode([
                'sub' => Guid::dashed($user->id),
                'rme' => false,
                'iss' => 'mealie',
                'iat' => time(),
                'exp' => time() + 3600,
            ], 'test-secret');

            $created = $this->withToken($token)->postJson('/api/recipes/create', [
                'name' => 'PHP Image Recipe',
            ])->assertCreated();
            $id = $created->json('id');
            $slug = $created->json('slug');
            $directory = dirname(base_path()).'/dev/data/recipes/'.$id.'/images';
            $png = base64_decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
            $path = tempnam(sys_get_temp_dir(), 'mealie');
            file_put_contents($path, $png);
            $file = new UploadedFile($path, 'dot.png', 'image/png', null, true);

            $this->withToken($token)->put('/api/recipes/'.$slug.'/image', [
                'extension' => 'png',
                'image' => $file,
            ])->assertOk()->assertJsonStructure(['image']);

            $this->assertFileExists($directory.'/original.webp');
        } finally {
            $connection->rollBack();
            if (is_string($directory)) {
                Images::removeSet($directory);
                @rmdir($directory);
                @rmdir(dirname($directory));
            }
        }
    }

    public function test_ai_settings_are_returned(): void
    {
        $connection = DB::connection('mealie');
        $connection->beginTransaction();

        try {
            $user = MealieDb::table('users')->first();
            $token = Jwt::encode([
                'sub' => Guid::dashed($user->id),
                'rme' => false,
                'iss' => 'mealie',
                'iat' => time(),
                'exp' => time() + 3600,
            ], 'test-secret');

            $this->withToken($token)->getJson('/api/groups/ai-providers/settings')
                ->assertOk()
                ->assertJsonStructure(['providers', 'aiEnabled']);
        } finally {
            $connection->rollBack();
        }
    }

    public function test_today_and_suggestions_are_available(): void
    {
        $user = MealieDb::table('users')->first();
        $token = Jwt::encode([
            'sub' => Guid::dashed($user->id),
            'rme' => false,
            'iss' => 'mealie',
            'iat' => time(),
            'exp' => time() + 3600,
        ], 'test-secret');

        $this->withToken($token)->getJson('/api/households/mealplans/today')->assertOk();
        $this->withToken($token)->getJson('/api/recipes/suggestions')->assertOk()->assertJsonStructure(['items']);
        $this->withToken($token)->getJson('/api/admin/about')->assertStatus(
            filter_var($user->admin, FILTER_VALIDATE_BOOL) ? 200 : 403
        );
    }

    public function test_explore_unknown_group_is_not_found(): void
    {
        $this->getJson('/api/explore/groups/does-not-exist/recipes')->assertNotFound();
    }

    public function test_bad_password_is_rejected(): void
    {
        $this->post('/api/auth/token', [
            'username' => 'nobody-'.uniqid(),
            'password' => 'not-a-real-password',
        ])->assertUnauthorized();
    }
}
