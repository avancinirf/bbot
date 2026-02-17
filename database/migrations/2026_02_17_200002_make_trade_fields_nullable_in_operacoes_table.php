<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('operacoes', function (Blueprint $table) {
            $table->decimal('valor_trade', 20, 10)->nullable()->change();
            $table->dateTime('data_trade')->nullable()->change();
        });
    }

    public function down(): void
    {
        Schema::table('operacoes', function (Blueprint $table) {
            $table->decimal('valor_trade', 20, 10)->nullable(false)->change();
            $table->dateTime('data_trade')->nullable(false)->change();
        });
    }
};
