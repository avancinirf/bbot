<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('bots', function (Blueprint $table) {
            $table->id();
            $table->string('nome');

            $table->foreignId('moeda_id')
                ->constrained('moedas')
                ->cascadeOnDelete();

            $table->decimal('valor_anterior', 20, 10)->nullable();

            $table->enum('status', ['inativo', 'ativo', 'desabilitado', 'concluido'])
                ->default('inativo');

            $table->timestamps();

            $table->index('moeda_id');
            $table->unique(['moeda_id', 'nome']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('bots');
    }
};
