import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, CheckCircle2, AlertCircle, ChevronDown, Search } from 'lucide-react';
import { ShiningText } from './ui/shining-text';
import type { AnalysisState } from '../hooks/useForexAnalysis';

interface AgentExecutionDetailsProps {
  state: AnalysisState;
  isAnalyzing: boolean;
}

export function AgentExecutionDetails({ state, isAnalyzing }: AgentExecutionDetailsProps) {
  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({});

  const toggleCard = (agentId: string) => {
    setExpandedCards(prev => ({
      ...prev,
      [agentId]: !prev[agentId]
    }));
  };

  const agents = [
    {
      id: 'news',
      title: 'News Agent',
      icon: '📰',
      agentState: state.agents.news,
    },
    {
      id: 'technical',
      title: 'Technical Agent',
      icon: '📊',
      agentState: state.agents.technical,
    },
    {
      id: 'fundamental',
      title: 'Fundamental Agent',
      icon: '💼',
      agentState: state.agents.fundamental,
    }
  ];

  // Don't show if no agents are running or completed
  if (!isAnalyzing && !agents.some(a => a.agentState.status !== 'pending')) {
    return null;
  }

  // Format execution time
  const formatExecutionTime = (timeInSeconds: number | null) => {
    if (!timeInSeconds) return 'N/A';
    return `${timeInSeconds.toFixed(2)}s`;
  };

  return (
    <motion.div
      className="mt-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-heading text-[hsl(var(--text-primary))]">
          Parallel Agent Execution
        </h2>
        <div className="px-3 py-1.5 rounded-lg bg-[hsl(var(--gold)/0.1)] border border-[hsl(var(--gold)/0.3)]">
          <span className="text-sm font-mono font-semibold text-[hsl(var(--gold))]">
            {agents.filter(a => a.agentState.status === 'completed').length} / {agents.length} agents completed
          </span>
        </div>
      </div>

      {/* 3 Agent Cards in Horizontal Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {agents.map((agent, index) => {
          const agentData = agent.agentState;
          const isActive = agentData.status === 'running';
          const isCompleted = agentData.status === 'completed';
          const isFailed = agentData.status === 'failed';

          return (
            <motion.div
              key={agent.id}
              className="glass rounded-xl p-5 border border-[hsl(var(--gold)/0.3)]"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              {/* Agent Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{agent.icon}</span>
                  <div>
                    <h3 className="text-lg font-heading text-[hsl(var(--text-primary))]">
                      {agent.title}
                    </h3>
                    {isActive && (
                      <span className="inline-block mt-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-[hsl(var(--gold)/0.2)] text-[hsl(var(--gold))] border border-[hsl(var(--gold)/0.4)]">
                        Processing
                      </span>
                    )}
                    {isCompleted && (
                      <span className="inline-block mt-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-[hsl(var(--emerald)/0.2)] text-[hsl(var(--emerald))] border border-[hsl(var(--emerald)/0.4)]">
                        Completed
                      </span>
                    )}
                    {isFailed && (
                      <span className="inline-block mt-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-[hsl(var(--ruby)/0.2)] text-[hsl(var(--ruby))] border border-[hsl(var(--ruby)/0.4)]">
                        Failed
                      </span>
                    )}
                  </div>
                </div>

                {/* Status Icon */}
                {isActive && (
                  <motion.div
                    className="w-6 h-6 rounded-full border-2 border-[hsl(var(--gold))] border-t-transparent"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  />
                )}
                {isCompleted && (
                  <CheckCircle2 className="w-6 h-6 text-[hsl(var(--emerald))]" />
                )}
                {isFailed && (
                  <AlertCircle className="w-6 h-6 text-[hsl(var(--ruby))]" />
                )}
              </div>

              {/* Current Step (when running) */}
              {isActive && (
                <div className="mb-3 px-3 py-2 rounded-lg bg-[hsl(var(--gold)/0.1)] border border-[hsl(var(--gold)/0.2)]">
                  <div className="text-xs text-[hsl(var(--text-muted))] mb-1">Current Step:</div>
                  {agentData.currentStep ? (
                    <div className="text-sm text-[hsl(var(--text-primary))]">{agentData.currentStep}</div>
                  ) : (
                    <ShiningText text="Analyzing..." className="text-sm" />
                  )}
                </div>
              )}

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-[hsl(var(--text-secondary))]">Progress</span>
                  <span className="text-sm font-mono font-bold text-[hsl(var(--gold))]">
                    {agentData.progress}%
                  </span>
                </div>
                <div className="w-full h-2 bg-[hsl(var(--bg-tertiary))] rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full ${isFailed ? 'bg-[hsl(var(--ruby))]' : 'bg-[hsl(var(--gold))]'}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${agentData.progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              {/* Execution Time */}
              {agentData.executionTime !== null && (
                <div className="flex items-center gap-2 mb-4 text-sm text-[hsl(var(--text-secondary))]">
                  <Clock className="w-4 h-4" />
                  <span>Execution time: {formatExecutionTime(agentData.executionTime)}</span>
                </div>
              )}

              {/* Intermediate Data */}
              {agentData.intermediateData && Object.keys(agentData.intermediateData).length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs text-gray-400 mb-2 font-semibold">
                    Intermediate Data:
                  </h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {Object.entries(agentData.intermediateData).map(([key, value]) => (
                      <div key={key} className="p-3 rounded-lg bg-[#1a1f3a] border border-gray-700">
                        <div className="text-xs text-gray-400 mb-1.5 font-semibold">{key}:</div>
                        <div className="text-sm text-white">
                          {typeof value === 'object' && value !== null ? (
                            Array.isArray(value) ? (
                              <ul className="space-y-1 ml-2">
                                {value.map((item: any, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-gray-300 mt-1">•</span>
                                    <span className="flex-1 break-words">{typeof item === 'object' ? JSON.stringify(item) : String(item)}</span>
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <div className="space-y-1">
                                {Object.entries(value).map(([k, v]) => (
                                  <div key={k} className="flex gap-2">
                                    <span className="text-gray-300">{k}:</span>
                                    <span className="flex-1 break-words font-mono">{String(v)}</span>
                                  </div>
                                ))}
                              </div>
                            )
                          ) : (
                            <span className="break-words font-mono">{String(value)}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Web Search Toggle Button */}
              {(agentData.webSearchQueries.length > 0 || agentData.webSearchSources.length > 0) && (
                <>
                  <button
                    onClick={() => toggleCard(agent.id)}
                    className="w-full mt-2 px-3 py-2 rounded-lg bg-[#1a1f3a] hover:bg-[#242943] transition-colors text-sm text-gray-300 flex items-center justify-between border border-gray-700"
                  >
                    <div className="flex items-center gap-2">
                      <Search className="w-4 h-4" />
                      <span>Web Search ({agentData.webSearchQueries.length + agentData.webSearchSources.length} items)</span>
                    </div>
                    <motion.div
                      animate={{ rotate: expandedCards[agent.id] ? 180 : 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <ChevronDown className="w-4 h-4" />
                    </motion.div>
                  </button>

                  {/* Web Search Results (Collapsible) */}
                  <AnimatePresence>
                    {expandedCards[agent.id] && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-3 p-4 rounded-lg bg-[#0f1420] border border-gray-700">
                          {/* Search Queries */}
                          {agentData.webSearchQueries.length > 0 && (
                            <div className="mb-4">
                              <h5 className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-2">
                                <Search className="w-3 h-3" />
                                Search Queries:
                              </h5>
                              <div className="space-y-2">
                                {agentData.webSearchQueries.map((query: string, idx: number) => (
                                  <div
                                    key={idx}
                                    className="px-3 py-1.5 rounded-md bg-[#1a1f3a] border border-gray-700 text-xs font-mono text-gray-300"
                                  >
                                    "{query}"
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Search Sources */}
                          {agentData.webSearchSources.length > 0 && (
                            <div>
                              <h5 className="text-xs font-semibold text-gray-400 mb-2">
                                Sources ({agentData.webSearchSources.length}):
                              </h5>
                              <div className="space-y-2 max-h-48 overflow-y-auto">
                                {agentData.webSearchSources.map((source: { title: string; url: string }, idx: number) => (
                                  <a
                                    key={idx}
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block px-3 py-2 rounded-md bg-[#1a1f3a] border border-gray-700 hover:border-gray-500 hover:bg-[#242943] transition-colors group"
                                  >
                                    <div className="text-xs font-semibold text-white group-hover:text-gray-200 transition-colors mb-1">
                                      {source.title}
                                    </div>
                                    <div className="text-xs text-gray-400 truncate">
                                      {source.url}
                                    </div>
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Messages (if any) */}
                          {agentData.messages.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-gray-700">
                              <h5 className="text-xs font-semibold text-gray-400 mb-2">
                                Activity Log ({agentData.messages.length}):
                              </h5>
                              <div className="space-y-1 max-h-32 overflow-y-auto">
                                {agentData.messages.slice(-5).map((msg: string, idx: number) => (
                                  <div
                                    key={idx}
                                    className="text-xs text-gray-300 font-mono flex items-start gap-2"
                                  >
                                    <span className="text-gray-400 mt-0.5">›</span>
                                    <span className="flex-1">{msg}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </>
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
