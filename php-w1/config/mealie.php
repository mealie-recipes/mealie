<?php

$repoRoot = dirname(base_path());

return [
    'secret' => env('MEALIE_SECRET'),
    'secret_file' => env('MEALIE_SECRET_FILE', $repoRoot.'/dev/data/.secret'),
    'token_hours' => (int) env('TOKEN_TIME', 48),
    'max_login_attempts' => (int) env('SECURITY_MAX_LOGIN_ATTEMPTS', 5),
    'lockout_hours' => (int) env('SECURITY_USER_LOCKOUT_TIME', 24),
    'allow_signup' => filter_var(env('ALLOW_SIGNUP', false), FILTER_VALIDATE_BOOL),
    'allow_password_login' => filter_var(env('ALLOW_PASSWORD_LOGIN', true), FILTER_VALIDATE_BOOL),
    'default_group' => env('DEFAULT_GROUP', 'Home'),
    'default_household' => env('DEFAULT_HOUSEHOLD', 'Family'),
    'default_email' => 'changeme@example.com',
    'version' => env('MEALIE_VERSION', 'php'),
    'production' => filter_var(env('PRODUCTION', false), FILTER_VALIDATE_BOOL),
    'demo' => filter_var(env('IS_DEMO', false), FILTER_VALIDATE_BOOL),
    'data_dir' => env('MEALIE_DATA_DIR', $repoRoot.'/dev/data'),
    'base_url' => env('BASE_URL', 'http://127.0.0.1:3000'),
    'smtp_enabled' => filter_var(env('SMTP_ENABLE', false), FILTER_VALIDATE_BOOL),
];
