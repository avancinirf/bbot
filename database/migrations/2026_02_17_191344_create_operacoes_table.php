<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('operacoes', function (Blueprint $table) {
            $table->id();

            $table->foreignId('bot_id')
                ->constrained('bots')
                ->cascadeOnDelete();

            $table->enum('tipo', ['compra', 'venda']);

            $table->decimal('valor_anterior', 20, 10)->nullable();
            $table->decimal('valor_trade', 20, 10);

            $table->dateTime('data_trade');

            $table->timestamps();

            $table->index(['bot_id', 'data_trade']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('operacoes');
    }
};
