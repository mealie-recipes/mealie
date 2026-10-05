<?php

namespace Tests\Feature;

use Tests\TestCase;

class HealthTest extends TestCase
{
    public function test_health_reads_the_mealie_database(): void
    {
        $response = $this->getJson('/api/health');

        $response->assertOk()
            ->assertJsonPath('status', 'ok')
            ->assertJsonPath('backend', 'php')
            ->assertJsonPath('database', 'sqlite')
            ->assertJsonStructure(['status', 'backend', 'database', 'users']);

        $this->assertIsInt($response->json('users'));
    }
}
