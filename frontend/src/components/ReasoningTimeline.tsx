import { motion } from 'motion/react'
import { Loader2 } from 'lucide-react'
import { AgentExecutionDetails } from './AgentExecutionDetails'
import type { AnalysisState } from '../hooks/useForexAnalysis'

interface ReasoningTimelineProps {
  state: AnalysisState
  isAnalyzing: boolean
  query: string
  onViewReport?: () => void
}

export function ReasoningTimeline({ state, isAnalyzing, query, onViewReport }: ReasoningTimelineProps) {
  // Simplified process flow steps for left sidebar
  const processFlowSteps = [
    {
      id: 'query',
      title: 'Query Optimization',
      status: state.queryContext ? 'completed' : (state.progress.stage === 'parsing' ? 'active' : 'pending'),
    },
    {
      id: 'parallel',
      title: 'Parallel Agent Execution',
      status: state.progress.agentsCompleted === 3 ? 'completed' : (state.progress.stage === 'analyzing' || state.progress.totalAgents > 0 ? 'active' : 'pending'),
    },
    {
      id: 'synthesis',
      title: 'Data Synthesis',
      status: state.decision ? 'completed' : (state.progress.stage === 'decision' ? 'active' : 'pending'),
    },
    {
      id: 'report',
      title: 'Report Generation',
      status: state.reportResult?.success ? 'completed' : (state.progress.stage === 'report' || state.progress.currentAgent === 'report' ? 'active' : 'pending'),
    },
  ]

  return (
    <div className="min-h-screen relative overflow-hidden bg-black">
      {/* Animated Grid Background */}
      <div className="absolute inset-0 animated-grid opacity-20" />

      <div className="relative z-10 container-custom py-12">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="glass rounded-2xl p-6 border border-[hsl(var(--gold)/0.2)]">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm text-[hsl(var(--text-muted))] mb-1">Analysis Query</h2>
                <p className="text-2xl font-heading text-[hsl(var(--text-primary))]">{query}</p>
              </div>
              <div className="flex items-center gap-3">
                {isAnalyzing && (
                  <div className="flex items-center gap-2 px-4 py-2 rounded-xl glass border border-[hsl(var(--border))]">
                    <div className="w-2 h-2 rounded-full bg-[hsl(var(--gold))] animate-pulse" />
                    <span className="text-sm font-mono text-[hsl(var(--text-secondary))]">
                      Processing {Math.round((processFlowSteps.filter(s => s.status === 'completed').length / processFlowSteps.length) * 100)}%
                    </span>
                  </div>
                )}
                {!isAnalyzing && (
                  <div className="flex items-center gap-2 px-4 py-2 rounded-xl glass border border-[hsl(var(--emerald)/0.3)]">
                    <div className="w-2 h-2 rounded-full bg-[hsl(var(--emerald))]" />
                    <span className="text-sm font-mono text-[hsl(var(--emerald))]">
                      Completed 100%
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Overall Progress Bar */}
            <div className="mt-6 h-2 bg-[hsl(var(--bg-tertiary))] rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-[hsl(var(--gold))]"
                initial={{ width: 0 }}
                animate={{ width: `${(processFlowSteps.filter(s => s.status === 'completed').length / processFlowSteps.length) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </motion.div>

        {/* 2-Column Layout: Process Flow (Left) + Content (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-6">
          {/* LEFT SIDEBAR: Process Flow */}
          <motion.div
            className="glass rounded-xl p-4 border border-[hsl(var(--gold)/0.2)] h-fit"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h3 className="text-xs font-semibold text-[hsl(var(--text-muted))] mb-4 uppercase tracking-wider">
              Process Flow
            </h3>

            <div className="space-y-1 relative">
              {/* Connecting Line */}
              <div className="absolute left-5 top-4 bottom-4 w-px bg-[hsl(var(--bg-tertiary))]" />

              {processFlowSteps.map((step, index) => (
                <motion.div
                  key={step.id}
                  className="relative flex items-center gap-2 py-2"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                >
                  {/* Step Icon */}
                  <div className="relative z-10 flex-shrink-0">
                    {step.status === 'completed' && (
                      <div className="w-10 h-10 rounded-full bg-[hsl(var(--emerald))] flex items-center justify-center shadow-lg shadow-[hsl(var(--emerald)/0.3)]">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    )}
                    {step.status === 'active' && (
                      <div className="w-10 h-10 rounded-full bg-[hsl(var(--gold))] flex items-center justify-center shadow-lg shadow-[hsl(var(--gold)/0.5)]">
                        <Loader2 className="w-5 h-5 text-white animate-spin" />
                      </div>
                    )}
                    {step.status === 'pending' && (
                      <div className="w-10 h-10 rounded-full glass border-2 border-[hsl(var(--border))] flex items-center justify-center">
                        <span className="text-xs font-mono font-semibold text-[hsl(var(--text-muted))]">{index + 1}</span>
                      </div>
                    )}
                  </div>

                  {/* Step Title */}
                  <div className="flex-1">
                    <h4 className={`text-xs font-semibold leading-tight ${
                      step.status === 'completed' ? 'text-[hsl(var(--emerald))]' :
                      step.status === 'active' ? 'text-[hsl(var(--gold))]' :
                      'text-[hsl(var(--text-muted))]'
                    }`}>
                      {step.title}
                    </h4>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* RIGHT CONTENT AREA */}
          <div className="space-y-6">
            {/* Parallel Agent Execution */}
            <AgentExecutionDetails state={state} isAnalyzing={isAnalyzing} />

            {/* Data Synthesis Section */}
            {state.decision && (
              <motion.div
                className="glass rounded-xl p-6 border border-[hsl(var(--gold)/0.2)]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-full bg-[hsl(var(--gold)/0.2)] flex items-center justify-center">
                    <span className="text-2xl">🧠</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-heading text-[hsl(var(--text-primary))]">Data Synthesis</h3>
                    <p className="text-sm text-[hsl(var(--text-secondary))]">Synthesis completed</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-[hsl(var(--emerald))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <p className="text-sm text-[hsl(var(--text-secondary))]">
                      All three analysis dimensions (News, Technical, Fundamental) indicate favorable conditions for gold investment
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-[hsl(var(--emerald))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <p className="text-sm text-[hsl(var(--text-secondary))]">
                      Confluence of bullish technical signals and positive fundamental factors
                    </p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Final Report Section */}
            {(state.progress.stage === 'report' || state.reportResult) && (
              <motion.div
                className="glass rounded-xl p-6 border border-[hsl(var(--gold)/0.2)]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-full bg-[hsl(var(--gold)/0.2)] flex items-center justify-center">
                    {state.progress.stage === 'report' && !state.reportResult?.success ? (
                      <Loader2 className="w-6 h-6 text-[hsl(var(--gold))] animate-spin" />
                    ) : (
                      <span className="text-2xl">📊</span>
                    )}
                  </div>
                  <div>
                    <h3 className="text-xl font-heading text-[hsl(var(--text-primary))]">Final Analysis Report</h3>
                    <p className="text-sm text-[hsl(var(--text-secondary))]">
                      {state.reportResult?.success ? 'Report generated' : 'Generating report...'}
                    </p>
                  </div>
                </div>

                {state.reportResult?.success ? (
                  <>
                    {/* Report Summary Card */}
                    <div className="bg-[#1a1f3a] rounded-xl p-6 border border-gray-700 mb-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h4 className="text-lg font-heading text-white mb-2">
                            Report Generated Successfully
                          </h4>
                          <p className="text-sm text-gray-400">
                            {state.reportResult.metadata.word_count} words • {state.reportResult.metadata.sections.length} sections
                          </p>
                        </div>
                        <div className="text-4xl">📊</div>
                      </div>

                      <div className="flex gap-3">
                        <button
                          onClick={() => {
                            const newWindow = window.open();
                            if (newWindow && state.reportResult) {
                              newWindow.document.write(state.reportResult.html);
                              newWindow.document.close();
                            }
                          }}
                          className="flex-1 py-3 px-6 rounded-xl bg-white hover:bg-gray-100 text-black font-semibold transition-colors flex items-center justify-center gap-2"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          View Report in New Tab
                        </button>
                        <button
                          onClick={() => {
                            const blob = new Blob([state.reportResult!.html], { type: 'text/html' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `trading-report-${Date.now()}.html`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                          }}
                          className="py-3 px-6 rounded-xl bg-[#f59e0b] hover:bg-[#d97706] text-black font-semibold transition-colors flex items-center justify-center gap-2"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                          </svg>
                          Download
                        </button>
                      </div>

                      {/* View Full Report Button */}
                      {onViewReport && state.finalResult && (
                        <button
                          onClick={onViewReport}
                          className="w-full py-3 px-6 rounded-xl bg-gradient-to-r from-[#f59e0b] to-[#fbbf24] hover:from-[#d97706] hover:to-[#f59e0b] text-black font-semibold transition-all duration-300 flex items-center justify-center gap-2 mt-3 shadow-lg hover:shadow-xl"
                        >
                          <span className="text-xl">📊</span>
                          <span>View Full Report & Share</span>
                        </button>
                      )}
                    </div>

                    {state.decision && (
                      <div className="bg-[#1a1f3a] rounded-xl p-6 border border-gray-700 mb-6">
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="text-lg font-heading text-white">
                            Recommendation: <span className={`${
                              state.decision.action === 'BUY' ? 'text-[#10b981]' :
                              state.decision.action === 'SELL' ? 'text-[#dc2626]' :
                              'text-[#f59e0b]'
                            }`}>{state.decision.action}</span>
                          </h4>
                        </div>
                        <p className="text-sm text-gray-300 mb-4">
                          {state.decision.reasoning.summary}
                        </p>

                        <div className="grid grid-cols-3 gap-4 mt-6">
                          <div className="text-center">
                            <div className="text-xs text-gray-400 mb-1">Risk Level</div>
                            <div className="text-lg font-mono font-bold text-[#f59e0b]">Medium</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-400 mb-1">Confidence</div>
                            <div className="text-lg font-mono font-bold text-[#10b981]">
                              {(state.decision.confidence * 100).toFixed(0)}%
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-400 mb-1">Time Horizon</div>
                            <div className="text-lg font-mono font-bold text-[#f59e0b]">Short-term</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="flex items-center justify-center py-12">
                    <div className="flex flex-col items-center gap-4">
                      <Loader2 className="w-12 h-12 text-[hsl(var(--gold))] animate-spin" />
                      <p className="text-sm text-[hsl(var(--text-secondary))] font-mono">Generating comprehensive report...</p>
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

