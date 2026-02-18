<?php

namespace App\Services;

use App\Models\User;
use Illuminate\Support\Facades\Log;

class NotificationService
{
    /**
     * Envia uma notificacao ao utilizador.
     * Placeholder -- sera implementado futuramente com push notification.
     * Campos disponiveis: $user->telefone, $user->email
     */
    public function sendNotification(User $user, string $title, string $message): void
    {
        Log::warning("NotificationService: [{$title}] {$message} -> {$user->email}");
    }
}
