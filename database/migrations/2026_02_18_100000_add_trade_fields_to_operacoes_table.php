<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('operacoes', function (Blueprint $table) {
            $table->decimal('valor_negociado', 20, 10)->nullable()->after('porcentagem');
            $table->string('binance_order_id')->nullable()->after('data_trade');
            $table->decimal('quantidade_executada', 20, 10)->nullable()->after('binance_order_id');
            $table->decimal('comissao_total', 20, 10)->nullable()->after('quantidade_executada');
        });
    }

    public function down(): void
    {
        Schema::table('operacoes', function (Blueprint $table) {
            $table->dropColumn(['valor_negociado', 'binance_order_id', 'quantidade_executada', 'comissao_total']);
        });
    }
};
