<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            Bots
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">

            {{-- Card Bots --}}
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900">

                    {{-- Barra Ultima Atualizacao com polling automatico --}}
                    <div class="mb-4 px-4 py-2 bg-gray-100 rounded-md border border-gray-200 flex items-center justify-between"
                        x-data="{
                            timestamp: '{{ $ultimaAtualizacao ? \Carbon\Carbon::parse($ultimaAtualizacao)->format('d/m/Y H:i:s') : '' }}',
                            polling: null,
                            startPolling() {
                                this.polling = setInterval(() => this.fetchTimestamp(), 30000);
                            },
                            fetchTimestamp() {
                                fetch('{{ route('scheduler.ultimaAtualizacao') }}', {
                                    headers: { 'Accept': 'application/json' }
                                })
                                .then(r => r.json())
                                .then(data => {
                                    if (data.timestamp) this.timestamp = data.timestamp;
                                })
                                .catch(() => {});
                            },
                            checkCron() {
                                fetch('{{ route('scheduler.status') }}', {
                                    method: 'POST',
                                    headers: { 'X-CSRF-TOKEN': '{{ csrf_token() }}', 'Accept': 'application/json' }
                                })
                                .then(r => r.json())
                                .then(data => {
                                    Swal.fire({ icon: data.running ? 'info' : 'success', title: data.title, text: data.message, timer: 3000, showConfirmButton: false });
                                    this.fetchTimestamp();
                                })
                                .catch(() => {
                                    Swal.fire({ icon: 'error', title: 'Erro', text: 'Não foi possível verificar o cron.' });
                                });
                            }
                        }"
                        x-init="startPolling()">
                        <p class="text-sm text-gray-600">
                            <span class="font-medium">Última atualização:</span>
                            <span x-show="timestamp" x-text="timestamp"></span>
                            <span x-show="!timestamp" class="italic text-gray-400">Nunca executado</span>
                        </p>
                        <button type="button"
                            x-on:click="checkCron()"
                            class="inline-flex items-center gap-1 px-3 py-1 bg-gray-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-gray-500 active:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition ease-in-out duration-150"
                            title="Verificar e iniciar o cron se necessário">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            Cron
                        </button>
                    </div>

                    {{-- Flash messages via SweetAlert2 (ver @push('scripts') abaixo) --}}

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

                    <div x-data="{ tab: 'todos' }">
                        {{-- Abas de filtro --}}
                        <div class="border-b border-gray-200 mb-4">
                            <nav class="-mb-px flex gap-6" aria-label="Tabs">
                                <button type="button" x-on:click="tab = 'todos'"
                                    :class="tab === 'todos' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'"
                                    class="whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium transition-colors">
                                    Todos
                                </button>
                                <button type="button" x-on:click="tab = 'ativo'"
                                    :class="tab === 'ativo' ? 'border-green-500 text-green-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'"
                                    class="whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium transition-colors">
                                    Ativos
                                </button>
                                <button type="button" x-on:click="tab = 'inativo'"
                                    :class="tab === 'inativo' ? 'border-gray-500 text-gray-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'"
                                    class="whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium transition-colors">
                                    Inativos
                                </button>
                                <button type="button" x-on:click="tab = 'desabilitado'"
                                    :class="tab === 'desabilitado' ? 'border-red-500 text-red-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'"
                                    class="whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium transition-colors">
                                    Desabilitados
                                </button>
                                <button type="button" x-on:click="tab = 'concluido'"
                                    :class="tab === 'concluido' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'"
                                    class="whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium transition-colors">
                                    Concluídos
                                </button>
                            </nav>
                        </div>

                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                        <th class="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-10"></th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Moeda</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Último Valor</th>
                                        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">OP</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Criado em</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Atualizado em</th>
                                        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    @forelse ($bots as $bot)
                                        @php
                                            $s = $bot->status;
                                            $canActivate   = $s === 'inativo';
                                            $canDeactivate = $s === 'ativo';
                                            $canDisable    = in_array($s, ['ativo', 'inativo']);
                                            $canRefresh    = $s === 'ativo';
                                        @endphp
                                        <tr x-show="tab === 'todos' || tab === '{{ $s }}'">
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->id }}</td>
                                            <td class="px-3 py-4 text-center">
                                                <span class="inline-block w-2.5 h-2.5 rounded-full
                                                    @if($s === 'ativo') bg-green-500
                                                    @elseif($s === 'inativo') bg-gray-400
                                                    @elseif($s === 'desabilitado') bg-red-500
                                                    @elseif($s === 'concluido') bg-blue-500
                                                    @endif"
                                                    title="{{ ucfirst($s) }}">
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->nome }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->moeda->nome }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ $bot->ultimo_valor !== null ? number_format($bot->ultimo_valor, 2, ',', '.') : '—' }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700">{{ $bot->operacoes->whereNotNull('data_trade')->count() }}/{{ $bot->operacoes->count() }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ $bot->created_at->format('d/m/Y H:i') }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ $bot->updated_at->format('d/m/Y H:i') }}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm">
                                                <div class="flex items-center justify-center gap-1">
                                                    {{-- Ver detalhes --}}
                                                    <a href="{{ route('bots.show', $bot) }}"
                                                        class="p-1 text-gray-500 hover:text-gray-700 rounded transition-colors"
                                                        title="Ver detalhes">
                                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                                                            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
                                                            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                                        </svg>
                                                    </a>

                                                    {{-- Ativar --}}
                                                    <form method="POST" action="{{ route('bots.changeStatus', $bot) }}"
                                                        x-on:submit.prevent="Swal.fire({ title: 'Confirmar ação', text: 'Deseja ATIVAR o bot \'{{ $bot->nome }}\'?', icon: 'question', showCancelButton: true, confirmButtonText: 'Sim, ativar', cancelButtonText: 'Cancelar' }).then((r) => { if (r.isConfirmed) $el.submit(); })">
                                                        @csrf
                                                        @method('PATCH')
                                                        <input type="hidden" name="status" value="ativo">
                                                        <button type="submit" title="Ativar bot"
                                                            class="p-1 rounded transition-colors {{ $canActivate ? 'text-gray-500 hover:text-gray-700' : 'text-gray-300 cursor-not-allowed opacity-30' }}"
                                                            {{ $canActivate ? '' : 'disabled' }}>
                                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                                                                <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z"/>
                                                            </svg>
                                                        </button>
                                                    </form>

                                                    {{-- Inativar --}}
                                                    <form method="POST" action="{{ route('bots.changeStatus', $bot) }}"
                                                        x-on:submit.prevent="Swal.fire({ title: 'Confirmar ação', text: 'Deseja INATIVAR o bot \'{{ $bot->nome }}\'?', icon: 'question', showCancelButton: true, confirmButtonText: 'Sim, inativar', cancelButtonText: 'Cancelar' }).then((r) => { if (r.isConfirmed) $el.submit(); })">
                                                        @csrf
                                                        @method('PATCH')
                                                        <input type="hidden" name="status" value="inativo">
                                                        <button type="submit" title="Inativar bot"
                                                            class="p-1 rounded transition-colors {{ $canDeactivate ? 'text-gray-500 hover:text-gray-700' : 'text-gray-300 cursor-not-allowed opacity-30' }}"
                                                            {{ $canDeactivate ? '' : 'disabled' }}>
                                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                                                                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25v13.5m-7.5-13.5v13.5"/>
                                                            </svg>
                                                        </button>
                                                    </form>

                                                    {{-- Desabilitar --}}
                                                    <form method="POST" action="{{ route('bots.changeStatus', $bot) }}"
                                                        x-on:submit.prevent="Swal.fire({ title: 'Atenção!', text: 'Deseja DESABILITAR o bot \'{{ $bot->nome }}\'? Esta ação não pode ser revertida.', icon: 'warning', showCancelButton: true, confirmButtonText: 'Sim, desabilitar', cancelButtonText: 'Cancelar', confirmButtonColor: '#dc2626' }).then((r) => { if (r.isConfirmed) $el.submit(); })">
                                                        @csrf
                                                        @method('PATCH')
                                                        <input type="hidden" name="status" value="desabilitado">
                                                        <button type="submit" title="Desabilitar bot"
                                                            class="p-1 rounded transition-colors {{ $canDisable ? 'text-red-500 hover:text-red-700' : 'text-red-300 cursor-not-allowed opacity-30' }}"
                                                            {{ $canDisable ? '' : 'disabled' }}>
                                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                                                                <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                                            </svg>
                                                        </button>
                                                    </form>

                                                    {{-- Atualizar Valor --}}
                                                    <form method="POST" action="{{ route('bots.refreshPrice', $bot) }}"
                                                        x-on:submit.prevent="Swal.fire({ title: 'Atualizar valor', text: 'Atualizar o valor de referência do bot \'{{ $bot->nome }}\' com o preço atual de {{ $bot->moeda->nome }}/USDC?', icon: 'question', showCancelButton: true, confirmButtonText: 'Sim, atualizar', cancelButtonText: 'Cancelar' }).then((r) => { if (r.isConfirmed) $el.submit(); })">
                                                        @csrf
                                                        <button type="submit" title="Atualizar valor de referência"
                                                            class="p-1 rounded transition-colors {{ $canRefresh ? 'text-gray-500 hover:text-gray-700' : 'text-gray-300 cursor-not-allowed opacity-30' }}"
                                                            {{ $canRefresh ? '' : 'disabled' }}>
                                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                                                                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182M20.016 4.36v4.993"/>
                                                            </svg>
                                                        </button>
                                                    </form>
                                                </div>
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
    </div>

    {{-- Modal: Criar Bot --}}
    <x-modal name="criar-bot" maxWidth="2xl" focusable>
        <div class="p-6" x-data="{
            statusAtivo: {{ old('status', 'inativo') === 'ativo' ? 'true' : 'false' }},
            operacoes: [{ tipo: 'compra', porcentagem: '', valor_negociado: '' }],
            addOperacao() {
                this.operacoes.push({ tipo: 'compra', porcentagem: '', valor_negociado: '' });
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
                                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Valor USDC</th>
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
                                                :min="op.tipo === 'venda' ? '0.1' : '0'"
                                                max="100"
                                                x-model="op.porcentagem"
                                                :name="'operacoes[' + index + '][porcentagem]'"
                                                class="block w-full text-sm border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                                                :placeholder="op.tipo === 'venda' ? 'Ex: 5.0' : 'Ex: 0.0'"
                                                required>
                                        </td>
                                        <td class="px-3 py-2">
                                            <input
                                                type="number"
                                                step="0.01"
                                                min="0.01"
                                                x-model="op.valor_negociado"
                                                :name="'operacoes[' + index + '][valor_negociado]'"
                                                class="block w-full text-sm border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm"
                                                placeholder="Ex: 100.00"
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

    @push('scripts')
    @if (session('success'))
    <script>
        Swal.fire({ icon: 'success', title: 'Sucesso', text: @js(session('success')), timer: 3000, showConfirmButton: false });
    </script>
    @endif
    @if (session('error'))
    <script>
        Swal.fire({ icon: 'error', title: 'Erro', text: @js(session('error')) });
    </script>
    @endif
    @endpush
</x-app-layout>
