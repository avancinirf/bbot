<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Builder;

class Bot extends Model
{
    protected $table = 'bots';

    // Carrega automaticamente a moeda ao buscar um Bot (sem gerar loop)
    protected $with = [
        'moeda',
    ];

    protected $fillable = [
        'nome',
        'moeda_id',
        'ultimo_valor',
        'status',
    ];

    protected $casts = [
        'ultimo_valor' => 'decimal:10',
        'status' => 'string',
    ];

    public function moeda(): BelongsTo
    {
        return $this->belongsTo(Moeda::class, 'moeda_id');
    }

    public function operacoes(): HasMany
    {
        return $this->hasMany(Operacao::class, 'bot_id')
            ->orderByDesc('data_trade');
    }

    /**
     * Para buscar um bot já trazendo moeda + operações:
     * Bot::withRelated()->find($id)
     */
    public function scopeWithRelated(Builder $query): Builder
    {
        return $query->with(['moeda', 'operacoes']);
    }

    public static function findWithRelated(int $id): ?self
    {
        return static::query()->withRelated()->find($id);
    }
}
