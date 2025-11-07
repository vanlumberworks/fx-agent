/**
 * React Hook for Forex Agent System Streaming API
 *
 * This custom hook provides a clean interface for consuming the streaming API
 * in React applications. It handles connection management, event parsing,
 * and state updates automatically.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { analyze, state, isAnalyzing, error } = useForexAnalysis();
 *
 *   const handleAnalyze = () => {
 *     analyze("Analyze gold trading");
 *   };
 *
 *   return (
 *     <div>
 *       <button onClick={handleAnalyze} disabled={isAnalyzing}>
 *         Analyze
 *       </button>
 *       {state.decision && <div>Action: {state.decision.action}</div>}
 *     </div>
 *   );
 * }
 * ```
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import type {
  AnalysisResult,
  QueryContext,
  AgentResult,
  Decision,
  EventType,
  AgentName,
  StartEventData,
  QueryParsedEventData,
  AgentUpdateEventData,
  RiskUpdateEventData,
  DecisionEventData,
  CompleteEventData,
  ErrorEventData,
} from './types';

// ============================================================================
// Types
// ============================================================================

export interface AnalysisState {
  query: string | null;
  queryContext: QueryContext | null;
  newsResult: AgentResult | null;
  technicalResult: AgentResult | null;
  fundamentalResult: AgentResult | null;
  riskResult: AgentResult | null;
  decision: Decision | null;
  finalResult: AnalysisResult | null;
  progress: {
    stage: 'idle' | 'parsing' | 'analyzing' | 'risk' | 'decision' | 'complete';
    agentsCompleted: number;
    totalAgents: number;
  };
}

export interface UseForexAnalysisOptions {
  apiUrl?: string;
  onStart?: () => void;
  onComplete?: (result: AnalysisResult) => void;
  onError?: (error: string) => void;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
}

export interface UseForexAnalysisReturn {
  analyze: (query: string) => void;
  cancel: () => void;
  state: AnalysisState;
  isAnalyzing: boolean;
  error: string | null;
}

// ============================================================================
// Initial State
// ============================================================================

const initialState: AnalysisState = {
  query: null,
  queryContext: null,
  newsResult: null,
  technicalResult: null,
  fundamentalResult: null,
  riskResult: null,
  decision: null,
  finalResult: null,
  progress: {
    stage: 'idle',
    agentsCompleted: 0,
    totalAgents: 3,
  },
};

// ============================================================================
// Custom Hook
// ============================================================================

export function useForexAnalysis(
  options: UseForexAnalysisOptions = {}
): UseForexAnalysisReturn {
  const {
    apiUrl = 'http://localhost:8000',
    onStart,
    onComplete,
    onError,
    autoReconnect = false,
    maxReconnectAttempts = 3,
  } = options;

  const [state, setState] = useState<AnalysisState>(initialState);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  // Cancel analysis
  const cancel = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsAnalyzing(false);
    setState(initialState);
  }, []);

  // Handle reconnection
  const handleReconnect = useCallback(
    (query: string) => {
      if (!autoReconnect || reconnectAttemptsRef.current >= maxReconnectAttempts) {
        setError('Connection lost. Please try again.');
        setIsAnalyzing(false);
        return;
      }

      reconnectAttemptsRef.current += 1;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);

      reconnectTimeoutRef.current = setTimeout(() => {
        console.log(`Reconnecting... (attempt ${reconnectAttemptsRef.current})`);
        analyze(query);
      }, delay);
    },
    [autoReconnect, maxReconnectAttempts]
  );

  // Start analysis
  const analyze = useCallback(
    (query: string) => {
      // Close existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Reset state
      setState(initialState);
      setError(null);
      setIsAnalyzing(true);
      reconnectAttemptsRef.current = 0;

      // Call onStart callback
      onStart?.();

      // Create EventSource connection
      const url = `${apiUrl}/analyze/stream?query=${encodeURIComponent(query)}`;
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Event handlers
      eventSource.addEventListener('start', (event) => {
        const data: StartEventData = JSON.parse(event.data);
        setState((prev) => ({
          ...prev,
          query: data.query,
          progress: { ...prev.progress, stage: 'parsing' },
        }));
      });

      eventSource.addEventListener('query_parsed', (event) => {
        const data: QueryParsedEventData = JSON.parse(event.data);
        setState((prev) => ({
          ...prev,
          queryContext: data.query_context,
          progress: { ...prev.progress, stage: 'analyzing' },
        }));
      });

      eventSource.addEventListener('agent_update', (event) => {
        const data: AgentUpdateEventData = JSON.parse(event.data);
        const { agent, result } = data;

        setState((prev) => {
          const agentsCompleted = prev.progress.agentsCompleted + 1;
          const updates: Partial<AnalysisState> = {
            progress: { ...prev.progress, agentsCompleted },
          };

          // Update specific agent result
          if (agent === 'news') updates.newsResult = result;
          else if (agent === 'technical') updates.technicalResult = result;
          else if (agent === 'fundamental') updates.fundamentalResult = result;

          return { ...prev, ...updates };
        });
      });

      eventSource.addEventListener('risk_update', (event) => {
        const data: RiskUpdateEventData = JSON.parse(event.data);
        setState((prev) => ({
          ...prev,
          riskResult: data.risk_result,
          progress: {
            ...prev.progress,
            stage: data.trade_approved ? 'decision' : 'complete',
          },
        }));
      });

      eventSource.addEventListener('decision', (event) => {
        const data: DecisionEventData = JSON.parse(event.data);
        setState((prev) => ({
          ...prev,
          decision: data.decision,
        }));
      });

      eventSource.addEventListener('complete', (event) => {
        const data: CompleteEventData = JSON.parse(event.data);
        setState((prev) => ({
          ...prev,
          finalResult: data.result,
          decision: data.result.decision,
          progress: { ...prev.progress, stage: 'complete' },
        }));
        setIsAnalyzing(false);
        eventSource.close();
        onComplete?.(data.result);
      });

      eventSource.addEventListener('error', (event) => {
        const data: ErrorEventData = JSON.parse(event.data);
        const errorMessage = data.error || 'An error occurred during analysis';
        setError(errorMessage);
        setIsAnalyzing(false);
        eventSource.close();
        onError?.(errorMessage);
      });

      eventSource.onerror = (err) => {
        console.error('EventSource connection error:', err);
        eventSource.close();

        if (isAnalyzing) {
          handleReconnect(query);
        }
      };
    },
    [apiUrl, onStart, onComplete, onError, handleReconnect, isAnalyzing]
  );

  return {
    analyze,
    cancel,
    state,
    isAnalyzing,
    error,
  };
}
