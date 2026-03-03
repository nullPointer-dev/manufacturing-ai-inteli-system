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
  IndustrialValidationResponse,
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
    mode: OptimizationMode = 'balanced',
    customWeights?: CustomWeights
  ): Promise<OptimizationResponse> => {
    const { data } = await api.post('/optimize_target', {
      ...constraints,
      mode,
      custom_weights: mode === 'custom' ? customWeights : undefined,
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

  rejectGolden: async (
    mode: string,
    clusterId: number,
    proposedMetrics: Record<string, number>,
    reason: string = 'User rejected',
    scenarioKey?: string
  ): Promise<{ status: string; total_rejections: number }> => {
    const { data } = await api.post('/reject_golden', {
      mode,
      cluster_id: clusterId,
      proposed_metrics: proposedMetrics,
      reason,
      scenario_key: scenarioKey,
    })
    return data
  },

  getRejectionHistory: async (): Promise<{
    rejections: Array<{
      time: string
      mode: string
      cluster: number
      scenario_key?: string
      reason: string
      proposed_metrics: Record<string, number>
      type: string
    }>
  }> => {
    const { data } = await api.get('/rejection_history')
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
  
  getDashboardStats: async (): Promise<{
    current: {
      quality: number
      yield: number
      performance: number
      energy: number
      co2: number
      energy_efficiency: number
    }
    trends: {
      quality: number
      yield: number
      performance: number
      energy: number
      co2: number
    }
    baseline: {
      quality: number
      yield: number
      performance: number
      energy: number
      co2: number
    }
    total_batches: number
  }> => {
    const { data } = await api.get('/dashboard/stats')
    return data
  },
  
  getProductionTrends: async (): Promise<{
    trends: Array<{
      batch_id: string
      batch_number: number
      quality: number
      energy: number
      performance: number
      content_uniformity: number
      co2: number
    }>
    total_batches: number
  }> => {
    const { data } = await api.get('/production/trends')
    return data
  },
  
  getDataFiles: async (): Promise<{
    files: Array<{
      name: string
      size: number
      modified: number
    }>
  }> => {
    const { data } = await api.get('/data-files')
    return data
  },
  
  downloadDataFile: async (filename: string): Promise<void> => {
    const response = await fetch(`${API_BASE}/data-files/${filename}`)
    if (!response.ok) {
      let detail = `Download failed (${response.status})`
      try {
        const err = await response.json()
        detail = err.detail || detail
      } catch { /* ignore parse errors */ }
      throw new Error(detail)
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  },
  
  uploadDataFiles: async (productionFile: File, processFile: File): Promise<{
    success: boolean
    message: string
    production_file: string
    process_file: string
    batches_loaded: number
    classified_as: Record<string, string>
  }> => {
    const formData = new FormData()
    formData.append('file1', productionFile)
    formData.append('file2', processFile)
    
    // Use fetch instead of axios for better FormData handling
    const response = await fetch(API_BASE + '/data-files/upload', {
      method: 'POST',
      body: formData,
      // Don't set Content-Type - let browser set it with boundary
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Upload failed')
    }
    
    return await response.json()
  },
}

// Correction API
export const correctionApi = {
  getBatches: async (): Promise<{
    status: string
    batches: Array<{
      Batch_ID: string
      Quality_Score: number
      Yield_Percentage: number
      Performance_Index: number
    }>
    total: number
  }> => {
    const { data } = await api.get('/batches')
    return data
  },

  analyzeBatch: async (batchId: string): Promise<{
    status: string
    batch_id: string
    batch_info: {
      quality: number
      yield: number
      performance: number
      energy: number
      co2: number
    }
    analysis: Array<{
      Parameter: string
      Current: number
      'Golden Mean': number
      'Drift (σ)': number
      Severity: string
      Suggestion: string
      'Predicted Impact': number
    }>
    summary: {
      total_parameters: number
      critical: number
      moderate: number
      ok: number
    }
  }> => {
    const { data } = await api.get(`/batch/${batchId}/analyze`)
    return data
  },
}

// Anomaly Detection API
export const anomalyApi = {
  getAnomalies: async (): Promise<{
    total_batches: number
    anomalous_count: number
    contamination_rate: number
    anomalous_batches: Array<{
      batch_id: string
      anomaly_score: number
      risk_level: string
      quality: number
      yield: number
      performance: number
      energy: number
      co2: number
    }>
    all_batches: Array<{
      batch_id: string
      anomaly_score: number
      is_anomaly: number
      risk_level: string
      quality: number
      energy: number
      content_uniformity: number
      hardness: number
    }>
    risk_distribution: {
      high: number
      medium: number
      low: number
    }
  }> => {
    const { data } = await api.get('/anomalies')
    return data
  },

  getAssetReliability: async (): Promise<{
    batches: Array<{
      batch_id: string
      reliability_state: string
      asset_cause: string
      maintenance_action: string
      energy_drift: number
      instability_score: number
    }>
    summary: {
      stable: number
      efficiency_loss: number
      process_instability: number
      calibration_gain: number
    }
  }> => {
    const { data } = await api.get('/asset_reliability')
    return data
  },
}

// Industrial Validation API
export const industrialValidationApi = {
  calculate: async (params: {
    electricity_cost: number
    batches_per_day: number
    deployment_cost: number
    annual_maintenance_cost: number
    operating_days_per_year?: number
    current_batch_params?: Record<string, any>
  }): Promise<IndustrialValidationResponse> => {
    const { data } = await api.post('/industrial_validation', params)
    return data
  },
}

export default api
