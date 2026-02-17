<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Builder;

class Moeda extends Model
{
    protected $table = 'moedas';

    protected $fillable = [
        'nome',
        'status',
    ];

    protected $casts = [
        'status' => 'boolean',
    ];

    public function bots(): HasMany
    {
        return $this->hasMany(Bot::class, 'moeda_id')
            ->orderBy('nome');
    }

    /**
     * Para buscar uma moeda já trazendo os bots:
     * Moeda::withRelated()->find($id)
     */
    public function scopeWithRelated(Builder $query): Builder
    {
        return $query->with('bots');
    }

    public static function findWithRelated(int $id): ?self
    {
        return static::query()->withRelated()->find($id);
    }
}
