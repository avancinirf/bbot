<?php

namespace App\Http\Controllers;

use App\Models\Moeda;
use App\Services\BinanceService;
use Illuminate\Http\RedirectResponse;

class MoedaController extends Controller
{
    /**
     * Sincroniza moedas base da Binance com a BD.
     *
     * - Novas moedas: inseridas com status = true
     * - Moedas que nao existem mais na API: status = false
     * - Moedas que voltaram a existir na API: status = true
     * - Moedas ja existentes com status true: ignoradas
     */
    public function sync(BinanceService $service): RedirectResponse
    {
        try {
            $apiAssets = $service->getBaseAssets();
        } catch (\Throwable $e) {
            return redirect()->route('dashboard')
                ->with('error', 'Erro ao conectar com a Binance: ' . $e->getMessage());
        }

        $existingMoedas = Moeda::all()->keyBy('nome');

        $added = 0;
        $reactivated = 0;

        foreach ($apiAssets as $asset) {
            $moeda = $existingMoedas->get($asset);

            if ($moeda === null) {
                Moeda::create(['nome' => $asset, 'status' => true]);
                $added++;
            } elseif (!$moeda->status) {
                $moeda->update(['status' => true]);
                $reactivated++;
            }
        }

        $deactivated = Moeda::whereNotIn('nome', $apiAssets)
            ->where('status', true)
            ->update(['status' => false]);

        $message = "{$added} moedas adicionadas, {$deactivated} desativadas, {$reactivated} reativadas.";

        return redirect()->route('dashboard')
            ->with('success', $message);
    }
}
