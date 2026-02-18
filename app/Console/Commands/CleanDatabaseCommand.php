<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

class CleanDatabaseCommand extends Command
{
    protected $signature = 'db:clean
                            {--force : Executar sem pedir confirmacao}';

    protected $description = 'Remove todos os dados de moedas, bots e operacoes e limpa o cache da aplicacao';

    public function handle(): int
    {
        if (! $this->option('force') && ! $this->confirm('Confirma a remocao de todos os dados (moedas, bots, operacoes) e limpeza do cache?')) {
            $this->warn('Operacao cancelada.');
            return self::FAILURE;
        }

        $this->info('Limpando dados...');

        DB::transaction(function () {
            DB::table('operacoes')->delete();
            DB::table('bots')->delete();
            DB::table('moedas')->delete();
        });

        Cache::forget('bots_ultima_atualizacao');
        Cache::forget('wallet_data');
        Cache::forget('wallet_ultima_atualizacao');

        $this->info('Dados removidos e cache limpo.');

        return self::SUCCESS;
    }
}
