<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            Carteira
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900"
                    x-data="{
                        balances: [],
                        timestamp: '',
                        loading: true,
                        error: '',
                        polling: null,
                        formatNumber(val) {
                            return Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
                        },
                        async fetchBalances(refresh = false) {
                            try {
                                const url = '{{ route('wallet.balances') }}' + (refresh ? '?refresh=1' : '');
                                const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
                                const data = await res.json();
                                if (data.error) {
                                    this.error = data.error;
                                } else {
                                    this.balances = data.balances;
                                    if (data.timestamp) this.timestamp = data.timestamp;
                                    this.error = '';
                                }
                            } catch (e) {
                                this.error = 'Erro ao buscar saldos.';
                            } finally {
                                this.loading = false;
                            }
                        },
                        async refreshBalances() {
                            this.loading = true;
                            await this.fetchBalances(true);
                        },
                        startPolling() {
                            this.polling = setInterval(() => this.fetchBalances(false), 600000);
                        }
                    }"
                    x-init="fetchBalances(false); startPolling();">

                    {{-- Barra Ultima Atualizacao da Carteira --}}
                    <div class="mb-4 px-4 py-2 bg-gray-100 rounded-md border border-gray-200 flex items-center justify-between">
                        <p class="text-sm text-gray-600">
                            <span class="font-medium">Última atualização:</span>
                            <span x-show="timestamp" x-text="timestamp"></span>
                            <span x-show="!timestamp && !loading" class="italic text-gray-400">Nunca executado</span>
                            <span x-show="!timestamp && loading" class="italic text-gray-400">Carregando...</span>
                        </p>
                        <button type="button"
                            x-on:click="refreshBalances()"
                            :disabled="loading"
                            class="inline-flex items-center p-2 bg-gray-600 border border-transparent rounded-md text-white hover:bg-gray-500 active:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition ease-in-out duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Atualizar saldos da carteira">
                            <svg class="w-4 h-4" :class="loading && 'animate-spin'" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182M20.016 4.36v4.993"/>
                            </svg>
                        </button>
                    </div>

                    <h3 class="text-lg font-semibold mb-4">Saldos</h3>

                    {{-- Erro --}}
                    <div x-show="error" x-cloak class="mb-4 p-4 rounded-md bg-red-50 border border-red-200">
                        <p class="text-sm text-red-800" x-text="error"></p>
                    </div>

                    {{-- Tabela de saldos --}}
                    <div class="overflow-x-auto max-h-[280px] overflow-y-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50 sticky top-0 z-10">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Moeda</th>
                                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Disponível</th>
                                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Bloqueado</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                <template x-if="loading && balances.length === 0">
                                    <tr>
                                        <td colspan="3" class="px-6 py-4 text-center text-sm text-gray-500">
                                            Carregando saldos...
                                        </td>
                                    </tr>
                                </template>
                                <template x-if="!loading && balances.length === 0 && !error">
                                    <tr>
                                        <td colspan="3" class="px-6 py-4 text-center text-sm text-gray-500">
                                            Nenhum saldo encontrado.
                                        </td>
                                    </tr>
                                </template>
                                <template x-for="(b, i) in balances" :key="i">
                                    <tr>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900" x-text="b.asset"></td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right" x-text="formatNumber(b.free)"></td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right" x-text="formatNumber(b.locked)"></td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>
