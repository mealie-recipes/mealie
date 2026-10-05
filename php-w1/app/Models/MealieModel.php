<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

/**
 * Base model for tables owned by the Python Mealie schema.
 *
 * Primary keys are UUID strings. The updated-at column is spelled update_at.
 */
abstract class MealieModel extends Model
{
    protected $connection = 'mealie';

    protected $keyType = 'string';

    public $incrementing = false;

    public const UPDATED_AT = 'update_at';

    protected $guarded = ['*'];
}
