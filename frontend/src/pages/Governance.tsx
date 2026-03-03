import { useQuery, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Shield, RefreshCw, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { governanceApi } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import { format } from 'date-fns'
import { useState } from 'react'

export function Governance() {
  const queryClient = useQueryClient()
  const [retrainLoading, setRetrainLoading] = useState(false)
  const [retrainResult, setRetrainResult] = useState<{ retrained: boolean; flags: Record<string, boolean> } | null>(null)

  const { data: modelHistory = [], isError: historyError } = useQuery({
    queryKey: ['model-history'],
    queryFn: governanceApi.getModelHistory,
  })

  const { data: featureImportance = [], isLoading: shapLoading, isError: shapError } = useQuery({
    queryKey: ['feature-importance'],
    queryFn: governanceApi.getFeatureImportance,
  })

  const latestVersion = modelHistory[modelHistory.length - 1]

  const handleCheckRetrain = async () => {
    setRetrainLoading(true)
    setRetrainResult(null)
    try {
      const result = await governanceApi.checkRetrain()
      setRetrainResult(result)
      if (result.retrained) {
        // Refresh model history and feature importance after retraining
        queryClient.invalidateQueries({ queryKey: ['model-history'] })
        queryClient.invalidateQueries({ queryKey: ['feature-importance'] })
      }
    } catch (err) {
      console.error('Retrain check failed:', err)
    } finally {
      setRetrainLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold mb-2">Model Governance & Drift Monitor</h1>
        <p className="text-muted-foreground">
          Model versioning, drift detection, and continuous learning management
        </p>
      </div>

      {historyError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
          Failed to load model history. Retrying automatically.
        </div>
      )}
      {shapError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
          Failed to load feature importance data. Retrying automatically.
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-5">
        <Card className="glass-panel border-neon-green/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground">Model Version</p>
              <p className="text-3xl font-bold text-neon-green">
                v{latestVersion?.model_version || 1}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-teal-500/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">MAE</p>
              <p className="text-2xl font-bold text-teal-400">
                {latestVersion?.metrics?.mae != null ? formatNumber(latestVersion.metrics.mae, 3) : '-'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-teal-500/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">RMSE</p>
              <p className="text-2xl font-bold text-teal-400">
                {latestVersion?.metrics?.rmse != null ? formatNumber(latestVersion.metrics.rmse, 3) : '-'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-neon-yellow/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">avg R²</p>
              <p className="text-2xl font-bold text-neon-yellow">
                {latestVersion?.metrics?.r2 != null ? formatNumber(latestVersion.metrics.r2, 4) : '-'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-orange-500/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">MAPE</p>
              <p className="text-2xl font-bold text-orange-400">
                {latestVersion?.metrics?.mape != null
                  ? `${formatNumber(latestVersion.metrics.mape * 100, 2)}%`
                  : '—'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Model Version History */}
      <Card className="glass-panel">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Model Version History</CardTitle>
            <div className="flex items-center gap-3">
              {retrainResult && (
                <div className={`flex items-center gap-2 text-sm px-3 py-1 rounded-full ${
                  retrainResult.retrained
                    ? 'bg-neon-green/15 text-neon-green'
                    : 'bg-secondary text-muted-foreground'
                }`}>
                  {retrainResult.retrained
                    ? <><CheckCircle className="h-4 w-4" /> Retrained successfully</>
                    : <><AlertCircle className="h-4 w-4" /> {Object.keys(retrainResult.flags).find(k => retrainResult.flags[k] === true) === 'cooldown_active' ? 'Cooldown active — no retrain needed' : 'No drift detected'}</>}
                </div>
              )}
              <Button variant="outline" size="sm" onClick={handleCheckRetrain} disabled={retrainLoading}>
                <RefreshCw className={`mr-2 h-4 w-4 ${retrainLoading ? 'animate-spin' : ''}`} />
                {retrainLoading ? 'Checking...' : 'Check Drift & Retrain'}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {modelHistory.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Version</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead className="text-right">MAE</TableHead>
                  <TableHead className="text-right">RMSE</TableHead>
                  <TableHead className="text-right">avg R²</TableHead>
                  <TableHead className="text-right">MAPE</TableHead>
                  <TableHead className="text-right">Dataset Size</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {modelHistory.map((version) => (
                  <TableRow key={version.model_version}>
                    <TableCell className="font-bold">v{version.model_version}</TableCell>
                    <TableCell className="text-sm">
                      {version.time
                        ? format(new Date(version.time), 'MMM dd, yyyy HH:mm')
                        : <span className="text-muted-foreground italic">Initial training</span>}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {Object.entries(version.reason).map(([key, value]) =>
                          value ? (
                            <span
                              key={key}
                              className="text-xs px-2 py-1 rounded bg-neon-red/20 text-neon-red"
                            >
                              {key.replace(/_/g, ' ')}
                            </span>
                          ) : null
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {version.metrics.mae != null ? formatNumber(version.metrics.mae, 3) : '—'}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {version.metrics.rmse != null ? formatNumber(version.metrics.rmse, 3) : '—'}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {version.metrics.r2 != null ? formatNumber(version.metrics.r2, 4) : '—'}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {version.metrics.mape != null
                        ? `${formatNumber((version.metrics.mape as number) * 100, 2)}%`
                        : '—'}
                    </TableCell>
                    <TableCell className="text-right">{version.dataset_size}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <AlertCircle className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <p>No model versions yet. Train the initial model to begin tracking.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Feature Importance */}
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            SHAP Global Feature Importance
          </CardTitle>
        </CardHeader>
        <CardContent>
          {shapLoading ? (
            <div className="space-y-3">
              <p className="text-xs text-muted-foreground mb-4 animate-pulse">
                Computing SHAP values across all model estimators — this may take a few seconds…
              </p>
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div
                    className="h-4 bg-secondary rounded animate-pulse"
                    style={{ width: `${60 + Math.round((i % 4) * 15)}px` }}
                  />
                  <div className="flex-1 h-6 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-secondary/60 rounded-full animate-pulse"
                      style={{ width: `${90 - i * 9}%`, animationDelay: `${i * 80}ms` }}
                    />
                  </div>
                  <div className="h-4 w-16 bg-secondary rounded animate-pulse" />
                </div>
              ))}
            </div>
          ) : featureImportance.length > 0 ? (
            <div className="space-y-3">
              {featureImportance.slice(0, 15).map((feature, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <span className="text-sm font-medium w-48">{feature.feature}</span>
                  <div className="flex-1 h-6 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(feature.importance / featureImportance[0].importance) * 100}%` }}
                      transition={{ duration: 0.5, delay: idx * 0.05 }}
                      className="h-full bg-gradient-to-r from-teal-600 to-teal-400"
                    />
                  </div>
                  <span className="text-sm font-mono text-muted-foreground w-20 text-right">
                    {formatNumber(feature.importance, 4)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              Feature importance will be available once the model is trained
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
