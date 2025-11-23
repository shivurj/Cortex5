import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface PriceData {
    timestamp: string;
    close: number;
}

interface PriceChartProps {
    ticker: string;
}

export const PriceChart: React.FC<PriceChartProps> = ({ ticker }) => {
    const [data, setData] = useState<PriceData[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!ticker) return;

        const fetchData = async () => {
            setLoading(true);
            try {
                const res = await fetch(`http://localhost:8000/api/market-data/${ticker}`);
                const json = await res.json();
                // Reverse to show oldest to newest if API returns newest first
                setData(json.reverse());
            } catch (e) {
                console.error("Failed to fetch market data", e);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [ticker]);

    if (loading) return <div className="h-64 flex items-center justify-center text-slate-500">Loading Chart...</div>;
    if (data.length === 0) return <div className="h-64 flex items-center justify-center text-slate-500">No Data Available</div>;

    return (
        <div className="h-64 w-full bg-slate-900 rounded-xl border border-slate-800 p-4">
            <h3 className="text-slate-400 text-sm mb-4 font-mono">PRICE ACTION: {ticker}</h3>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="timestamp"
                        tickFormatter={(val) => new Date(val).toLocaleDateString()}
                        stroke="#64748b"
                        fontSize={12}
                    />
                    <YAxis
                        domain={['auto', 'auto']}
                        stroke="#64748b"
                        fontSize={12}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }}
                        itemStyle={{ color: '#10b981' }}
                        labelStyle={{ color: '#94a3b8' }}
                    />
                    <Line
                        type="monotone"
                        dataKey="close"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};
