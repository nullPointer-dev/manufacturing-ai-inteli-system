import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Factory, AlertTriangle, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tooltip } from '@/components/ui/tooltip'
import { systemApi, anomalyApi } from '@/lib/api'
import { useSystemStore } from '@/store/systemStore'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts'

export function Dashboard() {
  const { setStatus } = useSystemStore()
  const navigate = useNavigate()

  // Fetch system status
  const { data: systemStatus } = useQuery({
    queryKey: ['system-status'],
    queryFn: systemApi.getStatus,
    refetchInterval: 30000,
  })

  // Sync system status to store when data changes
  useEffect(() => {
    if (systemStatus) setStatus(systemStatus)
  }, [systemStatus])

  // Fetch dashboard statistics from real data
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: systemApi.getDashboardStats,
    refetchInterval: 60000, // Refresh every minute
  })

  // Fetch anomaly detection results
  const { data: anomalies, isLoading: anomaliesLoading } = useQuery({
    queryKey: ['anomalies'],
    queryFn: anomalyApi.getAnomalies,
    refetchInterval: 120000, // Refresh every 2 minutes
  })

  // Fetch production trends
  const { data: productionTrends, isLoading: trendsLoading } = useQuery({
    queryKey: ['production-trends'],
    queryFn: systemApi.getProductionTrends,
    refetchInterval: 120000, // Refresh every 2 minutes
  })

  // Check if initial data is loading
  const isInitialLoading = statsLoading && !stats

  const metrics = stats?.current || {
    quality: 0,
    yield: 0,
    performance: 0,
    energy: 0,
    co2: 0,
    energy_efficiency: 0,
  }

  const trends = stats?.trends || {
    quality: 0,
    yield: 0,
    performance: 0,
    energy: 0,
    co2: 0,
  }

  const getTrend = (value: number): 'up' | 'down' | 'neutral' => {
    if (value > 0.5) return 'up'
    if (value < -0.5) return 'down'
    return 'neutral'
  }

  const getEnergyTrend = (value: number): 'up' | 'down' | 'neutral' => {
    // For energy and CO2, down is good
    if (value < -0.5) return 'up' // improvement shown as up
    if (value > 0.5) return 'down' // increase shown as down
    return 'neutral'
  }

  return (
    <>
      {/* Loading Overlay */}
      <AnimatePresence>
        {isInitialLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="flex flex-col items-center gap-6 p-12 rounded-xl bg-card/90 border border-teal-500/30 shadow-2xl"
            >
              <div className="relative">
                <Loader2 className="h-16 w-16 text-teal-400 animate-spin" />
                <div className="absolute inset-0 h-16 w-16 bg-teal-500/20 rounded-full animate-pulse" />
              </div>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold text-teal-400">Processing Data</h2>
                <p className="text-muted-foreground">Loading manufacturing intelligence...</p>
              </div>
              <div className="flex gap-1">
                <motion.div
                  className="w-2 h-2 bg-teal-400 rounded-full"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="w-2 h-2 bg-teal-400 rounded-full"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                  className="w-2 h-2 bg-teal-400 rounded-full"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-6"
      >
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-primary/20 to-violet-500/20 p-6 border border-violet-500/30">
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">Manufacturing AI Intelligence System</h1>
          <p className="text-muted-foreground">
            Real-time adaptive multi-objective optimization | Batch-level intelligence | Golden signature management
          </p>
        </div>
        <div className="absolute right-0 top-0 h-full w-64 opacity-10">
          <Factory className="h-full w-full" />
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 grid-cols-3">
        <MetricCard
          title="Quality Score"
          value={metrics.quality}
          trend={getTrend(trends.quality)}
          trendValue={trends.quality}
          tooltip="Overall quality score based on defect rates, consistency, and product specifications. Higher is better."
        />
        <MetricCard
          title="Yield"
          value={metrics.yield}
          unit="%"
          trend={getTrend(trends.yield)}
          trendValue={trends.yield}
          tooltip="Content uniformity percentage - measures consistency of tablet composition across batches. Higher values indicate better manufacturing control."
        />
        <MetricCard
          title="Performance"
          value={metrics.performance}
          unit=" Score"
          trend={getTrend(trends.performance)}
          trendValue={trends.performance}
          tooltip="Production throughput score (0-100) - measures quality output per unit time. Higher scores indicate better production efficiency."
        />
        <MetricCard
          title="Energy"
          value={metrics.energy}
          unit=" kWh"
          trend={getEnergyTrend(trends.energy)}
          trendValue={Math.abs(trends.energy)}
          tooltip="Total energy consumption per batch. Lower values indicate better energy efficiency."
        />
        <MetricCard
          title="CO₂ Emissions"
          value={metrics.co2}
          unit=" kg"
          trend={getEnergyTrend(trends.co2)}
          trendValue={Math.abs(trends.co2)}
          tooltip="Carbon dioxide emissions calculated from energy usage (0.82 kg CO₂ per kWh). Lower is better."
        />
        <Card className="glass-panel h-full relative overflow-hidden group">
          <CardContent className="p-6 flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <p className="text-lg font-bold whitespace-nowrap">Anomalies</p>
                <Tooltip content="Number of batches flagged as anomalous by Isolation Forest algorithm. Click to view details and analysis." />
              </div>
              <div className="flex items-baseline gap-2">
                <span className={`text-2xl font-bold ${anomalies && anomalies.anomalous_count > 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {anomaliesLoading ? '...' : anomalies?.anomalous_count || 0}
                </span>
                <span className="text-xs text-muted-foreground">
                  / {anomalies?.total_batches || 0} batches
                </span>
              </div>
              {anomalies && anomalies.anomalous_count > 0 && (
                <div className="mt-2 text-xs text-red-500 font-bold flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  {anomalies.contamination_rate}% contamination
                </div>
              )}
            </div>
            <Button
              size="sm"
              variant="neon"
              onClick={() => navigate('/anomaly')}
              className="mt-3 w-full opacity-0 group-hover:opacity-100 transition-opacity"
            >
              View Analysis
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Production Trends */}
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle>Production Performance Trends</CardTitle>
        </CardHeader>
        <CardContent>
          {trendsLoading ? (
            <div className="h-64 flex items-center justify-center text-muted-foreground">
              Loading trends data...
            </div>
          ) : productionTrends && productionTrends.trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={productionTrends.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="batch_number" 
                  stroke="hsl(var(--muted-foreground))"
                  label={{ value: 'Batch Number', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
                />
                <RechartsTooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))', 
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                  labelFormatter={(value) => `Batch #${value}`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="quality" 
                  stroke="#10b981" 
                  name="Quality Score"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="energy" 
                  stroke="#f59e0b" 
                  name="Energy (kWh)"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="performance" 
                  stroke="#3b82f6" 
                  name="Performance"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="content_uniformity" 
                  stroke="#8b5cf6" 
                  name="Content Uniformity (%)"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-muted-foreground">
              No trends data available
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
    </>
  )
}
