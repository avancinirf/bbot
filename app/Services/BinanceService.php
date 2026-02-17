<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\Client\PendingRequest;
use RuntimeException;

class BinanceService
{
    private string $apiKey;
    private string $apiSecret;
    private string $baseUrl;

    /**
     * Endpoints proibidos por seguranca (regra 020).
     * Qualquer chamada contendo estas palavras sera bloqueada.
     */
    private const BLOCKED_KEYWORDS = [
        'withdraw',
        'transfer',
        'capital',
    ];

    public function __construct()
    {
        $this->apiKey = config('services.binance.key');
        $this->apiSecret = config('services.binance.secret');
        $this->baseUrl = config('services.binance.base_url');
    }

    /**
     * Retorna lista de moedas base unicas (BTC, ETH, SOL, USDC...)
     * extraidas dos symbols com status TRADING no exchangeInfo.
     *
     * @return string[]
     */
    public function getBaseAssets(): array
    {
        $response = $this->publicRequest('GET', '/api/v3/exchangeInfo');

        $symbols = $response['symbols'] ?? [];

        $assets = collect($symbols)
            ->filter(fn (array $symbol) => ($symbol['status'] ?? '') === 'TRADING')
            ->flatMap(fn (array $symbol) => [
                $symbol['baseAsset'] ?? null,
                $symbol['quoteAsset'] ?? null,
            ])
            ->filter()
            ->unique()
            ->sort()
            ->values()
            ->all();

        return $assets;
    }

    /**
     * Retorna o preco atual de um ativo base em relacao a um ativo de cotacao.
     * Ex: getPrice('BTC', 'USDC') consulta o par BTCUSDC.
     *
     * @return float|null  Preco atual ou null se nao encontrado.
     */
    public function getPrice(string $baseAsset, string $quoteAsset = 'USDC'): ?float
    {
        $symbol = strtoupper($baseAsset . $quoteAsset);
        $response = $this->publicRequest('GET', '/api/v3/ticker/price', ['symbol' => $symbol]);

        return isset($response['price']) ? (float) $response['price'] : null;
    }

    /**
     * Retorna os saldos da conta com valores > 0.
     * Usa signedRequest no endpoint /api/v3/account.
     *
     * @return array<int, array{asset: string, free: float, locked: float}>
     */
    public function getAccountBalances(): array
    {
        $response = $this->signedRequest('GET', '/api/v3/account', [
            'omitZeroBalances' => 'true',
        ]);
        $balances = $response['balances'] ?? [];

        return collect($balances)
            ->filter(fn ($b) => (float) $b['free'] > 0 || (float) $b['locked'] > 0)
            ->map(fn ($b) => [
                'asset' => $b['asset'],
                'free' => (float) $b['free'],
                'locked' => (float) $b['locked'],
            ])
            ->sortBy('asset')
            ->values()
            ->all();
    }

    /**
     * Requisicao publica (sem assinatura HMAC).
     */
    public function publicRequest(string $method, string $endpoint, array $params = []): array
    {
        $this->guardEndpoint($endpoint);

        $response = $this->httpClient()
            ->send($method, $endpoint, [
                'query' => $params,
            ]);

        if ($response->failed()) {
            throw new RuntimeException(
                "Binance API error [{$response->status()}]: " . $response->body()
            );
        }

        return $response->json();
    }

    /**
     * Requisicao assinada com HMAC SHA256 (para endpoints SIGNED).
     * Preparado para uso futuro em trades.
     */
    public function signedRequest(string $method, string $endpoint, array $params = []): array
    {
        $this->guardEndpoint($endpoint);

        $params['timestamp'] = now()->getTimestampMs();
        $params['recvWindow'] = 5000;

        $queryString = http_build_query($params);
        $params['signature'] = hash_hmac('sha256', $queryString, $this->apiSecret);

        $response = $this->httpClient()
            ->send($method, $endpoint, [
                'query' => $params,
            ]);

        if ($response->failed()) {
            throw new RuntimeException(
                "Binance API error [{$response->status()}]: " . $response->body()
            );
        }

        return $response->json();
    }

    /**
     * Cria o HTTP client com base URL e header da API key.
     */
    private function httpClient(): PendingRequest
    {
        return Http::baseUrl($this->baseUrl)
            ->withHeaders([
                'X-MBX-APIKEY' => $this->apiKey,
            ])
            ->timeout(30);
    }

    /**
     * Bloqueia chamadas a endpoints proibidos (withdraw, transfer, capital).
     * Fail-fast de seguranca conforme regra 020-binance-safety.
     */
    private function guardEndpoint(string $endpoint): void
    {
        $lower = strtolower($endpoint);

        foreach (self::BLOCKED_KEYWORDS as $keyword) {
            if (str_contains($lower, $keyword)) {
                throw new RuntimeException(
                    "Endpoint bloqueado por seguranca: '{$endpoint}' contem '{$keyword}'. "
                    . 'Apenas endpoints de consulta e trade sao permitidos.'
                );
            }
        }
    }
}
