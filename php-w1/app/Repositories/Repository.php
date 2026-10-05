<?php

namespace App\Repositories;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

abstract class Repository
{
    /**
     * @return class-string<Model>
     */
    abstract protected function model(): string;

    protected function query(): Builder
    {
        $model = $this->model();

        return $model::query();
    }
}
