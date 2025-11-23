"use client";

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface Stock {
    ticker: string;
    name: string;
    sector: string;
}

interface TickerSelectorProps {
    selectedTickers: string[];
    onTickersChange: (tickers: string[]) => void;
    maxSelection?: number;
}

export default function TickerSelector({
    selectedTickers,
    onTickersChange,
    maxSelection = 10
}: TickerSelectorProps) {
    const [stocks, setStocks] = useState<Stock[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);

    // Fetch available stocks from API
    useEffect(() => {
        const fetchStocks = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/stocks');
                const data = await response.json();
                setStocks(data);
            } catch (error) {
                console.error('Failed to fetch stocks:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStocks();
    }, []);

    // Filter stocks based on search term
    const filteredStocks = stocks.filter(stock =>
        stock.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Add ticker to selection
    const addTicker = (ticker: string) => {
        if (selectedTickers.length < maxSelection && !selectedTickers.includes(ticker)) {
            onTickersChange([...selectedTickers, ticker]);
            setSearchTerm('');
            setIsOpen(false);
        }
    };

    // Remove ticker from selection
    const removeTicker = (ticker: string) => {
        onTickersChange(selectedTickers.filter(t => t !== ticker));
    };

    return (
        <div className="relative w-full">
            {/* Selected Tickers as Chips */}
            <div className="flex flex-wrap gap-2 mb-2">
                {selectedTickers.map(ticker => {
                    const stock = stocks.find(s => s.ticker === ticker);
                    return (
                        <div
                            key={ticker}
                            className="flex items-center gap-1 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-sm"
                        >
                            <span className="font-mono text-emerald-400">{ticker}</span>
                            {stock && (
                                <span className="text-slate-400 text-xs">• {stock.sector}</span>
                            )}
                            <button
                                onClick={() => removeTicker(ticker)}
                                className="ml-1 hover:text-red-400 transition-colors"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    );
                })}
                {selectedTickers.length === 0 && (
                    <span className="text-slate-500 text-sm">No stocks selected</span>
                )}
            </div>

            {/* Dropdown Input */}
            <div className="relative">
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                        setSearchTerm(e.target.value);
                        setIsOpen(true);
                    }}
                    onFocus={() => setIsOpen(true)}
                    placeholder={
                        selectedTickers.length >= maxSelection
                            ? `Maximum ${maxSelection} stocks selected`
                            : "Search stocks by ticker or name..."
                    }
                    disabled={selectedTickers.length >= maxSelection}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg 
                   focus:outline-none focus:ring-2 focus:ring-emerald-500 
                   disabled:opacity-50 disabled:cursor-not-allowed
                   font-mono text-sm"
                />

                {/* Dropdown List */}
                {isOpen && searchTerm && selectedTickers.length < maxSelection && (
                    <div className="absolute z-50 w-full mt-2 bg-slate-900 border border-slate-700 rounded-lg shadow-xl max-h-64 overflow-y-auto">
                        {loading ? (
                            <div className="px-4 py-3 text-slate-400 text-sm">Loading stocks...</div>
                        ) : filteredStocks.length === 0 ? (
                            <div className="px-4 py-3 text-slate-400 text-sm">No stocks found</div>
                        ) : (
                            filteredStocks.map(stock => (
                                <button
                                    key={stock.ticker}
                                    onClick={() => addTicker(stock.ticker)}
                                    disabled={selectedTickers.includes(stock.ticker)}
                                    className="w-full px-4 py-3 text-left hover:bg-slate-800 
                           disabled:opacity-50 disabled:cursor-not-allowed
                           border-b border-slate-800 last:border-b-0
                           transition-colors"
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <span className="font-mono text-emerald-400 font-semibold">
                                                {stock.ticker}
                                            </span>
                                            <span className="text-slate-300 text-sm ml-2">{stock.name}</span>
                                        </div>
                                        <span className="text-slate-500 text-xs">{stock.sector}</span>
                                    </div>
                                </button>
                            ))
                        )}
                    </div>
                )}
            </div>

            {/* Selection Counter */}
            <div className="mt-2 text-xs text-slate-500">
                {selectedTickers.length} / {maxSelection} stocks selected
            </div>

            {/* Click outside to close */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-40"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </div>
    );
}
