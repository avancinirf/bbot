<?php

namespace App\Services;

use Illuminate\Support\Facades\File;

class TradeLogService
{
    private string $basePath;

    public function __construct()
    {
        $this->basePath = storage_path('logs/trades');

        if (! File::isDirectory($this->basePath)) {
            File::makeDirectory($this->basePath, 0755, true);
        }
    }

    public function logResponse(int $botId, string $botNome, int $operacaoId, string $tipo, array $responseData): void
    {
        $this->write([
            'timestamp' => now()->toIso8601String(),
            'bot_id' => $botId,
            'bot_nome' => $botNome,
            'operacao_id' => $operacaoId,
            'tipo' => $tipo,
            'type' => 'response',
            'data' => $responseData,
        ]);
    }

    public function logError(int $botId, string $botNome, int $operacaoId, string $tipo, array $errorData): void
    {
        $this->write([
            'timestamp' => now()->toIso8601String(),
            'bot_id' => $botId,
            'bot_nome' => $botNome,
            'operacao_id' => $operacaoId,
            'tipo' => $tipo,
            'type' => 'error',
            'data' => $errorData,
        ]);
    }

    /**
     * Lista datas (YYYY-MM-DD) com ficheiros de log, mais recente primeiro.
     *
     * @return string[]
     */
    public function getAvailableDates(): array
    {
        if (! File::isDirectory($this->basePath)) {
            return [];
        }

        $files = File::files($this->basePath);

        return collect($files)
            ->map(fn ($f) => pathinfo($f->getFilename(), PATHINFO_FILENAME))
            ->filter(fn ($name) => preg_match('/^\d{4}-\d{2}-\d{2}$/', $name))
            ->sortDesc()
            ->values()
            ->all();
    }

    /**
     * Le todas as entradas de um dia, opcionalmente filtradas por type (request/response/error).
     *
     * @return array<int, array>
     */
    public function getLogsByDate(string $date, ?string $filter = null): array
    {
        $path = $this->basePath . '/' . $date . '.json';

        if (! File::exists($path)) {
            return [];
        }

        $lines = array_filter(explode("\n", File::get($path)));

        $entries = collect($lines)
            ->map(fn ($line) => json_decode($line, true))
            ->filter();

        if ($filter && in_array($filter, ['response', 'error'])) {
            $entries = $entries->filter(fn ($e) => ($e['type'] ?? '') === $filter);
        }

        return $entries->sortByDesc('timestamp')->values()->all();
    }

    private function write(array $entry): void
    {
        $date = now()->format('Y-m-d');
        $path = $this->basePath . '/' . $date . '.json';

        File::append($path, json_encode($entry, JSON_UNESCAPED_UNICODE) . "\n");
    }
}
