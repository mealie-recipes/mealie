<?php

namespace App\Services;

use App\Repositories\UserRepository;
use Throwable;

class HealthService
{
    public function __construct(private readonly UserRepository $users) {}

    /**
     * @return array{status: string, backend: string, database: string, users: int|null}
     */
    public function report(): array
    {
        $database = (string) config('database.connections.mealie.driver');

        try {
            $count = $this->users->count();
        } catch (Throwable) {
            return [
                'status' => 'error',
                'backend' => 'php',
                'database' => $database,
                'users' => null,
            ];
        }

        return [
            'status' => 'ok',
            'backend' => 'php',
            'database' => $database,
            'users' => $count,
        ];
    }
}
