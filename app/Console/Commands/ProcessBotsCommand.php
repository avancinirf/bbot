<?php

namespace App\Console\Commands;

use App\Services\BotProcessorService;
use Illuminate\Console\Command;

class ProcessBotsCommand extends Command
{
    protected $signature = 'bots:process';

    protected $description = 'Processa operacoes de todos os bots ativos';

    public function handle(BotProcessorService $service): int
    {
        $this->info('Iniciando processamento dos bots ativos...');

        $service->processar();

        $this->info('Processamento concluido.');

        return self::SUCCESS;
    }
}
