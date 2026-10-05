<?php

namespace App\Models\Mealie;

use App\Models\MealieModel;

class User extends MealieModel
{
    protected $table = 'users';

    protected $hidden = [
        'password',
        'cache_key',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'admin' => 'boolean',
            'advanced' => 'boolean',
            'can_manage' => 'boolean',
            'can_invite' => 'boolean',
            'can_organize' => 'boolean',
            'can_manage_household' => 'boolean',
            'show_announcements' => 'boolean',
            'created_at' => 'datetime',
            'update_at' => 'datetime',
            'locked_at' => 'datetime',
            'tokens_valid_after' => 'datetime',
        ];
    }
}
