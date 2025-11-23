"use client";

import { useState } from 'react';

export type TimeframeType = 'intraday' | 'longterm';

export interface TimeframeConfig {
    type: TimeframeType;
    interval?: string;  // For intraday: '1m', '5m', '15m', '30m', '1h'
    period?: string;    // For longterm: '1wk', '1mo', '3mo', '6mo', '1y'
}

interface TimeframeSelectorProps {
    value: TimeframeConfig;
    onChange: (config: TimeframeConfig) => void;
}

const INTRADAY_INTERVALS = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '30m', label: '30 Minutes' },
    { value: '1h', label: '1 Hour' },
];

const LONGTERM_PERIODS = [
    { value: '1wk', label: '1 Week' },
    { value: '1mo', label: '1 Month' },
    { value: '3mo', label: '3 Months' },
    { value: '6mo', label: '6 Months' },
    { value: '1y', label: '1 Year' },
];

export default function TimeframeSelector({ value, onChange }: TimeframeSelectorProps) {
    const handleTypeChange = (type: TimeframeType) => {
        if (type === 'intraday') {
            onChange({
                type,
                interval: '1h',  // Default to 1 hour
                period: undefined
            });
        } else {
            onChange({
                type,
                interval: undefined,
                period: '1mo'  // Default to 1 month
            });
        }
    };

    const handleIntervalChange = (interval: string) => {
        onChange({
            ...value,
            interval
        });
    };

    const handlePeriodChange = (period: string) => {
        onChange({
            ...value,
            period
        });
    };

    return (
        <div className="space-y-4">
            {/* Timeframe Type Selection */}
            <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                    Analysis Timeframe
                </label>
                <div className="flex gap-4">
                    <button
                        onClick={() => handleTypeChange('intraday')}
                        className={`flex-1 px-4 py-3 rounded-lg border transition-all ${value.type === 'intraday'
                                ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                                : 'bg-slate-900/50 border-slate-700 text-slate-400 hover:border-slate-600'
                            }`}
                    >
                        <div className="text-sm font-semibold">Intraday</div>
                        <div className="text-xs opacity-70">Minutes to hours</div>
                    </button>
                    <button
                        onClick={() => handleTypeChange('longterm')}
                        className={`flex-1 px-4 py-3 rounded-lg border transition-all ${value.type === 'longterm'
                                ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                                : 'bg-slate-900/50 border-slate-700 text-slate-400 hover:border-slate-600'
                            }`}
                    >
                        <div className="text-sm font-semibold">Long-term</div>
                        <div className="text-xs opacity-70">Days to months</div>
                    </button>
                </div>
            </div>

            {/* Interval/Period Selection */}
            {value.type === 'intraday' ? (
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Interval
                    </label>
                    <select
                        value={value.interval || '1h'}
                        onChange={(e) => handleIntervalChange(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg 
                     focus:outline-none focus:ring-2 focus:ring-emerald-500
                     text-slate-200"
                    >
                        {INTRADAY_INTERVALS.map(({ value, label }) => (
                            <option key={value} value={value}>
                                {label}
                            </option>
                        ))}
                    </select>
                    <p className="mt-2 text-xs text-amber-400/70">
                        ⚠️ Intraday data only available for last 60 days
                    </p>
                </div>
            ) : (
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Period
                    </label>
                    <select
                        value={value.period || '1mo'}
                        onChange={(e) => handlePeriodChange(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg 
                     focus:outline-none focus:ring-2 focus:ring-emerald-500
                     text-slate-200"
                    >
                        {LONGTERM_PERIODS.map(({ value, label }) => (
                            <option key={value} value={label}>
                                {label}
                            </option>
                        ))}
                    </select>
                </div>
            )}
        </div>
    );
}
