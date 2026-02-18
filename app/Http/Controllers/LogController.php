<?php

namespace App\Http\Controllers;

use App\Services\TradeLogService;
use Illuminate\Http\Request;
use Illuminate\View\View;

class LogController extends Controller
{
    public function index(Request $request, TradeLogService $tradeLogService, ?string $date = null): View
    {
        $dates = $tradeLogService->getAvailableDates();
        $selectedDate = $date ?? now()->format('Y-m-d');
        $filter = $request->query('filter');

        $logs = $selectedDate
            ? $tradeLogService->getLogsByDate($selectedDate, $filter)
            : [];

        return view('logs.index', compact('dates', 'selectedDate', 'filter', 'logs'));
    }
}
