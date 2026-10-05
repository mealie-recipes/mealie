<?php

namespace App\Repositories;

use App\Models\Mealie\User;

class UserRepository extends Repository
{
    protected function model(): string
    {
        return User::class;
    }

    public function count(): int
    {
        return $this->query()->count();
    }
}
