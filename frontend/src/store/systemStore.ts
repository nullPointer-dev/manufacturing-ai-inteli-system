import { create } from 'zustand'
import type { SystemStatus } from '@/types'

interface SystemState {
  status: SystemStatus | null
  isOnline: boolean
  lastUpdate: number | null
  
  setStatus: (status: SystemStatus) => void
  setOnline: (isOnline: boolean) => void
  updateTimestamp: () => void
}

export const useSystemStore = create<SystemState>((set) => ({
  status: null,
  isOnline: true,
  lastUpdate: null,

  setStatus: (status) =>
    set({ status, lastUpdate: Date.now() }),

  setOnline: (isOnline) => set({ isOnline }),

  updateTimestamp: () => set({ lastUpdate: Date.now() }),
}))
