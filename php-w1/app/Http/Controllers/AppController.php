<?php

namespace App\Http\Controllers;

use App\Services\AccountService;
use Illuminate\Http\JsonResponse;

final class AppController extends Controller
{
    public function __construct(private readonly AccountService $accounts) {}

    public function about(): JsonResponse
    {
        return response()->json($this->accounts->about());
    }

    public function startup(): JsonResponse
    {
        return response()->json($this->accounts->startup());
    }

    public function theme(): JsonResponse
    {
        return response()->json($this->accounts->theme())->header('Cache-Control', 'public, max-age=604800');
    }
}
