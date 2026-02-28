import { create } from 'zustand'
import type { SystemStatus } from '@/types'

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
}))
