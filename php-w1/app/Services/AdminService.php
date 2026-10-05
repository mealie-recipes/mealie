<?php

namespace App\Services;

use App\Support\Guid;
use App\Support\JsonShape;
use App\Support\MealieDb;
use App\Support\Pages;
use Illuminate\Http\Request;

final class AdminService
{
    public function __construct(private readonly AccountService $accounts) {}

    /**
     * @return array<string, mixed>
     */
    public function about(): array
    {
        $base = $this->accounts->about();

        return array_merge($base, [
            'versionLatest' => $base['version'],
            'apiPort' => 9001,
            'apiDocs' => false,
            'dbType' => (string) config('database.connections.mealie.driver'),
            'dbUrl' => null,
            'defaultGroup' => (string) config('mealie.default_group'),
            'defaultHousehold' => (string) config('mealie.default_household'),
            'buildId' => 'php',
            'recipeScraperVersion' => 'json-ld',
        ]);
    }

    /**
     * @return array<string, int>
     */
    public function statistics(): array
    {
        $recipes = MealieDb::table('recipes');

        return [
            'totalRecipes' => (clone $recipes)->count(),
            'totalUsers' => MealieDb::table('users')->count(),
            'totalHouseholds' => MealieDb::table('households')->count(),
            'totalGroups' => MealieDb::table('groups')->count(),
            'uncategorizedRecipes' => (clone $recipes)->whereNotIn('id', MealieDb::table('recipes_to_categories')->select('recipe_id'))->count(),
            'untaggedRecipes' => (clone $recipes)->whereNotIn('id', MealieDb::table('recipes_to_tags')->select('recipe_id'))->count(),
        ];
    }

    /**
     * @return array<string, bool>
     */
    public function check(): array
    {
        return [
            'emailReady' => false,
            'ldapReady' => false,
            'ldapDisabled' => true,
            'oidcReady' => false,
            'oidcDisabled' => true,
            'baseUrlSet' => true,
            'isUpToDate' => true,
        ];
    }

    /**
     * @return array<string, mixed>
     */
    public function users(Request $request): array
    {
        $query = Pages::query($request);
        $builder = MealieDb::table('users');
        $total = (clone $builder)->count();
        $rows = $builder->orderBy('username')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => $this->accounts->userOut($row))->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>
     */
    public function groups(Request $request): array
    {
        $query = Pages::query($request);
        $total = MealieDb::table('groups')->count();
        $rows = MealieDb::table('groups')->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'slug' => $row->slug,
        ])->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>
     */
    public function households(Request $request): array
    {
        $query = Pages::query($request);
        $total = MealieDb::table('households')->count();
        $rows = MealieDb::table('households')->orderBy('name')->forPage($query['page'], max($query['perPage'], 1))->get();

        return Pages::make($rows->map(fn ($row) => [
            'id' => Guid::dashed($row->id),
            'name' => $row->name,
            'slug' => $row->slug,
            'groupId' => Guid::dashed($row->group_id),
        ])->all(), $query['page'], $query['perPage'], $total);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function user(string $id): ?array
    {
        $row = $this->findUser($id);

        return $row === null ? null : $this->accounts->userOut($row);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    public function createUser(array $payload): array
    {
        $group = $this->resolveGroup((string) ($payload['group'] ?? ''));
        $household = $this->resolveHousehold($group, (string) ($payload['household'] ?? ''));
        $id = Guid::newHex();
        $now = MealieDb::now();
        MealieDb::table('users')->insert([
            'id' => $id,
            'username' => (string) $payload['username'],
            'full_name' => (string) ($payload['fullName'] ?? $payload['full_name'] ?? ''),
            'email' => (string) $payload['email'],
            'password' => password_hash(substr((string) $payload['password'], 0, 72), PASSWORD_BCRYPT),
            'admin' => JsonShape::bool($payload['admin'] ?? false) ? 1 : 0,
            'advanced' => JsonShape::bool($payload['advanced'] ?? false) ? 1 : 0,
            'group_id' => $group->id,
            'household_id' => $household?->id,
            'auth_method' => 'MEALIE',
            'can_invite' => JsonShape::bool($payload['canInvite'] ?? false) ? 1 : 0,
            'can_manage' => JsonShape::bool($payload['canManage'] ?? false) ? 1 : 0,
            'can_manage_household' => JsonShape::bool($payload['canManageHousehold'] ?? false) ? 1 : 0,
            'can_organize' => JsonShape::bool($payload['canOrganize'] ?? false) ? 1 : 0,
            'login_attemps' => 0,
            'created_at' => $now,
            'update_at' => $now,
        ]);

        return $this->accounts->userOut(MealieDb::table('users')->where('id', $id)->first());
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>|null
     */
    public function updateUser(string $id, array $payload): ?array
    {
        $row = $this->findUser($id);
        if ($row === null) {
            return null;
        }
        $fields = ['update_at' => MealieDb::now()];
        foreach ([
            'username' => 'username',
            'fullName' => 'full_name',
            'email' => 'email',
            'admin' => 'admin',
            'advanced' => 'advanced',
            'canInvite' => 'can_invite',
            'canManage' => 'can_manage',
            'canManageHousehold' => 'can_manage_household',
            'canOrganize' => 'can_organize',
        ] as $key => $column) {
            if (! array_key_exists($key, $payload)) {
                continue;
            }
            $fields[$column] = in_array($column, ['username', 'full_name', 'email'], true)
                ? (string) $payload[$key]
                : (JsonShape::bool($payload[$key]) ? 1 : 0);
        }
        if (isset($payload['password']) && is_string($payload['password']) && $payload['password'] !== '') {
            $fields['password'] = password_hash(substr($payload['password'], 0, 72), PASSWORD_BCRYPT);
            $fields['tokens_valid_after'] = MealieDb::now();
        }
        MealieDb::table('users')->where('id', $row->id)->update($fields);

        return $this->accounts->userOut(MealieDb::table('users')->where('id', $row->id)->first());
    }

    public function deleteUser(string $id, object $actor): bool
    {
        $row = $this->findUser($id);
        if ($row === null || $row->id === $actor->id) {
            return false;
        }

        return MealieDb::table('users')->where('id', $row->id)->delete() > 0;
    }

    /**
     * @return array<string, mixed>|null
     */
    public function passwordResetToken(string $email): ?array
    {
        $user = MealieDb::table('users')->whereRaw('lower(email) = ?', [strtolower($email)])->first();
        if ($user === null) {
            return null;
        }
        $token = bin2hex(random_bytes(16));
        MealieDb::table('password_reset_tokens')->insert([
            'user_id' => $user->id,
            'token' => $token,
            'created_at' => MealieDb::now(),
            'update_at' => MealieDb::now(),
        ]);

        return ['token' => $token];
    }

    public function unlock(): int
    {
        return MealieDb::table('users')->whereNotNull('locked_at')->update([
            'locked_at' => null,
            'login_attemps' => 0,
            'update_at' => MealieDb::now(),
        ]);
    }

    /**
     * @return array{imports: list<array<string, mixed>>, templates: list<string>}
     */
    public function backups(): array
    {
        $dir = rtrim((string) config('mealie.data_dir'), '/').'/backups';
        $imports = [];
        if (is_dir($dir)) {
            foreach (glob($dir.'/*.zip') ?: [] as $file) {
                $imports[] = [
                    'name' => basename($file),
                    'date' => date('c', (int) filemtime($file)),
                    'size' => $this->size((int) filesize($file)),
                ];
            }
        }
        usort($imports, fn ($a, $b) => strcmp($b['date'], $a['date']));

        return ['imports' => $imports, 'templates' => []];
    }

    private function findUser(string $id): ?object
    {
        $hex = Guid::hex($id);
        if ($hex !== null) {
            return MealieDb::table('users')->where('id', $hex)->first();
        }

        return MealieDb::table('users')->where(function ($query) use ($id) {
            $query->where('username', $id)->orWhere('email', $id);
        })->first();
    }

    private function resolveGroup(string $name): object
    {
        $hex = Guid::hex($name);
        $group = $hex !== null
            ? MealieDb::table('groups')->where('id', $hex)->first()
            : MealieDb::table('groups')->where(function ($query) use ($name) {
                $query->where('name', $name)->orWhere('slug', $name);
            })->first();
        if ($group === null) {
            $group = MealieDb::table('groups')->orderBy('name')->first();
        }

        return $group;
    }

    private function resolveHousehold(object $group, string $name): ?object
    {
        $query = MealieDb::table('households')->where('group_id', $group->id);
        $hex = Guid::hex($name);
        if ($hex !== null) {
            return (clone $query)->where('id', $hex)->first() ?? $query->orderBy('name')->first();
        }
        if ($name !== '') {
            $found = (clone $query)->where(function ($builder) use ($name) {
                $builder->where('name', $name)->orWhere('slug', $name);
            })->first();
            if ($found !== null) {
                return $found;
            }
        }

        return $query->orderBy('name')->first();
    }

    private function size(int $bytes): string
    {
        if ($bytes < 1024) {
            return $bytes.' B';
        }
        if ($bytes < 1048576) {
            return round($bytes / 1024, 1).' KB';
        }

        return round($bytes / 1048576, 1).' MB';
    }
}
