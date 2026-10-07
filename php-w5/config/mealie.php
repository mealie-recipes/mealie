<?php

// Shared Mealie settings. Phase 0 (orchestrator) owns this file.
return [
    // Mirrors mealie/core/config.py PRODUCTION. The oracle runs with PRODUCTION=False.
    'production' => filter_var(env('MEALIE_PRODUCTION', false), FILTER_VALIDATE_BOOLEAN),
    'data_dir' => env('MEALIE_DATA_DIR', dirname(base_path()).'/dev/data'),
    // Explicit secret override; otherwise see App\Auth\Jwt::secret().
    'secret' => env('MEALIE_SECRET'),
];
