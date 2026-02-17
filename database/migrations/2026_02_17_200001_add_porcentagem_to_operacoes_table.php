<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('operacoes', function (Blueprint $table) {
            $table->decimal('porcentagem', 4, 1)->unsigned()->after('tipo');
        });
    }

    public function down(): void
    {
        Schema::table('operacoes', function (Blueprint $table) {
            $table->dropColumn('porcentagem');
        });
    }
};
