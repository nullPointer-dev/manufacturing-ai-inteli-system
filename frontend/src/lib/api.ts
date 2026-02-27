import axios from 'axios'
import type {
  PredictionInput,
  PredictionOutput,
  OptimizationMode,
  CustomWeights,
  OptimizationConstraints,
  OptimizationResponse,
  GoldenRegistry,
  GoldenHistoryEntry,
  ModelVersionEntry,
  FeatureImportance,
  SystemStatus,
} from '@/types'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 seconds for optimization operations
})

// Prediction API
export const predictionApi = {
  predict: async (payload: PredictionInput): Promise<{ prediction: PredictionOutput }> => {
    const { data } = await api.post('/predict', { data: payload })
    return data
  },
}

// Optimization API
export const optimizationApi = {
  optimizeAuto: async (mode: OptimizationMode, customWeights?: CustomWeights): Promise<OptimizationResponse> => {
    const { data } = await api.post('/optimize_auto', {
      mode,
      custom_weights: customWeights,
    })
    return data
  },

  optimizeTarget: async (
    constraints: OptimizationConstraints,
    mode: OptimizationMode = 'balanced'
  ): Promise<OptimizationResponse> => {
    const { data } = await api.post('/optimize_target', {
      ...constraints,
      mode,
    })
    return data
  },
}

// Golden Signature API
export const goldenApi = {
  getRegistry: async (): Promise<GoldenRegistry> => {
    const { data } = await api.get('/golden')
    return data
  },

  acceptGolden: async (
    bestRow: Record<string, number>,
    mode: string,
    clusterId: number,
    scenarioKey?: string
  ): Promise<{ golden_updated: boolean }> => {
    const { data } = await api.post('/accept_golden', {
      best_row: bestRow,
      mode,
      cluster_id: clusterId,
      scenario_key: scenarioKey,
    })
    return data
  },

  getHistory: async (): Promise<GoldenHistoryEntry[]> => {
    const { data } = await api.get('/golden_history')
    return data
  },

  getArchive: async (): Promise<any> => {
    const { data } = await api.get('/golden_archive')
    return data
  },

  clearSession: async (): Promise<{ status: string; archived_count: number }> => {
    const { data } = await api.post('/clear_session')
    return data
  },
}

// Model Governance API
export const governanceApi = {
  getModelHistory: async (): Promise<ModelVersionEntry[]> => {
    const { data } = await api.get('/model_history')
    return data
  },

  checkRetrain: async (): Promise<{ retrained: boolean; flags: Record<string, boolean> }> => {
    const { data } = await api.post('/check_retrain')
    return data
  },

  getFeatureImportance: async (): Promise<FeatureImportance[]> => {
    const { data } = await api.get('/feature_importance')
    return data
  },
}

// System API
export const systemApi = {
  getStatus: async (): Promise<SystemStatus> => {
    const { data } = await api.get('/system_status')
    return data
  },
}

export default api
