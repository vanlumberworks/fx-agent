/**
 * Complete React Component Example
 *
 * This is a full-featured React component that demonstrates how to use
 * the useForexAnalysis hook to build an interactive forex analysis UI.
 *
 * Features:
 * - Real-time progress updates
 * - Agent completion indicators
 * - Decision display with confidence
 * - Trade parameters
 * - Error handling
 * - Loading states
 *
 * Usage:
 * ```tsx
 * import ForexAnalysisComponent from './ForexAnalysisComponent';
 *
 * function App() {
 *   return <ForexAnalysisComponent />;
 * }
 * ```
 */

import React, { useState } from 'react';
import { useForexAnalysis } from './useForexAnalysis';
import type { Decision, ActionType } from './types';

// ============================================================================
// Helper Components
// ============================================================================

const ProgressIndicator: React.FC<{ stage: string; agentsCompleted: number; totalAgents: number }> = ({
  stage,
  agentsCompleted,
  totalAgents,
}) => {
  const stages = ['idle', 'parsing', 'analyzing', 'risk', 'decision', 'complete'];
  const currentIndex = stages.indexOf(stage);
  const progress = ((currentIndex + 1) / stages.length) * 100;

  return (
    <div className="progress-container">
      <div className="progress-bar" style={{ width: `${progress}%` }} />
      <div className="progress-text">
        <span>{stage.charAt(0).toUpperCase() + stage.slice(1)}</span>
        {stage === 'analyzing' && (
          <span> ({agentsCompleted}/{totalAgents} agents)</span>
        )}
      </div>
    </div>
  );
};

const AgentStatus: React.FC<{
  name: string;
  result: any;
  icon: string;
}> = ({ name, result, icon }) => {
  const getStatus = () => {
    if (!result) return 'pending';
    return result.success ? 'complete' : 'error';
  };

  const status = getStatus();

  return (
    <div className={`agent-status agent-status-${status}`}>
      <span className="agent-icon">{icon}</span>
      <span className="agent-name">{name}</span>
      <span className="agent-indicator">
        {status === 'pending' && '⏳'}
        {status === 'complete' && '✓'}
        {status === 'error' && '✗'}
      </span>
    </div>
  );
};

const DecisionCard: React.FC<{ decision: Decision }> = ({ decision }) => {
  const { action, confidence, reasoning, trade_parameters, grounding_metadata } = decision;

  const getActionColor = (action: ActionType) => {
    switch (action) {
      case 'BUY':
        return '#10b981'; // green
      case 'SELL':
        return '#ef4444'; // red
      case 'WAIT':
        return '#f59e0b'; // yellow
      default:
        return '#6b7280'; // gray
    }
  };

  const getActionEmoji = (action: ActionType) => {
    switch (action) {
      case 'BUY':
        return '🟢';
      case 'SELL':
        return '🔴';
      case 'WAIT':
        return '🟡';
      default:
        return '❓';
    }
  };

  return (
    <div className="decision-card">
      <div className="decision-header" style={{ borderLeftColor: getActionColor(action) }}>
        <span className="decision-emoji">{getActionEmoji(action)}</span>
        <div>
          <h3 className="decision-action">{action}</h3>
          <p className="decision-confidence">
            Confidence: {(confidence * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      {reasoning?.summary && (
        <div className="decision-section">
          <h4>Summary</h4>
          <p>{reasoning.summary}</p>
        </div>
      )}

      {reasoning?.key_factors && reasoning.key_factors.length > 0 && (
        <div className="decision-section">
          <h4>Key Factors</h4>
          <ul>
            {reasoning.key_factors.map((factor, idx) => (
              <li key={idx}>{factor}</li>
            ))}
          </ul>
        </div>
      )}

      {trade_parameters && action !== 'WAIT' && (
        <div className="decision-section">
          <h4>Trade Parameters</h4>
          <div className="trade-params">
            <div className="param">
              <span className="param-label">Entry:</span>
              <span className="param-value">{trade_parameters.entry_price}</span>
            </div>
            <div className="param">
              <span className="param-label">Stop Loss:</span>
              <span className="param-value">{trade_parameters.stop_loss}</span>
            </div>
            <div className="param">
              <span className="param-label">Take Profit:</span>
              <span className="param-value">{trade_parameters.take_profit}</span>
            </div>
            <div className="param">
              <span className="param-label">Position Size:</span>
              <span className="param-value">{trade_parameters.position_size} lots</span>
            </div>
          </div>
        </div>
      )}

      {grounding_metadata?.sources && grounding_metadata.sources.length > 0 && (
        <div className="decision-section">
          <h4>🌐 Sources ({grounding_metadata.sources.length})</h4>
          <div className="sources">
            {grounding_metadata.sources.slice(0, 3).map((source, idx) => (
              <a
                key={idx}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="source-link"
              >
                {idx + 1}. {source.title}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Main Component
// ============================================================================

const ForexAnalysisComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const { analyze, cancel, state, isAnalyzing, error } = useForexAnalysis({
    apiUrl: 'http://localhost:8000',
    onComplete: (result) => {
      console.log('Analysis complete:', result);
    },
    onError: (error) => {
      console.error('Analysis error:', error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isAnalyzing) {
      analyze(query);
    }
  };

  const handleCancel = () => {
    cancel();
    setQuery('');
  };

  return (
    <div className="forex-analysis-container">
      <header className="header">
        <h1>🌍 Forex Agent System</h1>
        <p>Real-time Multi-Agent Trading Analysis</p>
      </header>

      <form onSubmit={handleSubmit} className="query-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter query (e.g., 'Analyze gold trading', 'EUR/USD')"
          className="query-input"
          disabled={isAnalyzing}
        />
        <div className="button-group">
          <button
            type="submit"
            disabled={isAnalyzing || !query.trim()}
            className="btn btn-primary"
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze'}
          </button>
          {isAnalyzing && (
            <button type="button" onClick={handleCancel} className="btn btn-secondary">
              Cancel
            </button>
          )}
        </div>
      </form>

      {error && (
        <div className="error-message">
          <span className="error-icon">❌</span>
          <span>{error}</span>
        </div>
      )}

      {isAnalyzing && (
        <div className="analysis-progress">
          <ProgressIndicator
            stage={state.progress.stage}
            agentsCompleted={state.progress.agentsCompleted}
            totalAgents={state.progress.totalAgents}
          />

          {state.queryContext && (
            <div className="query-context">
              <h3>📋 Analyzing: {state.queryContext.pair}</h3>
              <p>
                Asset: {state.queryContext.asset_type} | Timeframe:{' '}
                {state.queryContext.timeframe}
              </p>
            </div>
          )}

          <div className="agents-status">
            <AgentStatus name="News Agent" result={state.newsResult} icon="📰" />
            <AgentStatus name="Technical Agent" result={state.technicalResult} icon="📊" />
            <AgentStatus name="Fundamental Agent" result={state.fundamentalResult} icon="💼" />
          </div>

          {state.riskResult && (
            <div className="risk-status">
              <h3>⚖️ Risk Assessment</h3>
              <p>
                Status:{' '}
                {state.riskResult.data?.trade_approved ? (
                  <span className="status-approved">APPROVED ✓</span>
                ) : (
                  <span className="status-rejected">REJECTED ✗</span>
                )}
              </p>
              {!state.riskResult.data?.trade_approved && (
                <p className="rejection-reason">
                  {state.riskResult.data?.rejection_reason}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {state.decision && <DecisionCard decision={state.decision} />}

      <style jsx>{`
        .forex-analysis-container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .header {
          text-align: center;
          margin-bottom: 30px;
        }

        .header h1 {
          margin: 0;
          font-size: 2rem;
        }

        .header p {
          margin: 5px 0 0;
          color: #6b7280;
        }

        .query-form {
          margin-bottom: 20px;
        }

        .query-input {
          width: 100%;
          padding: 12px;
          font-size: 16px;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          margin-bottom: 10px;
        }

        .query-input:focus {
          outline: none;
          border-color: #3b82f6;
        }

        .button-group {
          display: flex;
          gap: 10px;
        }

        .btn {
          padding: 10px 20px;
          font-size: 16px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #3b82f6;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #2563eb;
        }

        .btn-primary:disabled {
          background: #9ca3af;
          cursor: not-allowed;
        }

        .btn-secondary {
          background: #ef4444;
          color: white;
        }

        .btn-secondary:hover {
          background: #dc2626;
        }

        .error-message {
          padding: 15px;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 8px;
          color: #dc2626;
          margin-bottom: 20px;
        }

        .progress-container {
          margin-bottom: 20px;
        }

        .progress-bar {
          height: 4px;
          background: #3b82f6;
          border-radius: 2px;
          transition: width 0.3s;
        }

        .progress-text {
          margin-top: 5px;
          font-size: 14px;
          color: #6b7280;
        }

        .agents-status {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
          margin: 20px 0;
        }

        .agent-status {
          padding: 15px;
          border-radius: 8px;
          background: #f9fafb;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .agent-status-complete {
          background: #f0fdf4;
          border: 1px solid #bbf7d0;
        }

        .agent-status-error {
          background: #fef2f2;
          border: 1px solid #fecaca;
        }

        .decision-card {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 20px;
          margin-top: 20px;
        }

        .decision-header {
          display: flex;
          align-items: center;
          gap: 15px;
          padding-left: 15px;
          border-left: 4px solid;
          margin-bottom: 20px;
        }

        .decision-emoji {
          font-size: 2rem;
        }

        .decision-action {
          margin: 0;
          font-size: 1.5rem;
        }

        .decision-confidence {
          margin: 5px 0 0;
          color: #6b7280;
        }

        .decision-section {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #e5e7eb;
        }

        .decision-section h4 {
          margin: 0 0 10px;
        }

        .trade-params {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
        }

        .param {
          display: flex;
          justify-content: space-between;
          padding: 8px;
          background: #f9fafb;
          border-radius: 4px;
        }

        .sources {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .source-link {
          color: #3b82f6;
          text-decoration: none;
        }

        .source-link:hover {
          text-decoration: underline;
        }

        .status-approved {
          color: #10b981;
        }

        .status-rejected {
          color: #ef4444;
        }
      `}</style>
    </div>
  );
};

export default ForexAnalysisComponent;
