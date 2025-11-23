"use client";

import { TrendingUp, TrendingDown, Activity, Target, AlertTriangle, Award } from 'lucide-react';

interface MetricsDashboardProps {
    metrics: {
        total_return?: number;
        cagr?: number;
        sharpe_ratio?: number;
        sortino_ratio?: number;
        max_drawdown?: number;
        volatility?: number;
        win_rate?: number;
        profit_factor?: number;
        total_trades?: number;
    };
}

export default function MetricsDashboard({ metrics }: MetricsDashboardProps) {
    const metricCards = [
        {
            label: 'Total Return',
            value: `${((metrics.total_return || 0) * 100).toFixed(2)}%`,
            icon: metrics.total_return && metrics.total_return > 0 ? TrendingUp : TrendingDown,
            color: metrics.total_return && metrics.total_return > 0 ? 'text-emerald-500' : 'text-red-500',
            bgColor: metrics.total_return && metrics.total_return > 0 ? 'bg-emerald-500/10' : 'bg-red-500/10'
        },
        {
            label: 'CAGR',
            value: `${((metrics.cagr || 0) * 100).toFixed(2)}%`,
            icon: Activity,
            color: 'text-blue-500',
            bgColor: 'bg-blue-500/10'
        },
        {
            label: 'Sharpe Ratio',
            value: (metrics.sharpe_ratio || 0).toFixed(2),
            icon: Target,
            color: 'text-purple-500',
            bgColor: 'bg-purple-500/10'
        },
        {
            label: 'Max Drawdown',
            value: `${((metrics.max_drawdown || 0) * 100).toFixed(2)}%`,
            icon: AlertTriangle,
            color: 'text-amber-500',
            bgColor: 'bg-amber-500/10'
        },
        {
            label: 'Volatility',
            value: `${((metrics.volatility || 0) * 100).toFixed(2)}%`,
            icon: Activity,
            color: 'text-slate-400',
            bgColor: 'bg-slate-500/10'
        },
        {
            label: 'Win Rate',
            value: `${((metrics.win_rate || 0) * 100).toFixed(1)}%`,
            icon: Award,
            color: 'text-emerald-500',
            bgColor: 'bg-emerald-500/10'
        },
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {metricCards.map((metric, index) => {
                const Icon = metric.icon;
                return (
                    <div
                        key={index}
                        className="bg-slate-900 rounded-xl border border-slate-800 p-4"
                    >
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-mono text-slate-500 uppercase">
                                {metric.label}
                            </span>
                            <div className={`p-2 rounded-lg ${metric.bgColor}`}>
                                <Icon size={16} className={metric.color} />
                            </div>
                        </div>
                        <div className={`text-2xl font-bold ${metric.color}`}>
                            {metric.value}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
