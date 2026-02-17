<?php

namespace App\Http\Controllers;

use App\Services\BinanceService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;

class WalletController extends Controller
{
    /**
     * Retorna os saldos da carteira Binance em JSON.
     *
     * - ?refresh=1 forca busca na API e atualiza o cache.
     * - Sem refresh, retorna do cache se existir (TTL 10 minutos).
     */
    public function balances(Request $request, BinanceService $binanceService): JsonResponse
    {
        $forceRefresh = $request->boolean('refresh');

        if (! $forceRefresh) {
            $cached = Cache::get('wallet_data');
            $timestamp = Cache::get('wallet_ultima_atualizacao');

            if ($cached !== null) {
                return response()->json([
                    'balances' => $cached,
                    'timestamp' => $timestamp ? \Carbon\Carbon::parse($timestamp)->format('d/m/Y H:i:s') : null,
                ]);
            }
        }

        try {
            $balances = $binanceService->getAccountBalances();
        } catch (\Throwable $e) {
            return response()->json([
                'balances' => [],
                'timestamp' => null,
                'error' => 'Não foi possível obter os saldos: ' . $e->getMessage(),
            ], 500);
        }

        Cache::put('wallet_data', $balances, 600);
        Cache::put('wallet_ultima_atualizacao', now(), 600);

        return response()->json([
            'balances' => $balances,
            'timestamp' => now()->format('d/m/Y H:i:s'),
        ]);
    }
}
