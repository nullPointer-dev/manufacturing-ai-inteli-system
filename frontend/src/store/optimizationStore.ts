import { create } from 'zustand'
import type { OptimizationMode, CustomWeights, OptimizationResult } from '@/types'

interface OptimizationState {
  mode: OptimizationMode
  customWeights: CustomWeights
  results: OptimizationResult[]
  allResults: OptimizationResult[]
  paretoFront: OptimizationResult[]
  selectedResult: OptimizationResult | null
  proposal: boolean
  clusterId: number | null
  scenarioKey: string | null
  isLoading: boolean
  error: string | null
  
  setMode: (mode: OptimizationMode) => void
  setCustomWeights: (weights: Partial<CustomWeights>) => void
  setResults: (results: OptimizationResult[]) => void
  setAllResults: (results: OptimizationResult[]) => void
  setParetoFront: (results: OptimizationResult[]) => void
  setSelectedResult: (result: OptimizationResult | null) => void
  setProposal: (proposal: boolean, clusterId: number, scenarioKey?: string) => void
  clearProposal: () => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const defaultWeights: CustomWeights = {
  quality: 0.3,
  yield: 0.3,
  performance: 0.2,
  energy: 0.1,
  co2: 0.1,
}

export const useOptimizationStore = create<OptimizationState>((set) => ({
  mode: 'balanced',
  customWeights: defaultWeights,
  results: [],
  allResults: [],
  paretoFront: [],
  selectedResult: null,
  proposal: false,
  clusterId: null,
  scenarioKey: null,
  isLoading: false,
  error: null,

  setMode: (mode) => set({ mode }),

  setCustomWeights: (weights) =>
    set((state) => ({
      customWeights: { ...state.customWeights, ...weights },
    })),

  setResults: (results) =>
    set({
      results,
      selectedResult: results.length > 0 ? results[0] : null,
    }),

  setAllResults: (allResults) => set({ allResults }),

  setParetoFront: (paretoFront) => set({ paretoFront }),

  setSelectedResult: (result) => set({ selectedResult: result }),

  setProposal: (proposal, clusterId, scenarioKey) =>
    set({ proposal, clusterId, scenarioKey }),

  clearProposal: () =>
    set({ proposal: false, clusterId: null, scenarioKey: null }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  reset: () =>
    set({
      mode: 'balanced',
      customWeights: defaultWeights,
      results: [],
      allResults: [],
      paretoFront: [],
      selectedResult: null,
      proposal: false,
      clusterId: null,
      scenarioKey: null,
      isLoading: false,
      error: null,
    }),

}))
