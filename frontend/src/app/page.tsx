"use client";

import { useState } from 'react';
import { AgentStatus } from '@/components/AgentStatus';
import { PriceChart } from '@/components/PriceChart';
import { TradeLog } from '@/components/TradeLog';
import { useAgentStream } from '@/hooks/useAgentStream';
import { Search, Play, Terminal } from 'lucide-react';

export default function Dashboard() {
  const { isConnected, activeAgent, logs, analyzeTicker } = useAgentStream();
  const [ticker, setTicker] = useState('AAPL');

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker) {
      analyzeTicker(ticker);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Top Section: Controls & Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Left: Input Control */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Search size={20} className="text-emerald-500" />
              Target Acquisition
            </h2>
            <form onSubmit={handleAnalyze} className="space-y-4">
              <div>
                <label className="text-xs font-mono text-slate-500 uppercase">Ticker Symbol</label>
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-xl font-mono focus:outline-none focus:border-emerald-500 transition-colors"
                  placeholder="AAPL"
                />
              </div>
              <button
                type="submit"
                disabled={!isConnected}
                className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all"
              >
                <Play size={18} />
                INITIATE ANALYSIS
              </button>
            </form>
            <div className="mt-4 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Neural Link:</span>
              <span className={isConnected ? "text-emerald-500" : "text-red-500"}>
                {isConnected ? "CONNECTED" : "OFFLINE"}
              </span>
            </div>
          </div>

          {/* Mini Log Console */}
          <div className="bg-slate-950 rounded-xl border border-slate-800 p-4 h-[300px] flex flex-col font-mono text-xs overflow-hidden">
            <div className="flex items-center gap-2 text-slate-400 mb-2 pb-2 border-b border-slate-800">
              <Terminal size={14} />
              <span>SYSTEM LOGS</span>
            </div>
            <div className="flex-1 overflow-y-auto space-y-1 scrollbar-thin scrollbar-thumb-slate-800">
              {logs.length === 0 && <span className="text-slate-700">Waiting for input...</span>}
              {logs.map((log, i) => (
                <div key={i} className="flex gap-2">
                  <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                  <span className={
                    log.type === 'error' ? 'text-red-500' :
                      log.type === 'success' ? 'text-emerald-500' :
                        log.agent === 'System' ? 'text-blue-400' : 'text-slate-300'
                  }>
                    <span className="font-bold">{log.agent}:</span> {log.message}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Agent Visualization & Charts */}
        <div className="lg:col-span-2 space-y-6">
          <AgentStatus activeAgent={activeAgent} />
          <PriceChart ticker={ticker} />
        </div>
      </div>

      {/* Bottom: Trade Logs */}
      <TradeLog />
    </div>
  );
}
