<?php

namespace App\Http\Controllers;

use App\Models\Bot;
use App\Models\Moeda;
use App\Services\BinanceService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class BotController extends Controller
{
    /**
     * Lista todos os bots (Dashboard).
     */
    public function index(): View
    {
        $bots = Bot::orderByDesc('created_at')->get();
        $moedas = Moeda::where('status', true)->orderBy('nome')->get();
        $ultimaAtualizacao = Cache::get('bots_ultima_atualizacao');

        return view('dashboard', compact('bots', 'moedas', 'ultimaAtualizacao'));
    }

    /**
     * Exibe o formulário de criação de um novo bot.
     */
    public function create(): View
    {
        $moedas = Moeda::where('status', true)->orderBy('nome')->get();

        return view('bots.create', compact('moedas'));
    }

    /**
     * Armazena um novo bot com suas operações no banco de dados.
     * Se status = ativo, busca o preco atual da moeda na Binance.
     */
    public function store(Request $request, BinanceService $binanceService): RedirectResponse
    {
        $validated = $request->validate([
            'nome' => 'required|string|max:255',
            'moeda_id' => 'required|exists:moedas,id',
            'status' => 'required|in:inativo,ativo',
            'operacoes' => 'required|array|min:1',
            'operacoes.*.tipo' => 'required|in:compra,venda',
            'operacoes.*.porcentagem' => 'required|numeric|min:0.1|max:100',
        ]);

        $ultimoValor = null;

        if ($validated['status'] === 'ativo') {
            $moeda = Moeda::find($validated['moeda_id']);
            $ultimoValor = $binanceService->getPrice($moeda->nome);
        }

        DB::transaction(function () use ($validated, $ultimoValor) {
            $bot = Bot::create([
                'nome' => $validated['nome'],
                'moeda_id' => $validated['moeda_id'],
                'status' => $validated['status'],
                'ultimo_valor' => $ultimoValor,
            ]);

            $bot->operacoes()->createMany($validated['operacoes']);
        });

        return redirect()->route('dashboard')->with('success', 'Bot criado com sucesso.');
    }

    /**
     * Exibe os detalhes de um bot específico.
     */
    public function show(Bot $bot): View
    {
        $bot->load('operacoes');

        return view('bots.show', compact('bot'));
    }

    /**
     * Exibe o formulário de edição de um bot.
     */
    public function edit(Bot $bot): View
    {
        return view('bots.edit', compact('bot'));
    }

    /**
     * Atualiza um bot no banco de dados.
     */
    public function update(Request $request, Bot $bot): RedirectResponse
    {
        $validated = $request->validate([
            'nome' => 'required|string|max:255',
            'moeda_id' => 'required|exists:moedas,id',
            'ultimo_valor' => 'nullable|numeric',
            'status' => 'required|in:inativo,ativo,desabilitado,concluido',
        ]);

        $bot->update($validated);

        return redirect()->route('dashboard')->with('success', 'Bot atualizado com sucesso.');
    }

    /**
     * Remove um bot do banco de dados.
     */
    public function destroy(Bot $bot): RedirectResponse
    {
        $bot->delete();

        return redirect()->route('dashboard')->with('success', 'Bot removido com sucesso.');
    }

    /**
     * Altera o status de um bot, respeitando as regras de transicao.
     *
     * Regras:
     *  - ativo    -> inativo | desabilitado
     *  - inativo  -> ativo   | desabilitado
     *  - desabilitado / concluido -> nao pode mudar manualmente
     *
     * Se o novo status for "ativo", busca o preco atual na Binance e atualiza ultimo_valor.
     */
    public function changeStatus(Request $request, Bot $bot, BinanceService $binanceService): RedirectResponse
    {
        $validated = $request->validate([
            'status' => 'required|in:ativo,inativo,desabilitado',
        ]);

        $novoStatus = $validated['status'];
        $statusAtual = $bot->status;

        $transicoesPermitidas = [
            'ativo' => ['inativo', 'desabilitado'],
            'inativo' => ['ativo', 'desabilitado'],
        ];

        $permitidas = $transicoesPermitidas[$statusAtual] ?? [];

        if (! in_array($novoStatus, $permitidas)) {
            return redirect()->route('dashboard')
                ->with('error', "Nao e possivel alterar o status de '{$statusAtual}' para '{$novoStatus}'.");
        }

        $dados = ['status' => $novoStatus];

        if ($novoStatus === 'ativo') {
            $preco = $binanceService->getPrice($bot->moeda->nome);
            if ($preco !== null) {
                $dados['ultimo_valor'] = $preco;
            }
        }

        $bot->update($dados);

        $label = ucfirst($novoStatus);

        return redirect()->route('dashboard')
            ->with('success', "Bot '{$bot->nome}' alterado para {$label}.");
    }

    /**
     * Retorna o timestamp da ultima atualizacao para polling AJAX.
     */
    public function ultimaAtualizacao(): \Illuminate\Http\JsonResponse
    {
        $timestamp = Cache::get('bots_ultima_atualizacao');

        return response()->json([
            'timestamp' => $timestamp ? \Carbon\Carbon::parse($timestamp)->format('d/m/Y H:i:s') : null,
        ]);
    }

    /**
     * Verifica se o scheduler (schedule:work) esta rodando.
     * Se estiver, informa o usuario via JSON. Se nao, inicia em background.
     * Usa bracket trick no pgrep para evitar falso positivo.
     */
    public function schedulerStatus(): \Illuminate\Http\JsonResponse
    {
        if (! function_exists('exec')) {
            Artisan::call('bots:process');

            return response()->json([
                'running' => false,
                'title' => 'Executado',
                'message' => 'exec() não disponível. Processamento executado manualmente.',
            ]);
        }

        $output = [];
        exec('pgrep -f "[s]chedule:work" 2>/dev/null', $output);
        $running = count($output) > 0;

        if ($running) {
            return response()->json([
                'running' => true,
                'title' => 'Cron Ativo',
                'message' => 'O cron já está em execução.',
            ]);
        }

        $basePath = base_path();
        exec("cd {$basePath} && nohup php artisan schedule:work > /dev/null 2>&1 &");

        return response()->json([
            'running' => false,
            'title' => 'Cron Iniciado',
            'message' => 'O cron não estava ativo e foi iniciado com sucesso.',
        ]);
    }

    /**
     * Atualiza o ultimo_valor do bot consultando o preco atual na Binance.
     */
    public function refreshPrice(Bot $bot, BinanceService $binanceService): RedirectResponse
    {
        $preco = $binanceService->getPrice($bot->moeda->nome);

        if ($preco === null) {
            return redirect()->route('dashboard')
                ->with('error', "Nao foi possivel obter o preco de {$bot->moeda->nome}/USDC.");
        }

        $bot->update(['ultimo_valor' => $preco]);

        return redirect()->route('dashboard')
            ->with('success', "Valor de referencia do bot '{$bot->nome}' atualizado para {$preco}.");
    }
}
