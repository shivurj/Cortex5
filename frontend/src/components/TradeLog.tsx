import React, { useEffect, useState } from 'react';

interface Trade {
    id: number;
    timestamp: string;
    symbol: string;
    side: string;
    quantity: number;
    price: number;
    status: string;
    trade_signal: string;
}

export const TradeLog: React.FC = () => {
    const [trades, setTrades] = useState<Trade[]>([]);

    const fetchTrades = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/trades');
            const json = await res.json();
            setTrades(json);
        } catch (e) {
            console.error("Failed to fetch trades", e);
        }
    };

    useEffect(() => {
        fetchTrades();
        // Poll every 5 seconds
        const interval = setInterval(fetchTrades, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                <h3 className="text-slate-400 text-sm font-mono">EXECUTION LOG</h3>
                <span className="text-xs text-slate-600 animate-pulse">LIVE</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-slate-400">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-800/50">
                        <tr>
                            <th className="px-6 py-3">Time</th>
                            <th className="px-6 py-3">Symbol</th>
                            <th className="px-6 py-3">Side</th>
                            <th className="px-6 py-3">Qty</th>
                            <th className="px-6 py-3">Price</th>
                            <th className="px-6 py-3">Signal</th>
                            <th className="px-6 py-3">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {trades.map((trade) => (
                            <tr key={trade.id} className="border-b border-slate-800 hover:bg-slate-800/30">
                                <td className="px-6 py-4 font-mono text-xs">
                                    {new Date(trade.timestamp).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 font-bold text-white">{trade.symbol}</td>
                                <td className={`px-6 py-4 font-bold ${trade.side === 'BUY' ? 'text-emerald-500' : 'text-red-500'}`}>
                                    {trade.side}
                                </td>
                                <td className="px-6 py-4">{trade.quantity}</td>
                                <td className="px-6 py-4">${trade.price.toFixed(2)}</td>
                                <td className="px-6 py-4 text-xs font-mono">{trade.trade_signal}</td>
                                <td className="px-6 py-4">
                                    <span className={`px-2 py-1 rounded-full text-xs ${trade.status === 'EXECUTED' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-700 text-slate-400'
                                        }`}>
                                        {trade.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
