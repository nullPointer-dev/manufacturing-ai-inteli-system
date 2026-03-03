import { ReactNode, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, WifiOff } from 'lucide-react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { useSystemStore } from '@/store/systemStore'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { isProcessing, processingMessage, isOnline, startHealthPolling } = useSystemStore()

  // Start background health polling when the app first mounts; clean up on unmount.
  useEffect(() => {
    const stop = startHealthPolling()
    return stop
  }, [startHealthPolling])

  return (
    <>
      {/* Global Loading Overlay */}
      <AnimatePresence>
        {isProcessing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="flex flex-col items-center gap-6 p-12 rounded-xl bg-card/90 border border-teal-500/30 shadow-2xl"
            >
              <div className="relative">
                <Loader2 className="h-16 w-16 text-teal-500 animate-spin" />
                <div className="absolute inset-0 h-16 w-16 bg-teal-500/20 rounded-full animate-pulse" />
              </div>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold text-teal-500">Processing Data</h2>
                <p className="text-muted-foreground">{processingMessage}</p>
              </div>
              <div className="flex gap-1">
                <motion.div
                  className="w-2 h-2 bg-teal-500 rounded-full"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="w-2 h-2 bg-teal-500 rounded-full"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                  className="w-2 h-2 bg-teal-500 rounded-full"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex h-screen bg-background control-room-grid">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header />
          {/* Offline Banner */}
          <AnimatePresence>
            {!isOnline && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="flex items-center justify-center gap-2 bg-red-500/15 border-b border-red-500/30 px-4 py-2 text-sm text-red-400 font-medium"
              >
                <WifiOff className="h-4 w-4" />
                Backend unreachable — retrying in 30 s
              </motion.div>
            )}
          </AnimatePresence>
          <main className="flex-1 overflow-y-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </>
  )
}
