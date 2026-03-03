// Core prediction types
export interface PredictionInput {
  [key: string]: number | string
}

export interface PredictionOutput {
  Hardness: number
  Dissolution_Rate: number
  Content_Uniformity: number
  Quality: number
  Yield: number
  Performance: number
  Energy: number
  CO2: number
}

// Optimization types
export type OptimizationMode = 'balanced' | 'eco' | 'quality' | 'yield' | 'performance' | 'custom'

export interface CustomWeights {
  quality: number
  yield: number
  performance: number
  energy: number
  co2: number
}

export interface OptimizationConstraints {
  required_reduction?: number
  min_quality?: number
  min_yield?: number
  min_performance?: number
}

export interface OptimizationResult {
  Score: number
  Quality: number
  Yield: number
  Performance: number
  Energy: number
  CO2: number
  [key: string]: number
}

export interface OptimizationResponse {
  status: string
  top_result?: OptimizationResult
  best_solution?: OptimizationResult
  all_results?: OptimizationResult[]
  pareto_front?: OptimizationResult[]
  proposal: boolean
  cluster_id: number
  scenario_key?: string
}

// Golden signature types
export interface GoldenMetrics {
  score: number
  quality: number
  yield: number
  performance: number
  energy: number
  co2: number
}

export interface GoldenCluster {
  [clusterKey: string]: GoldenMetrics
}

export interface GoldenRegistry {
  [mode: string]: GoldenCluster | {
    [scenarioKey: string]: GoldenCluster
  }
}

export interface GoldenHistoryEntry {
  time: string
  mode: string
  scenario_key?: string
  cluster: number
  type: string
  metrics: GoldenMetrics
}

// Model governance types
export interface ModelMetrics {
  mae: number
  rmse: number
  r2: number
  mape?: number | null
}

export interface ModelVersionEntry {
  time: string
  reason: Record<string, boolean>
  metrics: ModelMetrics
  dataset_size: number
  model_version: number
}

export interface DriftFlags {
  high_anomaly_rate: boolean
  high_energy_drift: boolean
  cooldown_active?: boolean
}

// Feature importance
export interface FeatureImportance {
  feature: string
  importance: number
}

// Batch correction types
export interface CorrectionReport {
  Parameter: string
  Current: number
  'Golden Mean': number
  'Drift (σ)': number
  Severity: 'OK' | 'Moderate' | 'Critical'
  Suggestion: string
  'Predicted Impact': number
}

// System status
export interface SystemStatus {
  model_exists: boolean
  golden_registry_exists: boolean
  version_log_exists: boolean
}

// Anomaly types
export interface AnomalyData {
  Batch_ID: string
  anomaly_score: number
  anomaly_flag: number
  risk_level: 'Low' | 'Medium' | 'High'
  quality_score: number
  total_energy: number
  reliability_state: string
  energy_drift: number
  instability_score: number
}

// Industrial Validation types
export interface IndustrialValidationResponse {
  inputs: {
    electricity_cost: number
    batches_per_day: number
    deployment_cost: number
    annual_maintenance_cost: number
    operating_days_per_year: number
    annual_batches: number
  }
  baseline: {
    quality: number
    yield: number
    performance: number
    energy_per_batch: number
    co2_per_batch: number
  }
  optimized: {
    quality: number
    yield: number
    performance: number
    energy_per_batch: number
    co2_per_batch: number
  }
  improvements: {
    quality_improvement_pct: number
    yield_improvement_pct: number
    performance_improvement_pct: number
    energy_saved_per_batch: number
    co2_saved_per_batch: number
  }
  annual_savings: {
    energy_saved_kwh: number
    co2_saved_kg: number
    energy_cost_savings: number
    raw_material_savings: number
    quality_savings: number
    performance_savings: number
    total_savings: number
    net_benefit: number
  }
  financial: {
    roi_3_year_pct: number
    payback_period_years: number
    payback_period_months: number
  }
  environmental: {
    energy_efficiency_improvement_pct: number
    co2_reduction_pct: number
    trees_equivalent: number
  }
  status: string
}
