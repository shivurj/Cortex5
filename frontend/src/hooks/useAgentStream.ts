import { useState, useEffect, useRef, useCallback } from 'react';

export type AgentType = 'DataAgent' | 'SentimentAgent' | 'QuantAgent' | 'RiskAgent' | 'ExecutionAgent' | 'System';

export interface AgentLog {
    timestamp: string;
    agent: AgentType;
    message: string;
    type: 'info' | 'error' | 'success' | 'status' | 'result';
    data?: any;
}

export const useAgentStream = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [activeAgent, setActiveAgent] = useState<AgentType | null>(null);
    const [logs, setLogs] = useState<AgentLog[]>([]);
    const [tradeDecision, setTradeDecision] = useState<any>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/ws/stream');
        wsRef.current = ws;

        ws.onopen = () => {
            setIsConnected(true);
            addLog('System', 'Connected to Cortex5 Neural Link', 'success');
        };

        ws.onclose = () => {
            setIsConnected(false);
            addLog('System', 'Disconnected from Cortex5 Neural Link', 'error');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleMessage(data);
            } catch (e) {
                console.error('Failed to parse WebSocket message', e);
            }
        };

        return () => {
            ws.close();
        };
    }, []);

    const handleMessage = (data: any) => {
        const { type, agent, message, timestamp, data: payload } = data;

        // Update active agent if it's a status update
        if (type === 'status' && agent !== 'System') {
            setActiveAgent(agent);
        }

        // If execution is complete, clear active agent
        if (type === 'result' && agent === 'ExecutionAgent') {
            setActiveAgent(null);
            setTradeDecision(payload);
        }

        setLogs((prev) => [...prev, {
            timestamp: timestamp || new Date().toISOString(),
            agent: agent || 'System',
            message: message || JSON.stringify(payload),
            type: type,
            data: payload
        }]);
    };

    const addLog = (agent: AgentType, message: string, type: 'info' | 'error' | 'success') => {
        setLogs((prev) => [...prev, {
            timestamp: new Date().toISOString(),
            agent,
            message,
            type
        }]);
    };

    const analyzeTicker = useCallback((ticker: string) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            setLogs([]); // Clear previous logs
            setTradeDecision(null);
            wsRef.current.send(JSON.stringify({ action: 'analyze', ticker }));
        } else {
            console.error('WebSocket is not connected');
        }
    }, []);

    return {
        isConnected,
        activeAgent,
        logs,
        tradeDecision,
        analyzeTicker
    };
};
