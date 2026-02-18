<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            Logs de Trade
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900">

                    {{-- Filtros --}}
                    <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
                        {{-- Selector de data --}}
                        <div class="flex items-center gap-2">
                            <label for="date-select" class="text-sm font-medium text-gray-700">Data:</label>
                            <select id="date-select"
                                onchange="window.location.href = '/logs/' + this.value + (window.location.search || '')"
                                class="text-sm border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-md shadow-sm">
                                @if(empty($dates))
                                    <option value="">Nenhum log disponível</option>
                                @endif
                                @foreach($dates as $d)
                                    <option value="{{ $d }}" @selected($d === $selectedDate)>
                                        {{ \Carbon\Carbon::parse($d)->format('d/m/Y') }}
                                    </option>
                                @endforeach
                            </select>
                        </div>

                        {{-- Abas de filtro --}}
                        @if($selectedDate)
                        <div class="flex gap-2">
                            @php
                                $base = route('logs.index', ['date' => $selectedDate]);
                                $filters = [
                                    null => 'Todos',
                                    'response' => 'Sucesso',
                                    'error' => 'Erros',
                                ];
                            @endphp
                            @foreach($filters as $key => $label)
                                <a href="{{ $base . ($key ? '?filter=' . $key : '') }}"
                                    class="px-3 py-1.5 text-xs font-semibold rounded-md border transition-colors
                                        {{ $filter === $key ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50' }}">
                                    {{ $label }}
                                </a>
                            @endforeach
                        </div>
                        @endif
                    </div>

                    {{-- Tabela de logs --}}
                    @if(empty($logs))
                        <p class="text-sm text-gray-500 text-center py-8">
                            @if(empty($dates))
                                Nenhum ficheiro de log encontrado.
                            @else
                                Nenhuma entrada encontrada para os filtros selecionados.
                            @endif
                        </p>
                    @else
                        <div class="overflow-x-auto" x-data="{ expanded: null }">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hora</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bot</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Op. ID</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoria</th>
                                        <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-10"></th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    @foreach($logs as $i => $log)
                                        <tr class="cursor-pointer hover:bg-gray-50" x-on:click="expanded = expanded === {{ $i }} ? null : {{ $i }}">
                                            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                                                {{ \Carbon\Carbon::parse($log['timestamp'])->format('H:i:s') }}
                                            </td>
                                            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                                                #{{ $log['bot_id'] }} {{ $log['bot_nome'] }}
                                            </td>
                                            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                                                #{{ $log['operacao_id'] }}
                                            </td>
                                            <td class="px-4 py-3 whitespace-nowrap text-sm">
                                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                                    {{ $log['tipo'] === 'compra' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800' }}">
                                                    {{ ucfirst($log['tipo']) }}
                                                </span>
                                            </td>
                                            <td class="px-4 py-3 whitespace-nowrap text-sm">
                                                @php $type = $log['type'] ?? 'unknown'; @endphp
                                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                                    @if($type === 'response') bg-blue-100 text-blue-800
                                                    @elseif($type === 'error') bg-red-100 text-red-800
                                                    @else bg-gray-100 text-gray-800
                                                    @endif">
                                                    {{ ucfirst($type) }}
                                                </span>
                                            </td>
                                            <td class="px-4 py-3 text-center text-sm text-gray-400">
                                                <svg class="w-4 h-4 inline transition-transform" :class="expanded === {{ $i }} && 'rotate-180'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                                </svg>
                                            </td>
                                        </tr>
                                        <tr x-show="expanded === {{ $i }}" x-cloak>
                                            <td colspan="6" class="px-4 py-3 bg-gray-50">
                                                <pre class="text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap max-h-64 overflow-y-auto">{{ json_encode($log['data'] ?? [], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) }}</pre>
                                            </td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    @endif

                </div>
            </div>
        </div>
    </div>
</x-app-layout>
