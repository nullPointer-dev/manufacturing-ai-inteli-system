import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Target, Play, CheckCircle, XCircle, Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useOptimizationStore } from '@/store/optimizationStore'
import { optimizationApi, goldenApi } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import type { OptimizationMode } from '@/types'

const modes: { value: OptimizationMode; label: string; description: string }[] = [
  { value: 'balanced', label: 'Balanced', description: '30% Q, 30% Y, 20% P, 10% E, 10% CO₂' },
  { value: 'eco', label: 'Eco', description: '40% Energy focus' },
  { value: 'quality', label: 'Quality', description: '50% Quality focus' },
  { value: 'yield', label: 'Yield', description: '50% Yield focus' },
  { value: 'performance', label: 'Performance', description: '50% Performance focus' },
  { value: 'custom', label: 'Custom', description: 'Define your own weights' },
]

export function Optimization() {
  const {
    mode,
    customWeights,
    results,
    proposal,
    clusterId,
    scenarioKey,
    setMode,
    setCustomWeights,
    setResults,
    setProposal,
    clearProposal,
  } = useOptimizationStore()

  const [optimizationType, setOptimizationType] = useState<'auto' | 'target'>('auto')
  const [constraints, setConstraints] = useState({
    required_reduction: 2.0,
    min_quality: 75,
    min_yield: 85,
    min_performance: 80,
  })

  const optimizeMutation = useMutation({
    mutationFn: async () => {
      if (optimizationType === 'auto') {
        return optimizationApi.optimizeAuto(
          mode,
          mode === 'custom' ? customWeights : undefined
        )
      } else {
        return optimizationApi.optimizeTarget(constraints, mode)
      }
    },
    onSuccess: (data) => {
      console.log('Optimization response:', data)
      if (data.status === 'success') {
        const result = data.top_result || data.best_solution
        if (result) {
          console.log('Setting results:', result)
          setResults([result])
          if (data.proposal && data.cluster_id !== undefined) {
            setProposal(true, data.cluster_id, data.scenario_key)
          }
        }
      } else {
        console.error('Optimization failed:', data)
      }
    },
    onError: (error) => {
      console.error('Optimization error:', error)
    },
  })

  const acceptGoldenMutation = useMutation({
    mutationFn: async () => {
      if (!results[0] || clusterId === null) return
      return goldenApi.acceptGolden(
        results[0],
        mode,
        clusterId,
        scenarioKey || undefined
      )
    },
    onSuccess: () => {
      clearProposal()
    },
  })

  const rejectGolden = () => {
    clearProposal()
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold mb-2">Multi-Objective Optimization</h1>
        <p className="text-muted-foreground">
          NSGA-II optimization with adaptive golden signature management
        </p>
      </div>

      {/* Configuration Section */}
      <div className="space-y-6">
        <div className="grid grid-cols-4 gap-6">
          {/* Optimization Scenario - 2x3 Grid */}
          <Card className="glass-panel col-span-3">
            <CardHeader className="pb-4">
              <CardTitle className="text-base">Optimization Scenario</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {modes.map((m) => (
                  <button
                    key={m.value}
                    onClick={() => setMode(m.value)}
                    className={`text-left p-4 rounded-lg border transition-all ${
                      mode === m.value
                        ? 'border-neon-blue bg-neon-blue/20 text-neon-blue'
                        : 'border-border hover:border-neon-blue/50'
                    }`}
                  >
                    <div className="font-semibold text-sm mb-1">{m.label}</div>
                    <div className="text-xs text-muted-foreground leading-relaxed">{m.description}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Strategy - 1x2 Grid */}
          <Card className="glass-panel col-span-1">
            <CardHeader className="pb-4">
              <CardTitle className="text-base">Strategy</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                <button
                  onClick={() => setOptimizationType('auto')}
                  className={`text-left p-4 rounded-lg border transition-all ${
                    optimizationType === 'auto'
                      ? 'border-neon-green bg-neon-green/20 text-neon-green'
                      : 'border-border hover:border-neon-green/50'
                  }`}
                >
                  <div className="font-semibold text-sm mb-1">Automatic</div>
                  <div className="text-xs text-muted-foreground leading-relaxed">Learn best process</div>
                </button>
                <button
                  onClick={() => setOptimizationType('target')}
                  className={`text-left p-4 rounded-lg border transition-all ${
                    optimizationType === 'target'
                      ? 'border-neon-green bg-neon-green/20 text-neon-green'
                      : 'border-border hover:border-neon-green/50'
                  }`}
                >
                  <div className="font-semibold text-sm mb-1">Target-Based</div>
                  <div className="text-xs text-muted-foreground leading-relaxed">Meet defined goals</div>
                </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Custom Weights */}
        <AnimatePresence>
          {mode === 'custom' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <Card className="glass-panel border-neon-purple/30">
                <CardHeader className="pb-4">
                  <CardTitle className="text-base">Custom Weights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-5 gap-6">
                    {Object.entries(customWeights).map(([key, value]) => (
                      <div key={key} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <Label className="font-medium">{key.charAt(0).toUpperCase() + key.slice(1)}</Label>
                          <span className="text-neon-purple font-semibold">{(value * 100).toFixed(0)}%</span>
                        </div>
                        <Slider
                          value={[value * 100]}
                          onValueChange={([v]) => setCustomWeights({ ...customWeights, [key]: v / 100 })}
                          max={100}
                          step={1}
                        />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Target Constraints */}
        <AnimatePresence>
          {optimizationType === 'target' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <Card className="glass-panel border-neon-yellow/30">
                <CardHeader className="pb-4">
                  <CardTitle className="text-base">Constraints</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-4 gap-6">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">CO₂ Reduction (%)</Label>
                      <Input
                        type="number"
                        step="0.1"
                        value={constraints.required_reduction}
                        onChange={(e) =>
                          setConstraints({ ...constraints, required_reduction: parseFloat(e.target.value) })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Min Quality</Label>
                      <Input
                        type="number"
                        value={constraints.min_quality}
                        onChange={(e) =>
                          setConstraints({ ...constraints, min_quality: parseFloat(e.target.value) })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Min Yield</Label>
                      <Input
                        type="number"
                        value={constraints.min_yield}
                        onChange={(e) =>
                          setConstraints({ ...constraints, min_yield: parseFloat(e.target.value) })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Min Performance</Label>
                      <Input
                        type="number"
                        value={constraints.min_performance}
                        onChange={(e) =>
                          setConstraints({ ...constraints, min_performance: parseFloat(e.target.value) })
                        }
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Run Optimization Button - Centered */}
        <div className="flex justify-center pt-2">
          <Button
            variant="neon"
            className="px-16 py-6 text-base shadow-none"
            size="lg"
            onClick={() => optimizeMutation.mutate()}
            disabled={optimizeMutation.isPending}
          >
            <Play className="mr-2 h-5 w-5" />
            {optimizeMutation.isPending ? 'Optimizing...' : 'Run Optimization'}
          </Button>
        </div>
      </div>

      {/* Results Section */}
      <div className="space-y-4">
          <AnimatePresence mode="wait">
            {results.length > 0 ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                {/* Golden Proposal */}
                <AnimatePresence>
                  {proposal && (
                    <motion.div
                      initial={{ opacity: 0, y: -20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <Card className="glass-panel border-neon-green bg-neon-green/10">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-3">
                              <Sparkles className="h-6 w-6 text-neon-green mt-1" />
                              <div>
                                <h3 className="font-bold text-neon-green mb-1">
                                  Golden Signature Improvement Detected
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                  This solution exceeds the current golden benchmark for {mode} mode
                                  {scenarioKey && ` (scenario: ${scenarioKey})`} in cluster {clusterId}.
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                variant="default"
                                size="sm"
                                onClick={() => acceptGoldenMutation.mutate()}
                                disabled={acceptGoldenMutation.isPending}
                              >
                                <CheckCircle className="mr-1 h-4 w-4" />
                                Accept
                              </Button>
                              <Button variant="outline" size="sm" onClick={rejectGolden}>
                                <XCircle className="mr-1 h-4 w-4" />
                                Reject
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Optimal Solution */}
                <Card className="glass-panel">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-neon-blue" />
                      Optimal Solution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {/* Primary KPIs */}
                    <div className="grid grid-cols-5 gap-4 mb-6">
                      {['Quality', 'Yield', 'Performance', 'Energy', 'CO2'].map((metric) => (
                        <div key={metric} className="text-center">
                          <p className="text-xs text-muted-foreground mb-1">{metric}</p>
                          <p className="text-2xl font-bold text-neon-blue">
                            {formatNumber(results[0][metric] || 0, 1)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {metric === 'Energy' ? 'kWh' : metric === 'CO2' ? 'kg' : ''}
                          </p>
                        </div>
                      ))}
                    </div>

                    <div className="border-t border-border pt-4 space-y-6">
                      {/* Performance Metrics */}
                      <div>
                        <p className="text-sm font-semibold mb-3 text-neon-green">Performance Metrics</p>
                        <div className="grid grid-cols-4 gap-4">
                          {['Hardness', 'Dissolution_Rate', 'Content_Uniformity', 'Friability'].map((metric) => (
                            results[0][metric] !== undefined && (
                              <div key={metric} className="bg-background/50 rounded p-3">
                                <p className="text-xs text-muted-foreground mb-1">{metric.replace(/_/g, ' ')}</p>
                                <p className="text-lg font-semibold">{formatNumber(results[0][metric] as number, 2)}</p>
                              </div>
                            )
                          ))}
                        </div>
                      </div>

                      {/* Process Parameters */}
                      <div>
                        <p className="text-sm font-semibold mb-3 text-neon-purple">Process Parameters</p>
                        <Table>
                          <TableBody>
                            {[
                              'Granulation_Time', 'Binder_Amount', 'Drying_Temp', 'Drying_Time',
                              'Compression_Force', 'Machine_Speed', 'Lubricant_Conc', 'Moisture_Content',
                              'Tablet_Weight', 'Disintegration_Time'
                            ].map((param) => (
                              results[0][param] !== undefined && (
                                <TableRow key={param}>
                                  <TableCell className="text-sm">{param.replace(/_/g, ' ')}</TableCell>
                                  <TableCell className="text-right text-sm font-mono">
                                    {formatNumber(results[0][param] as number, 2)}
                                  </TableCell>
                                </TableRow>
                              )
                            ))}
                          </TableBody>
                        </Table>
                      </div>

                      {/* Energy & Efficiency */}
                      <div className="border border-neon-yellow/30 rounded-lg p-4 bg-neon-yellow/5">
                        <p className="text-base font-bold mb-4 text-neon-yellow">Energy & Efficiency</p>
                        <div className="grid grid-cols-4 gap-4">
                          {['energy_per_tablet', 'energy_efficiency_score', 'process_efficiency', 'equipment_load'].map((metric) => (
                            results[0][metric] !== undefined && (
                              <div key={metric} className="bg-background/70 rounded border border-border p-3">
                                <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wide">{metric.replace(/_/g, ' ')}</p>
                                <p className="text-xl font-bold">{formatNumber(results[0][metric] as number, 3)}</p>
                              </div>
                            )
                          ))}
                        </div>
                      </div>

                      {/* Process Timing */}
                      <div className="border border-orange-500/30 rounded-lg p-4 bg-orange-500/5">
                        <p className="text-base font-bold mb-4 text-orange-400">Process Timing (minutes)</p>
                        <div className="grid grid-cols-4 gap-4">
                          {Object.entries(results[0])
                            .filter(([key]) => key.startsWith('duration_'))
                            .map(([key, value]) => (
                              <div key={key} className="bg-background/70 rounded border border-border p-3">
                                <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wide">{key.replace('duration_', '').replace(/_/g, ' ')}</p>
                                <p className="text-lg font-bold">{formatNumber(value as number, 1)}</p>
                              </div>
                            ))}
                        </div>
                      </div>

                      {/* Process Conditions */}
                      <div className="border border-emerald-500/30 rounded-lg p-4 bg-emerald-500/5">
                        <p className="text-base font-bold mb-4 text-emerald-400">Process Conditions</p>
                        <div className="grid grid-cols-4 gap-4">
                          {['avg_power_consumption', 'avg_temperature', 'avg_pressure', 'avg_vibration'].map((metric) => (
                            results[0][metric] !== undefined && (
                              <div key={metric} className="bg-background/70 rounded border border-border p-3">
                                <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wide">{metric.replace(/avg_/g, '').replace(/_/g, ' ')}</p>
                                <p className="text-xl font-bold">{formatNumber(results[0][metric] as number, 2)}</p>
                              </div>
                            )
                          ))}
                        </div>
                      </div>

                      {/* Advanced Scores */}
                      {(results[0]['yield_score'] !== undefined || results[0]['stability_index'] !== undefined) && (
                        <div className="border border-purple-500/30 rounded-lg p-4 bg-purple-500/5">
                          <p className="text-base font-bold mb-4 text-purple-400">Advanced Scores</p>
                          <div className="grid grid-cols-4 gap-4">
                            {['yield_score', 'performance_score', 'stability_index', 'process_intensity'].map((metric) => (
                              results[0][metric] !== undefined && (
                                <div key={metric} className="bg-background/70 rounded border border-border p-3">
                                  <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wide">{metric.replace(/_/g, ' ')}</p>
                                  <p className="text-xl font-bold">{formatNumber(results[0][metric] as number, 3)}</p>
                                </div>
                              )
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <Card className="glass-panel h-96">
                  <CardContent className="h-full flex items-center justify-center">
                    <div className="text-center">
                      <Target className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                      <p className="text-muted-foreground">
                        Configure optimization parameters and click Run to discover optimal solutions
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
    </motion.div>
  )
}
