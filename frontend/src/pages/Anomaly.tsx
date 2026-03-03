import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { AlertTriangle, Activity, TrendingUp, AlertCircle, CheckCircle, Wrench, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tooltip } from '@/components/ui/tooltip'
import { anomalyApi } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, ZAxis } from 'recharts'

export function Anomaly() {
  const { data: anomalies, isLoading, isError: anomaliesError } = useQuery({
    queryKey: ['anomalies'],
    queryFn: anomalyApi.getAnomalies,
  })

  const { data: assetReliability, isLoading: assetLoading, isError: assetError } = useQuery({
    queryKey: ['asset-reliability'],
    queryFn: anomalyApi.getAssetReliability,
  })

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'high':
        return 'text-red-500 bg-red-500/20'
      case 'medium':
        return 'text-yellow-500 bg-yellow-500/20'
      case 'low':
        return 'text-green-500 bg-green-500/20'
      default:
        return 'text-muted-foreground bg-muted/20'
    }
  }

  const getRiskIcon = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'high':
        return <AlertCircle className="h-4 w-4" />
      case 'medium':
        return <AlertTriangle className="h-4 w-4" />
      case 'low':
        return <CheckCircle className="h-4 w-4" />
      default:
        return null
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          Anomaly Detection & Reliability
          <Tooltip content="Uses Isolation Forest algorithm to detect unusual patterns in batch manufacturing data. Anomalies may indicate quality issues, equipment problems, or process deviations." />
        </h1>
        <p className="text-muted-foreground">
          Isolation Forest analysis with batch-level intelligence and risk assessment
        </p>
      </div>

      {anomaliesError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
          Failed to load anomaly data. Retrying automatically.
        </div>
      )}
      {assetError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
          Failed to load asset reliability data. Retrying automatically.
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="glass-panel border-teal-500/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground">Total Batches</p>
              <p className="text-3xl font-bold text-teal-500">
                {isLoading ? '...' : anomalies?.total_batches || 0}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-red-500/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                Anomalous Batches
                <Tooltip content="Batches flagged as anomalous by the Isolation Forest model based on deviation from normal patterns." />
              </p>
              <p className="text-3xl font-bold text-red-500">
                {isLoading ? '...' : anomalies?.anomalous_count || 0}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-yellow-500/30">
          <CardContent className="p-6">
            <div>
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                Contamination Rate
                <Tooltip content="Percentage of batches identified as anomalous. Default contamination parameter is 10%." />
              </p>
              <p className="text-3xl font-bold text-yellow-500">
                {isLoading ? '...' : `${anomalies?.contamination_rate || 0}%`}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-neon-teal/30">
          <CardContent className="p-6">
            <div className="flex flex-col gap-2">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                Risk Distribution
                <Tooltip content="Classification of anomalies by severity: High (score > 0.10), Medium (0.05-0.10), Low (< 0.05)" />
              </p>
              <div className="flex gap-3 text-xs">
                <div className="flex items-center gap-1">
                  <div className="h-2 w-2 rounded-full bg-red-500" />
                  <span>High: {anomalies?.risk_distribution.high || 0}</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-2 w-2 rounded-full bg-yellow-500" />
                  <span>Med: {anomalies?.risk_distribution.medium || 0}</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span>Low: {anomalies?.risk_distribution.low || 0}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Anomalous Batches Table */}
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            Anomalous Batches - Detailed Analysis
            <Tooltip content="Batches sorted by anomaly score (higher = more anomalous). Each batch's parameters deviate significantly from the normal manufacturing pattern." />
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">
              Loading anomaly analysis...
            </div>
          ) : anomalies && anomalies.anomalous_batches.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Batch ID</TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <span>Anomaly Score</span>
                      <Tooltip content="Higher scores indicate greater deviation from normal patterns. Calculated using Isolation Forest decision function." />
                    </div>
                  </TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <span>Quality</span>
                      <Tooltip content="Overall quality score (0-100). Lower scores may indicate defects or inconsistencies." />
                    </div>
                  </TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <span>Yield</span>
                      <Tooltip content="Percentage of acceptable output. Lower yield indicates waste or production issues." />
                    </div>
                  </TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <span>Performance</span>
                      <Tooltip content="Overall equipment effectiveness (OEE). Lower values suggest downtime or inefficiency." />
                    </div>
                  </TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <span>Energy</span>
                      <Tooltip content="Total energy consumption in kWh. Unusual values may indicate equipment malfunction." />
                    </div>
                  </TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <span>CO₂</span>
                      <Tooltip content="Carbon emissions in kg. Calculated from energy usage (0.82 kg CO₂/kWh)." />
                    </div>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {anomalies.anomalous_batches.map((batch) => (
                  <TableRow key={batch.batch_id} className="hover:bg-muted/50">
                    <TableCell className="font-medium font-mono">{batch.batch_id}</TableCell>
                    <TableCell className="text-right font-mono text-red-500">
                      {formatNumber(batch.anomaly_score, 4)}
                    </TableCell>
                    <TableCell>
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${getRiskColor(batch.risk_level)}`}>
                        {getRiskIcon(batch.risk_level)}
                        {batch.risk_level}
                      </span>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatNumber(batch.quality, 2)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatNumber(batch.yield, 1)}%
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatNumber(batch.performance, 1)}%
                    </TableCell>
                    <TableCell className="text-right font-mono text-yellow-500">
                      {formatNumber(batch.energy, 1)} kWh
                    </TableCell>
                    <TableCell className="text-right font-mono text-red-400">
                      {formatNumber(batch.co2, 1)} kg
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <CheckCircle className="h-16 w-16 mx-auto mb-4 text-green-500 opacity-50" />
              <p>No anomalies detected in current batch data</p>
              <p className="text-sm mt-2">All batches are within normal operating patterns</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Isolation Forest Visualization */}
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Isolation Forest Anomaly Scores - Interactive Scatter Plot
            <Tooltip content="Interactive scatter plot showing quality vs energy consumption. Each point represents a batch - hover to see details. Red points are anomalies detected by Isolation Forest algorithm, green points are normal batches." />
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">
              Loading visualization...
            </div>
          ) : anomalies && anomalies.all_batches.length > 0 ? (
            <div className="space-y-4">
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart margin={{ top: 24, right: 32, bottom: 36, left: 32 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis 
                    type="number" 
                    dataKey="content_uniformity" 
                    name="Content Uniformity"
                    stroke="hsl(var(--muted-foreground))"
                    tick={{ fontSize: 11, fontFamily: 'Inter, sans-serif', letterSpacing: '0.02em', fill: 'hsl(var(--muted-foreground))' }}
                    tickLine={{ stroke: 'hsl(var(--border))' }}
                    label={{ 
                      value: 'Content Uniformity (%)', 
                      position: 'insideBottom', 
                      offset: -20,
                      style: { fill: 'hsl(var(--muted-foreground))', fontSize: 12, fontFamily: 'Inter, sans-serif', letterSpacing: '0.04em', fontWeight: 500 }
                    }}
                    domain={['dataMin - 2', 'dataMax + 2']}
                  />
                  <YAxis 
                    type="number" 
                    dataKey="anomaly_score" 
                    name="Anomaly Score"
                    stroke="hsl(var(--muted-foreground))"
                    tick={{ fontSize: 11, fontFamily: 'Inter, sans-serif', letterSpacing: '0.02em', fill: 'hsl(var(--muted-foreground))' }}
                    tickLine={{ stroke: 'hsl(var(--border))' }}
                    width={72}
                    label={{ 
                      value: 'Anomaly Score', 
                      angle: -90, 
                      position: 'insideLeft',
                      offset: -12,
                      style: { fill: 'hsl(var(--muted-foreground))', fontSize: 12, fontFamily: 'Inter, sans-serif', letterSpacing: '0.04em', fontWeight: 500 }
                    }}
                  />
                  <ZAxis type="number" dataKey="quality" range={[20, 100]} name="Quality" />
                  <RechartsTooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      padding: '12px',
                    }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload
                        return (
                          <div className="glass-panel border-neon-teal/30 px-3 py-2 rounded">
                            <div className="font-bold mb-1 tracking-wide">{data.batch_id}</div>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between gap-4">
                                <span className="text-muted-foreground tracking-wide">Quality:</span>
                                <span className="font-mono">{formatNumber(data.quality, 2)}</span>
                              </div>
                              <div className="flex justify-between gap-4">
                                <span className="text-muted-foreground tracking-wide">Content Uniformity:</span>
                                <span className="font-mono">{formatNumber(data.content_uniformity, 2)}%</span>
                              </div>
                              <div className="flex justify-between gap-4">
                                <span className="text-muted-foreground tracking-wide">Energy:</span>
                                <span className="font-mono">{formatNumber(data.energy, 1)} kWh</span>
                              </div>
                              <div className="flex justify-between gap-4">
                                <span className="text-muted-foreground tracking-wide">Anomaly Score:</span>
                                <span className="font-mono">{formatNumber(data.anomaly_score, 4)}</span>
                              </div>
                              <div className="flex justify-between gap-4">
                                <span className="text-muted-foreground tracking-wide">Risk Level:</span>
                                <span className={`font-semibold tracking-wider uppercase text-xs ${
                                  data.risk_level.toLowerCase() === 'high' ? 'text-red-500' :
                                  data.risk_level.toLowerCase() === 'medium' ? 'text-yellow-500' :
                                  'text-green-500'
                                }`}>{data.risk_level}</span>
                              </div>
                              {data.is_anomaly === 1 && (
                                <div className="mt-2 pt-2 border-t border-border">
                                  <span className="text-red-500 font-bold text-xs tracking-widest uppercase">⚠ Anomaly Detected</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )
                      }
                      return null
                    }}
                  />
                  <Scatter 
                    name="Batches" 
                    data={anomalies.all_batches}
                    fill="#8884d8"
                  >
                    {anomalies.all_batches.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.is_anomaly === 1 ? '#ef4444' : '#10b981'}
                        opacity={0.8}
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
              <div className="border-t border-border pt-3">
                <div className="flex justify-center gap-8 text-xs tracking-widest uppercase font-medium">
                  <span className="flex items-center gap-2">
                    <div className="h-2.5 w-2.5 rounded-full bg-green-500" />
                    <span className="text-muted-foreground">Normal ({anomalies.all_batches.filter(b => b.is_anomaly === 0).length})</span>
                  </span>
                  <span className="flex items-center gap-2">
                    <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                    <span className="text-muted-foreground">Anomaly ({anomalies.anomalous_count})</span>
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              No batch data available for visualization
            </div>
          )}
        </CardContent>
      </Card>

      {/* Asset Reliability & Predictive Maintenance */}
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wrench className="h-5 w-5 text-neon-yellow" />
            Asset Reliability & Predictive Maintenance
          </CardTitle>
        </CardHeader>
        <CardContent>
          {assetLoading ? (
            <div className="text-center py-8 text-muted-foreground">Loading asset analysis...</div>
          ) : assetReliability ? (
            <>
              {/* State summary */}
              <div className="grid grid-cols-4 gap-4 mb-6">
                {[
                  { key: 'stable',               label: 'Stable',              color: 'text-green-400 border-green-500/30 bg-green-500/5' },
                  { key: 'efficiency_loss',       label: 'Efficiency Loss',     color: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/5' },
                  { key: 'process_instability',   label: 'Process Instability', color: 'text-orange-400 border-orange-500/30 bg-orange-500/5' },
                  { key: 'calibration_gain',      label: 'Calibration Gain',   color: 'text-teal-500 border-teal-500/30 bg-teal-500/5' },
                ].map(({ key, label, color }) => (
                  <div key={key} className={`rounded-lg border p-4 text-center ${color}`}>
                    <p className="text-2xl font-bold">{assetReliability.summary[key as keyof typeof assetReliability.summary]}</p>
                    <p className="text-xs mt-1 text-muted-foreground">{label}</p>
                  </div>
                ))}
              </div>

              {/* Per-batch table — only batches that require action */}
              {(() => {
                const actionable = [...assetReliability.batches]
                  .filter((b) => b.maintenance_action !== 'No action required')
                  .sort((a, b) => {
                    const order: Record<string, number> = { 'Efficiency Loss': 0, 'Process Instability': 1, 'Calibration Gain': 2, 'Stable': 3 }
                    return (order[a.reliability_state] ?? 3) - (order[b.reliability_state] ?? 3)
                  })
                  .slice(0, 20)

                if (actionable.length === 0) {
                  return (
                    <div className="text-center py-8 text-green-400 flex flex-col items-center gap-2">
                      <CheckCircle className="h-8 w-8" />
                      <p className="font-medium">All batches are operating normally — no maintenance actions required.</p>
                    </div>
                  )
                }

                return (
                  <>
                    <p className="text-xs text-muted-foreground mb-3">
                      Showing {actionable.length} batch{actionable.length !== 1 ? 'es' : ''} with attributed asset causes (batches in normal stable operation are omitted).
                    </p>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Batch ID</TableHead>
                          <TableHead>Reliability State</TableHead>
                          <TableHead>Asset Cause</TableHead>
                          <TableHead>Recommended Action</TableHead>
                          <TableHead className="text-right">Energy Drift</TableHead>
                          <TableHead className="text-right">Instability</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {actionable.map((batch, idx) => (
                          <TableRow key={idx} className="bg-yellow-500/5">
                            <TableCell className="font-mono text-sm">{batch.batch_id}</TableCell>
                            <TableCell>
                              <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                                batch.reliability_state === 'Efficiency Loss' ? 'bg-yellow-500/20 text-yellow-400' :
                                batch.reliability_state === 'Process Instability' ? 'bg-orange-500/20 text-orange-400' :
                                'bg-teal-500/20 text-teal-500'
                              }`}>
                                {batch.reliability_state}
                              </span>
                            </TableCell>
                            <TableCell className="text-xs text-muted-foreground whitespace-normal break-words max-w-[200px]">{batch.asset_cause}</TableCell>
                            <TableCell className="text-sm max-w-xs">
                              <div className="flex items-start gap-1 text-orange-300">
                                <Zap className="h-3 w-3 mt-0.5 flex-shrink-0" />
                                <span className="text-xs">{batch.maintenance_action}</span>
                              </div>
                            </TableCell>
                            <TableCell className={`text-right font-mono text-sm ${batch.energy_drift > 0.05 ? 'text-yellow-400' : batch.energy_drift < -0.05 ? 'text-teal-500' : 'text-muted-foreground'}`}>
                              {batch.energy_drift > 0 ? '+' : ''}{formatNumber(batch.energy_drift * 100, 1)}%
                            </TableCell>
                            <TableCell className={`text-right font-mono text-sm ${batch.instability_score > 0.5 ? 'text-orange-400' : 'text-muted-foreground'}`}>
                              {formatNumber(batch.instability_score, 3)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </>
                )
              })()}
            </>
          ) : (
            <div className="text-center py-8 text-muted-foreground">No asset reliability data available</div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
