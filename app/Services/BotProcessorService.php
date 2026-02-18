<?php

namespace App\Services;

use App\Models\Bot;
use App\Models\Operacao;
use App\Models\User;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;

class BotProcessorService
{
    public function __construct(
        private BinanceService $binanceService,
        private TradeLogService $tradeLogService,
        private NotificationService $notificationService,
    ) {}

    /**
     * Processa todos os bots ativos, iterando por operacoes pendentes.
     * Atualiza o timestamp de ultima atualizacao no cache ao final.
     */
    public function processar(): void
    {
        $bots = Bot::where('status', 'ativo')
            ->with(['operacoes', 'moeda'])
            ->get();

        Log::info("BotProcessor: iniciando processamento de {$bots->count()} bot(s) ativo(s).");

        foreach ($bots as $bot) {
            $pendentes = $bot->operacoes
                ->whereNull('data_trade')
                ->sortBy('id');

            if ($pendentes->isEmpty()) {
                continue;
            }

            $operacao = $pendentes->first();
            Log::info("BotProcessor: processando bot #{$bot->id} ({$bot->nome}) - operacao #{$operacao->id} ({$pendentes->count()} pendente(s))");

            try {
                if (!$this->validarTrade($operacao)) {
                    Log::info("BotProcessor: operacao #{$operacao->id} do bot #{$bot->id} nao satisfaz condicoes, saltando bot.");
                    continue;
                }

                $this->executarTrade($operacao);

                $bot->refresh();
                $todasConcluidas = $bot->operacoes->every(fn ($op) => $op->data_trade !== null);
                if ($todasConcluidas) {
                    $bot->update(['status' => 'concluido']);
                    Log::info("BotProcessor: bot #{$bot->id} concluido - todas as operacoes executadas.");
                }
            } catch (\Throwable $e) {
                Log::error("BotProcessor: erro na operacao #{$operacao->id} do bot #{$bot->id}: {$e->getMessage()}");
            }
        }

        Cache::put('bots_ultima_atualizacao', now());

        Log::info('BotProcessor: processamento concluido.');
    }

    /**
     * Valida se a operacao pode ser executada com base nas regras de porcentagem.
     *
     * Regras:
     *  1. Se ja tem data_trade, retorna false (ja executada)
     *  2. Compra com porcentagem = 0: retorna true
     *  3. Compra com porcentagem > 0: preco_atual <= ultimo_valor * (1 - porcentagem/100)
     *  4. Venda: preco_atual >= ultimo_valor * (1 + porcentagem/100)
     */
    public function validarTrade(Operacao $operacao): bool
    {
        if ($operacao->data_trade !== null) {
            return false;
        }

        $bot = $operacao->bot;
        $moedaNome = $bot->moeda->nome;
        $ultimoValor = (float) $bot->ultimo_valor;

        $precoAtual = $this->binanceService->getPrice($moedaNome, 'USDC');

        if ($precoAtual === null) {
            Log::warning("BotProcessor: nao foi possivel obter preco de {$moedaNome}/USDC para operacao #{$operacao->id}");
            return false;
        }

        $porcentagem = (float) $operacao->porcentagem;

        if ($operacao->tipo === 'compra') {
            if ($porcentagem == 0) {
                return true;
            }

            $limiar = $ultimoValor * (1 - $porcentagem / 100);
            return $precoAtual <= $limiar;
        }

        if ($operacao->tipo === 'venda') {
            $limiar = $ultimoValor * (1 + $porcentagem / 100);
            return $precoAtual >= $limiar;
        }

        return false;
    }

    /**
     * Executa o trade na Binance e grava os dados na operacao.
     * Atualiza o ultimo_valor do bot com o preco medio executado.
     */
    public function executarTrade(Operacao $operacao): void
    {
        $bot = $operacao->bot;
        $moedaNome = $bot->moeda->nome;
        $symbol = strtoupper($moedaNome . 'USDC');
        $side = $operacao->tipo === 'compra' ? 'BUY' : 'SELL';
        $valorNegociado = (float) $operacao->valor_negociado;

        $requestData = [
            'symbol' => $symbol,
            'side' => $side,
            'type' => 'MARKET',
            'quoteOrderQty' => $valorNegociado,
        ];

        try {
            $response = $this->binanceService->placeOrder($symbol, $side, $valorNegociado);

            $this->tradeLogService->logResponse(
                $bot->id, $bot->nome, $operacao->id, $operacao->tipo, $response
            );

            if (($response['status'] ?? '') !== 'FILLED') {
                Log::warning("BotProcessor: ordem #{$response['orderId']} nao foi FILLED, status: {$response['status']}");
                return;
            }

            $executedQty = (float) ($response['executedQty'] ?? 0);
            $cummulativeQuoteQty = (float) ($response['cummulativeQuoteQty'] ?? 0);
            $precoMedio = $executedQty > 0 ? $cummulativeQuoteQty / $executedQty : 0;

            $comissaoTotal = collect($response['fills'] ?? [])
                ->sum(fn ($fill) => (float) ($fill['commission'] ?? 0));

            $operacao->update([
                'valor_anterior' => $bot->ultimo_valor,
                'valor_trade' => $precoMedio,
                'data_trade' => now(),
                'binance_order_id' => (string) ($response['orderId'] ?? ''),
                'quantidade_executada' => $executedQty,
                'comissao_total' => $comissaoTotal,
            ]);

            $bot->update(['ultimo_valor' => $precoMedio]);

            Log::info("BotProcessor: trade executado - bot #{$bot->id}, operacao #{$operacao->id}, preco medio: {$precoMedio}");

        } catch (\Throwable $e) {
            $this->tradeLogService->logError(
                $bot->id, $bot->nome, $operacao->id, $operacao->tipo,
                ['message' => $e->getMessage(), 'request' => $requestData]
            );

            $user = User::first();
            if ($user) {
                $this->notificationService->sendNotification(
                    $user,
                    'Erro no Trade',
                    "Erro ao executar {$operacao->tipo} no bot '{$bot->nome}' (operacao #{$operacao->id}): {$e->getMessage()}"
                );
            }

            throw $e;
        }
    }
}
