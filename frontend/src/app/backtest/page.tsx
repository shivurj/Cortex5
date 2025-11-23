"use client";

import { useState, useEffect } from 'react';
import { Play, Calendar, DollarSign, Clock } from 'lucide-react';
import TickerSelector from '@/components/TickerSelector';
import TimeframeSelector, { TimeframeConfig } from '@/components/TimeframeSelector';
import EquityCurve from '@/components/EquityCurve';
import MetricsDashboard from '@/components/MetricsDashboard';

export default function BacktestPage() {
    const [selectedTickers, setSelectedTickers] = useState<string[]>(['AAPL']);
    const [timeframe, setTimeframe] = useState<TimeframeConfig>({
        type: 'longterm',
        period: '1mo'
    });
    const [initialCapital, setInitialCapital] = useState(100000);
    const [startDate, setStartDate] = useState('2024-01-01');
    const [endDate, setEndDate] = useState('2024-11-23');

    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<any>(null);

    // Auto-adjust dates when switching to intraday
    useEffect(() => {
        if (timeframe.type === 'intraday') {
            const today = new Date();
            const sixtyDaysAgo = new Date(today);
            sixtyDaysAgo.setDate(today.getDate() - 30); // Use 30 days for safety

            setStartDate(sixtyDaysAgo.toISOString().split('T')[0]);
            setEndDate(today.toISOString().split('T')[0]);
        }
    }, [timeframe.type]);

    const handleRunBacktest = async () => {
        // Validate intraday date range
        if (timeframe.type === 'intraday') {
            const start = new Date(startDate);
            const end = new Date(endDate);
            const daysDiff = Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));

            if (daysDiff > 60) {
                alert(`Intraday data is only available for the last 60 days. Your selected range is ${daysDiff} days. Please reduce the date range.`);
                return;
            }
        }

        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/backtest/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tickers: selectedTickers,
                    start_date: startDate,
                    end_date: endDate,
                    interval: timeframe.type === 'intraday' ? timeframe.interval : '1d',
                    initial_capital: initialCapital
                })
            });

            const data = await response.json();

            // Check for error response
            if (!response.ok) {
                throw new Error(data.detail || 'Backtest failed');
            }

            // Fetch full results
            const resultsResponse = await fetch(`http://localhost:8000/api/backtest/results/${data.backtest_id}`);
            const fullResults = await resultsResponse.json();

            setResults(fullResults);
        } catch (error) {
            console.error('Backtest failed:', error);
            alert(`Backtest failed: ${error instanceof Error ? error.message : 'Unknown error'}. Check console for details.`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold mb-2">Backtest Engine</h1>
                <p className="text-slate-400">Test your strategy against historical data</p>
            </div>

            {/* Configuration Panel */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 space-y-6">
                <h2 className="text-xl font-bold">Backtest Configuration</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Left Column */}
                    <div className="space-y-6">
                        {/* Ticker Selection */}
                        <div>
                            <label className="text-sm font-medium text-slate-300 mb-2 block">
                                Select Stocks
                            </label>
                            <TickerSelector
                                selectedTickers={selectedTickers}
                                onTickersChange={setSelectedTickers}
                                maxSelection={10}
                            />
                        </div>

                        {/* Date Range */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium text-slate-300 mb-2 block flex items-center gap-2">
                                    <Calendar size={16} className="text-emerald-500" />
                                    Start Date
                                </label>
                                <div className="relative">
                                    <input
                                        type="date"
                                        value={startDate}
                                        onChange={(e) => setStartDate(e.target.value)}
                                        className="w-full px-4 py-3 bg-slate-950 border border-slate-700 rounded-lg 
                             focus:outline-none focus:ring-2 focus:ring-emerald-500
                             text-white placeholder-slate-500 color-scheme-dark"
                                        style={{ colorScheme: 'dark' }}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-slate-300 mb-2 block flex items-center gap-2">
                                    <Calendar size={16} className="text-emerald-500" />
                                    End Date
                                </label>
                                <div className="relative">
                                    <input
                                        type="date"
                                        value={endDate}
                                        onChange={(e) => setEndDate(e.target.value)}
                                        className="w-full px-4 py-3 bg-slate-950 border border-slate-700 rounded-lg 
                             focus:outline-none focus:ring-2 focus:ring-emerald-500
                             text-white placeholder-slate-500 color-scheme-dark"
                                        style={{ colorScheme: 'dark' }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right Column */}
                    <div className="space-y-6">
                        {/* Timeframe */}
                        <TimeframeSelector
                            value={timeframe}
                            onChange={setTimeframe}
                        />

                        {/* Initial Capital */}
                        <div>
                            <label className="text-sm font-medium text-slate-300 mb-2 block flex items-center gap-2">
                                <DollarSign size={16} className="text-emerald-500" />
                                Initial Capital
                            </label>
                            <div className="relative">
                                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-mono">$</span>
                                <input
                                    type="number"
                                    value={initialCapital}
                                    onChange={(e) => setInitialCapital(Number(e.target.value))}
                                    className="w-full pl-8 pr-4 py-3 bg-slate-950 border border-slate-700 rounded-lg 
                           focus:outline-none focus:ring-2 focus:ring-emerald-500 
                           text-white font-mono text-lg"
                                    step="1000"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Run Button */}
                <button
                    onClick={handleRunBacktest}
                    disabled={loading || selectedTickers.length === 0}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 
                   disabled:text-slate-600 text-white font-bold py-4 rounded-lg 
                   flex items-center justify-center gap-2 transition-all"
                >
                    {loading ? (
                        <>
                            <Clock size={20} className="animate-spin" />
                            Running Backtest...
                        </>
                    ) : (
                        <>
                            <Play size={20} />
                            RUN BACKTEST
                        </>
                    )}
                </button>
            </div>

            {/* Results */}
            {results && (
                <div className="space-y-6">
                    <h2 className="text-2xl font-bold">Results</h2>

                    {/* Metrics Dashboard */}
                    <MetricsDashboard metrics={results.metrics} />

                    {/* Equity Curve */}
                    <EquityCurve
                        data={results.equity_curve}
                        initialCapital={initialCapital}
                    />

                    {/* Trade Log */}
                    <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
                        <h3 className="text-lg font-bold mb-4">Completed Trades</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-slate-800">
                                        <th className="text-left py-2 px-4 font-mono text-slate-400">Ticker</th>
                                        <th className="text-left py-2 px-4 font-mono text-slate-400">Entry</th>
                                        <th className="text-left py-2 px-4 font-mono text-slate-400">Exit</th>
                                        <th className="text-right py-2 px-4 font-mono text-slate-400">Qty</th>
                                        <th className="text-right py-2 px-4 font-mono text-slate-400">Entry $</th>
                                        <th className="text-right py-2 px-4 font-mono text-slate-400">Exit $</th>
                                        <th className="text-right py-2 px-4 font-mono text-slate-400">P&L</th>
                                        <th className="text-right py-2 px-4 font-mono text-slate-400">%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.matched_trades && results.matched_trades.length > 0 ? (
                                        results.matched_trades.map((trade: any, i: number) => (
                                            <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                                                <td className="py-2 px-4 font-mono font-semibold text-emerald-400">
                                                    {trade.ticker}
                                                </td>
                                                <td className="py-2 px-4 font-mono text-xs text-slate-400">
                                                    {new Date(trade.entry_date).toLocaleString(undefined, {
                                                        month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
                                                    })}
                                                </td>
                                                <td className="py-2 px-4 font-mono text-xs text-slate-400">
                                                    {new Date(trade.exit_date).toLocaleString(undefined, {
                                                        month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
                                                    })}
                                                </td>
                                                <td className="py-2 px-4 text-right font-mono">{trade.quantity}</td>
                                                <td className="py-2 px-4 text-right font-mono text-slate-400">${trade.entry_price.toFixed(2)}</td>
                                                <td className="py-2 px-4 text-right font-mono text-slate-400">${trade.exit_price.toFixed(2)}</td>
                                                <td className={`py-2 px-4 text-right font-mono font-bold ${trade.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                    {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                                                </td>
                                                <td className={`py-2 px-4 text-right font-mono font-bold ${trade.pnl_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                    {trade.pnl_pct >= 0 ? '+' : ''}{trade.pnl_pct.toFixed(2)}%
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan={8} className="py-8 text-center text-slate-500 italic">
                                                No completed trades yet.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Agent Activity Log */}
                    <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 mt-6">
                        <h3 className="text-lg font-bold mb-4">Agent Activity Log</h3>
                        <div className="h-96 overflow-y-auto font-mono text-xs bg-black/50 p-4 rounded-lg border border-slate-800">
                            {results.agent_logs && results.agent_logs.length > 0 ? (
                                results.agent_logs.map((log: any, i: number) => (
                                    <div key={i} className="mb-2 border-l-2 border-slate-700 pl-3 py-1 hover:bg-slate-800/30 transition-colors">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-slate-500">
                                                {new Date(log.step_timestamp || log.timestamp).toLocaleString()}
                                            </span>
                                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${log.agent === 'DataAgent' ? 'bg-blue-500/20 text-blue-400' :
                                                    log.agent === 'SentimentAgent' ? 'bg-purple-500/20 text-purple-400' :
                                                        log.agent === 'QuantAgent' ? 'bg-emerald-500/20 text-emerald-400' :
                                                            log.agent === 'RiskAgent' ? 'bg-orange-500/20 text-orange-400' :
                                                                log.agent === 'ExecutionAgent' ? 'bg-red-500/20 text-red-400' :
                                                                    'bg-slate-500/20 text-slate-400'
                                                }`}>
                                                {log.agent}
                                            </span>
                                            <span className={`text-[10px] uppercase ${log.type === 'error' ? 'text-red-500 font-bold' :
                                                    log.type === 'warning' ? 'text-yellow-500' :
                                                        log.type === 'success' ? 'text-emerald-500' :
                                                            'text-slate-600'
                                                }`}>
                                                {log.type}
                                            </span>
                                        </div>
                                        <div className="text-slate-300 pl-1">
                                            {log.message}
                                        </div>
                                        {log.data && (
                                            <pre className="mt-1 text-slate-500 overflow-x-auto">
                                                {JSON.stringify(log.data, null, 2)}
                                            </pre>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="text-center text-slate-500 italic py-10">
                                    No agent logs available.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
