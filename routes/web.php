<?php

use App\Http\Controllers\BotController;
use App\Http\Controllers\LogController;
use App\Http\Controllers\MoedaController;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\WalletController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/dashboard', [BotController::class, 'index'])->name('dashboard');
    Route::post('/moedas/sync', [MoedaController::class, 'sync'])->name('moedas.sync');
    Route::resource('bots', BotController::class)->except(['index']);
    Route::patch('/bots/{bot}/status', [BotController::class, 'changeStatus'])->name('bots.changeStatus');
    Route::post('/bots/{bot}/refresh-price', [BotController::class, 'refreshPrice'])->name('bots.refreshPrice');
    Route::post('/scheduler/status', [BotController::class, 'schedulerStatus'])->name('scheduler.status');
    Route::get('/scheduler/ultima-atualizacao', [BotController::class, 'ultimaAtualizacao'])->name('scheduler.ultimaAtualizacao');
    Route::get('/carteira', [WalletController::class, 'index'])->name('wallet.index');
    Route::get('/wallet/balances', [WalletController::class, 'balances'])->name('wallet.balances');
    Route::get('/logs/{date?}', [LogController::class, 'index'])->name('logs.index');
});

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
