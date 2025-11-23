"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface EquityCurveProps {
    data: Array<{
        timestamp: string;
        equity: number;
    }>;
    initialCapital: number;
}

export default function EquityCurve({ data, initialCapital }: EquityCurveProps) {
    if (!data || data.length === 0) {
        return (
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
                <h3 className="text-lg font-bold mb-4">Equity Curve</h3>
                <div className="h-64 flex items-center justify-center text-slate-500">
                    No data available
                </div>
            </div>
        );
    }

    // Format data for chart
    const chartData = data.map(point => ({
        ...point,
        date: new Date(point.timestamp).toLocaleString(undefined, {
            month: 'numeric',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }),
        equity: point.equity,
        benchmark: initialCapital  // Flat line for comparison
    }));

    return (
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
            <h3 className="text-lg font-bold mb-4">Equity Curve</h3>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="date"
                        stroke="#94a3b8"
                        style={{ fontSize: '12px' }}
                    />
                    <YAxis
                        stroke="#94a3b8"
                        style={{ fontSize: '12px' }}
                        tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #475569',
                            borderRadius: '8px'
                        }}
                        formatter={(value: number) => [`$${value.toFixed(2)}`, 'Equity']}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="equity"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                        name="Strategy"
                    />
                    <Line
                        type="monotone"
                        dataKey="benchmark"
                        stroke="#64748b"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                        name="Initial Capital"
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
