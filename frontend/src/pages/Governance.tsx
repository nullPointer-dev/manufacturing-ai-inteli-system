import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Shield, RefreshCw, TrendingUp, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { governanceApi } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import { format } from 'date-fns'

export function Governance() {
  const { data: modelHistory = [] } = useQuery({
    queryKey: ['model-history'],
    queryFn: governanceApi.getModelHistory,
  })

  const { data: featureImportance = [] } = useQuery({
    queryKey: ['feature-importance'],
    queryFn: governanceApi.getFeatureImportance,
  })

  const latestVersion = modelHistory[modelHistory.length - 1]

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

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="glass-panel border-neon-green/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Model Version</p>
                <p className="text-3xl font-bold text-neon-green">
                  v{latestVersion?.model_version || 1}
                </p>
              </div>
              <Shield className="h-10 w-10 text-neon-green opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-neon-blue/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">MAE</p>
              <p className="text-2xl font-bold text-neon-blue">
                {latestVersion ? formatNumber(latestVersion.metrics.mae, 3) : '-'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-neon-purple/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">RMSE</p>
              <p className="text-2xl font-bold text-neon-purple">
                {latestVersion ? formatNumber(latestVersion.metrics.rmse, 3) : '-'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-neon-yellow/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">MAPE</p>
              <p className="text-2xl font-bold text-neon-yellow">
                {latestVersion ? formatNumber(latestVersion.metrics.mape, 2) : '-'}%
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
            <Button variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Check Drift & Retrain
            </Button>
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
                  <TableHead className="text-right">Dataset Size</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {modelHistory.map((version) => (
                  <TableRow key={version.model_version}>
                    <TableCell className="font-bold">v{version.model_version}</TableCell>
                    <TableCell className="text-sm">
                      {format(new Date(version.time), 'MMM dd, yyyy HH:mm')}
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
                      {formatNumber(version.metrics.mae, 3)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatNumber(version.metrics.rmse, 3)}
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
            Global Feature Importance
          </CardTitle>
        </CardHeader>
        <CardContent>
          {featureImportance.length > 0 ? (
            <div className="space-y-3">
              {featureImportance.slice(0, 15).map((feature, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <span className="text-sm font-medium w-48">{feature.feature}</span>
                  <div className="flex-1 h-6 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(feature.importance / featureImportance[0].importance) * 100}%` }}
                      transition={{ duration: 0.5, delay: idx * 0.05 }}
                      className="h-full bg-gradient-to-r from-neon-blue to-neon-purple"
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
