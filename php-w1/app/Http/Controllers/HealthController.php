<?php

namespace App\Http\Controllers;

use App\Services\HealthService;
use Illuminate\Http\JsonResponse;

class HealthController extends Controller
{
    public function __invoke(HealthService $health): JsonResponse
    {
        $report = $health->report();

        return response()->json($report, $report['status'] === 'ok' ? 200 : 503);
    }
}
