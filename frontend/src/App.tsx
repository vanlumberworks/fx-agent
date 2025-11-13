import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Toaster, toast } from 'sonner'
import { useForexAnalysis } from './hooks/useForexAnalysis'
import { ChatInterface } from './components/ChatInterface'
import { ReasoningTimeline } from './components/ReasoningTimeline'
import { ComprehensiveReport } from './components/ComprehensiveReport'

type ViewMode = 'chat' | 'timeline' | 'report'

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('chat')
  const [currentQuery, setCurrentQuery] = useState('')

  const { analyze, state, isAnalyzing, error } = useForexAnalysis({
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  })

  // Automatically switch views based on analysis state
  useEffect(() => {
    if (isAnalyzing || state.progress.progressMessages.length > 0) {
      setViewMode('timeline')
    } else if (state.finalResult && !isAnalyzing) {
      // Add a small delay before showing the report for dramatic effect
      const timer = setTimeout(() => {
        setViewMode('report')
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [isAnalyzing, state.finalResult, state.progress.progressMessages.length])

  // Show toast notification when report is ready
  useEffect(() => {
    if (state.reportResult?.success && !isAnalyzing) {
      toast.success('Analysis Complete!', {
        description: 'Your comprehensive report is ready to view',
        duration: 5000,
      })
    }
  }, [state.reportResult?.success, isAnalyzing])

  const handleAnalyze = (query: string) => {
    setCurrentQuery(query)
    setViewMode('timeline')
    analyze(query)
  }

  const handleNewAnalysis = () => {
    setViewMode('chat')
    setCurrentQuery('')
  }

  const handleViewReport = () => {
    setViewMode('report')
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'hsl(var(--bg-secondary))',
            color: 'hsl(var(--text-primary))',
            border: '1px solid hsl(var(--gold) / 0.3)',
          },
          className: 'glass',
        }}
      />

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="fixed top-8 right-8 z-50 max-w-md"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
          >
            <div className="glass rounded-xl p-6 border-2 border-[#dc2626] glow-gold">
              <div className="flex items-start gap-3">
                <span className="text-3xl">⚠️</span>
                <div className="flex-1">
                  <h3 className="font-semibold text-[#dc2626] mb-1">
                    Analysis Error
                  </h3>
                  <p className="text-sm text-[hsl(var(--text-secondary))]">
                    {error}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* View Switcher with Transitions */}
      <AnimatePresence mode="wait">
        {viewMode === 'chat' && (
          <motion.div
            key="chat"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.5 }}
          >
            <ChatInterface onSubmit={handleAnalyze} isAnalyzing={isAnalyzing} />
          </motion.div>
        )}

        {viewMode === 'timeline' && (
          <motion.div
            key="timeline"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.6 }}
          >
            <ReasoningTimeline
              state={state}
              isAnalyzing={isAnalyzing}
              query={currentQuery}
              onViewReport={handleViewReport}
            />
          </motion.div>
        )}

        {viewMode === 'report' && (
          <motion.div
            key="report"
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.7 }}
          >
            <ComprehensiveReport
              state={state}
              onNewAnalysis={handleNewAnalysis}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Subtle Vignette Overlay */}
      <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(10,14,39,0.8)_100%)] z-0" />
    </div>
  )
}

export default App
