<?php

namespace App\Services;

use Illuminate\Support\Facades\Mail;

final class MailService
{
    public function enabled(): bool
    {
        return (bool) config('mealie.smtp_enabled');
    }

    /**
     * @return array{success: bool, error: string|null}
     */
    public function send(string $to, string $subject, string $body): array
    {
        if (! $this->enabled()) {
            return ['success' => false, 'error' => 'SMTP is not enabled'];
        }
        if (! filter_var($to, FILTER_VALIDATE_EMAIL)) {
            return ['success' => false, 'error' => 'Email address is not valid'];
        }
        try {
            Mail::html('<p>'.e($body).'</p>', function ($message) use ($to, $subject) {
                $message->to($to)->subject($subject);
            });
        } catch (\Throwable $e) {
            return ['success' => false, 'error' => $e->getMessage()];
        }

        return ['success' => true, 'error' => null];
    }
}
