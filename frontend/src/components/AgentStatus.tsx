import React from 'react';
import { AgentType } from '../hooks/useAgentStream';
import { Database, Brain, Activity, Shield, Zap } from 'lucide-react';

interface AgentStatusProps {
    activeAgent: AgentType | null;
}

const agents = [
    { id: 'DataAgent', name: 'Data Agent', icon: Database, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { id: 'SentimentAgent', name: 'Sentiment Agent', icon: Brain, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { id: 'QuantAgent', name: 'Quant Agent', icon: Activity, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
    { id: 'RiskAgent', name: 'Risk Agent', icon: Shield, color: 'text-red-500', bg: 'bg-red-500/10' },
    { id: 'ExecutionAgent', name: 'Execution Agent', icon: Zap, color: 'text-green-500', bg: 'bg-green-500/10' },
];

export const AgentStatus: React.FC<AgentStatusProps> = ({ activeAgent }) => {
    return (
        <div className="flex justify-between items-center w-full max-w-4xl mx-auto p-6 bg-slate-900 rounded-xl border border-slate-800">
            {agents.map((agent, index) => {
                const isActive = activeAgent === agent.id;
                const Icon = agent.icon;

                return (
                    <div key={agent.id} className="flex flex-col items-center relative">
                        {/* Connector Line */}
                        {index < agents.length - 1 && (
                            <div className={`absolute top-6 left-1/2 w-full h-0.5 -z-10 ${isActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-800'
                                }`} style={{ width: 'calc(100% + 2rem)' }} />
                        )}

                        <div className={`
              w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300
              ${isActive ? `${agent.bg} ${agent.color} ring-2 ring-offset-2 ring-offset-slate-900 ring-${agent.color.split('-')[1]}-500 scale-110` : 'bg-slate-800 text-slate-500'}
            `}>
                            <Icon size={24} />
                        </div>
                        <span className={`mt-2 text-xs font-medium ${isActive ? 'text-white' : 'text-slate-500'}`}>
                            {agent.name}
                        </span>
                        {isActive && (
                            <span className="absolute -bottom-6 text-[10px] text-emerald-400 animate-bounce">
                                Thinking...
                            </span>
                        )}
                    </div>
                );
            })}
        </div>
    );
};
