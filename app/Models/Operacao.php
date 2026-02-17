<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Builder;

class Operacao extends Model
{
    protected $table = 'operacoes';

    // Carrega automaticamente o bot (e, por consequência, o bot já traz a moeda via $with do Bot)
    protected $with = [
        'bot',
    ];

    protected $fillable = [
        'bot_id',
        'tipo',
        'porcentagem',
        'valor_anterior',
        'valor_trade',
        'data_trade',
    ];

    protected $casts = [
        'porcentagem' => 'decimal:1',
        'valor_anterior' => 'decimal:10',
        'valor_trade' => 'decimal:10',
        'data_trade' => 'datetime',
        'tipo' => 'string',
    ];

    public function bot(): BelongsTo
    {
        return $this->belongsTo(Bot::class, 'bot_id');
    }

    /**
     * Para buscar uma operação já trazendo bot + moeda do bot:
     * Operacao::withRelated()->find($id)
     */
    public function scopeWithRelated(Builder $query): Builder
    {
        return $query->with(['bot', 'bot.moeda']);
    }

    public static function findWithRelated(int $id): ?self
    {
        return static::query()->withRelated()->find($id);
    }
}
