<?php

/*
 * Phase 0 (orchestrator) owns this file. Each area registers its routes only in its own file.
 * Paths inside area files are written without the /api prefix, which bootstrap/app.php adds.
 */
foreach (['auth-users', 'recipes', 'households', 'groups-admin'] as $area) {
    $file = __DIR__."/{$area}.php";
    if (is_file($file)) {
        require $file;
    }
}
