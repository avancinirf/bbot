<?php

use App\Http\Controllers\BotController;
use App\Http\Controllers\MoedaController;
use App\Http\Controllers\ProfileController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/dashboard', [BotController::class, 'index'])->name('dashboard');
    Route::post('/moedas/sync', [MoedaController::class, 'sync'])->name('moedas.sync');
    Route::resource('bots', BotController::class)->except(['index']);
});

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
