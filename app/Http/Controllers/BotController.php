<?php

namespace App\Http\Controllers;

use App\Models\Bot;
use App\Models\Moeda;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
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

        return view('dashboard', compact('bots', 'moedas'));
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
     */
    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'nome' => 'required|string|max:255',
            'moeda_id' => 'required|exists:moedas,id',
            'status' => 'required|in:inativo,ativo',
            'operacoes' => 'required|array|min:1',
            'operacoes.*.tipo' => 'required|in:compra,venda',
            'operacoes.*.porcentagem' => 'required|numeric|min:0.1|max:100',
        ]);

        DB::transaction(function () use ($validated) {
            $bot = Bot::create([
                'nome' => $validated['nome'],
                'moeda_id' => $validated['moeda_id'],
                'status' => $validated['status'],
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
}
