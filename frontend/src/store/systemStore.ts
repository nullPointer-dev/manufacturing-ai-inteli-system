import { create } from 'zustand'
import type { SystemStatus } from '@/types'

const HEALTH_POLL_INTERVAL_MS = 30_000  // 30 seconds

interface SystemState {
  status: SystemStatus | null
  isOnline: boolean
  lastUpdate: number | null
  isProcessing: boolean
  processingMessage: string
  
  setStatus: (status: SystemStatus) => void
  setOnline: (isOnline: boolean) => void
  updateTimestamp: () => void
  setProcessing: (isProcessing: boolean, message?: string) => void
  startHealthPolling: () => () => void  // returns a cleanup function
}

export const useSystemStore = create<SystemState>((set) => ({
  status: null,
  isOnline: true,
  lastUpdate: null,
  isProcessing: false,
  processingMessage: 'Processing...',

  setStatus: (status) =>
    set({ status, lastUpdate: Date.now() }),

  setOnline: (isOnline) => set({ isOnline }),

  updateTimestamp: () => set({ lastUpdate: Date.now() }),

  setProcessing: (isProcessing, message = 'Processing...') =>
    set({ isProcessing, processingMessage: message }),

  /**
   * Starts a background interval that polls /api/health every 30 s.
   * Returns a cleanup function to stop polling (call on component unmount).
   */
  startHealthPolling: () => {
    const poll = async () => {
      try {
        const res = await fetch('/api/health', { method: 'GET' })
        set({ isOnline: res.ok, lastUpdate: Date.now() })
      } catch {
        set({ isOnline: false })
      }
    }

    // Run immediately then on interval
    poll()
    const id = window.setInterval(poll, HEALTH_POLL_INTERVAL_MS)
    return () => window.clearInterval(id)
  },
}))
