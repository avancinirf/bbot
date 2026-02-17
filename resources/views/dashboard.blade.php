<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            {{ __('Dashboard') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900">

                    @if (session('success'))
                        <div class="mb-4 p-4 rounded-md bg-green-50 border border-green-200">
                            <p class="text-sm text-green-800">{{ session('success') }}</p>
                        </div>
                    @endif

                    @if (session('error'))
                        <div class="mb-4 p-4 rounded-md bg-red-50 border border-red-200">
                            <p class="text-sm text-red-800">{{ session('error') }}</p>
                        </div>
                    @endif

                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold">Lista de Bots</h3>

                        <div class="flex items-center gap-2">
                            <form action="{{ route('moedas.sync') }}" method="POST">
                                @csrf
                                <button type="submit"
                                    class="inline-flex items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-500 active:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition ease-in-out duration-150">
                                    Sincronizar Moedas
                                </button>
                            </form>

                            <button
                                x-data=""
                                x-on:click="$dispatch('open-modal', 'criar-bot')"
                                type="button"
                                class="inline-flex items-center justify-center w-9 h-9 bg-green-600 border border-transparent rounded-md font-semibold text-white hover:bg-green-500 active:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition ease-in-out duration-150"
                                title="Adicionar Bot">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    @if ($errors->any())
                        <div class="mb-4 p-4 rounded-md bg-red-50 border border-red-200">
                            <ul class="list-disc list-inside text-sm text-red-800">
                                @foreach ($errors->all() as $error)
                                    <li>{{ $error }}</li>
                                @endforeach
                            </ul>
                        </div>
                    @endif

                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Moeda</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Último Valor</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Criado em</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Atualizado em</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                @forelse ($bots as $bot)
                                    <tr>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->id }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->nome }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->moeda->nome }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->ultimo_valor ?? '—' }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm">
                                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                                @if($bot->status === 'ativo') bg-green-100 text-green-800
                                                @elseif($bot->status === 'inativo') bg-gray-100 text-gray-800
                                                @elseif($bot->status === 'desabilitado') bg-red-100 text-red-800
                                                @elseif($bot->status === 'concluido') bg-blue-100 text-blue-800
                                                @endif">
                                                {{ ucfirst($bot->status) }}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ $bot->created_at->format('d/m/Y H:i') }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ $bot->updated_at->format('d/m/Y H:i') }}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm">
                                            <a href="{{ route('bots.show', $bot) }}"
                                                class="text-blue-600 hover:text-blue-800 font-medium">
                                                Ver
                                            </a>
                                        </td>
                                    </tr>
                                @empty
                                    <tr>
                                        <td colspan="8" class="px-6 py-4 text-center text-sm text-gray-500">
                                            Nenhum bot encontrado.
                                        </td>
                                    </tr>
                                @endforelse
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {{-- Modal: Criar Bot --}}
    <x-modal name="criar-bot" maxWidth="2xl" focusable>
        <div class="p-6" x-data="{
            statusAtivo: {{ old('status', 'inativo') === 'ativo' ? 'true' : 'false' }},
            operacoes: [{ tipo: 'compra', porcentagem: '' }],
            addOperacao() {
                this.operacoes.push({ tipo: 'compra', porcentagem: '' });
            },
            removeOperacao(index) {
                if (this.operacoes.length > 1) {
                    this.operacoes.splice(index, 1);
                }
            }
        }">
            <form method="POST" action="{{ route('bots.store') }}">
                @csrf

                <h2 class="text-lg font-semibold text-gray-900 mb-4">Criar Novo Bot</h2>

                {{-- Campos do Bot --}}
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                    <div>
                        <x-input-label for="nome" value="Nome" />
                        <x-text-input id="nome" name="nome" type="text" class="mt-1 block w-full" required :value="old('nome')" />
                        <x-input-error :messages="$errors->get('nome')" class="mt-2" />
                    </div>

                    <div>
                        <x-input-label for="moeda_id" value="Moeda" />
                        <select id="moeda_id" name="moeda_id" class="mt-1 block w-full border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm" required>
                            <option value="">Selecione uma moeda</option>
                            @foreach ($moedas as $moeda)
                                <option value="{{ $moeda->id }}" @selected(old('moeda_id') == $moeda->id)>{{ $moeda->nome }}</option>
                            @endforeach
                        </select>
                        <x-input-error :messages="$errors->get('moeda_id')" class="mt-2" />
                    </div>

                    <div class="sm:col-span-2">
                        <div class="flex items-center gap-3">
                            <x-input-label for="status_toggle" value="Status" />
                            <input type="hidden" name="status" :value="statusAtivo ? 'ativo' : 'inativo'">
                            <button
                                type="button"
                                x-on:click="statusAtivo = !statusAtivo"
                                :class="statusAtivo ? 'bg-green-600' : 'bg-gray-300'"
                                class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                                role="switch"
                                :aria-checked="statusAtivo"
                                id="status_toggle">
                                <span
                                    :class="statusAtivo ? 'translate-x-5' : 'translate-x-0'"
                                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out">
                                </span>
                            </button>
                            <span class="text-sm text-gray-600" x-text="statusAtivo ? 'Ativo' : 'Inativo'"></span>
                        </div>
                        <x-input-error :messages="$errors->get('status')" class="mt-2" />
                    </div>
                </div>

                {{-- Operações --}}
                <div class="mb-6">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-md font-semibold text-gray-900">Operações</h3>
                        <button type="button" x-on:click="addOperacao()"
                            class="inline-flex items-center px-3 py-1.5 bg-gray-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-gray-500 active:bg-gray-700 transition ease-in-out duration-150">
                            + Adicionar
                        </button>
                    </div>

                    <x-input-error :messages="$errors->get('operacoes')" class="mb-2" />

                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Porcentagem (%)</th>
                                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase w-10"></th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                <template x-for="(op, index) in operacoes" :key="index">
                                    <tr>
                                        <td class="px-3 py-2">
                                            <select
                                                x-model="op.tipo"
                                                :name="'operacoes[' + index + '][tipo]'"
                                                class="block w-full text-sm border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                                                required>
                                                <option value="compra">Compra</option>
                                                <option value="venda">Venda</option>
                                            </select>
                                        </td>
                                        <td class="px-3 py-2">
                                            <input
                                                type="number"
                                                step="0.1"
                                                min="0.1"
                                                max="100"
                                                x-model="op.porcentagem"
                                                :name="'operacoes[' + index + '][porcentagem]'"
                                                class="block w-full text-sm border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                                                placeholder="Ex: 5.0"
                                                required>
                                        </td>
                                        <td class="px-3 py-2 text-center">
                                            <button type="button"
                                                x-on:click="removeOperacao(index)"
                                                :disabled="operacoes.length <= 1"
                                                class="text-red-500 hover:text-red-700 disabled:opacity-30 disabled:cursor-not-allowed"
                                                title="Remover operação">
                                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                                                </svg>
                                            </button>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                </div>

                {{-- Botões --}}
                <div class="flex justify-end gap-3">
                    <x-secondary-button x-on:click="$dispatch('close-modal', 'criar-bot')">
                        Cancelar
                    </x-secondary-button>

                    <x-primary-button>
                        Criar Bot
                    </x-primary-button>
                </div>
            </form>
        </div>
    </x-modal>
</x-app-layout>
