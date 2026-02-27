import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Factory } from 'lucide-react'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { Gauge } from '@/components/dashboard/Gauge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { systemApi } from '@/lib/api'
import { useSystemStore } from '@/store/systemStore'

export function Dashboard() {
  const { setStatus } = useSystemStore()

  // Fetch system status
  const { data: systemStatus } = useQuery({
    queryKey: ['system-status'],
    queryFn: systemApi.getStatus,
    refetchInterval: 30000,
    onSuccess: (data) => setStatus(data),
  })

  // Mock data for demo - in production, fetch from backend
  const mockMetrics = {
    quality: 85.4,
    yield: 92.1,
    performance: 88.7,
    energy: 245.3,
    co2: 201.1,
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-primary/20 to-neon-blue/20 p-6 border border-neon-blue/30">
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
      <div className="grid gap-4 grid-cols-5">
        <MetricCard
          title="Quality Score"
          value={mockMetrics.quality}
          trend="up"
          trendValue={3.2}
        />
        <MetricCard
          title="Yield"
          value={mockMetrics.yield}
          unit="%"
          trend="up"
          trendValue={1.8}
        />
        <MetricCard
          title="Performance"
          value={mockMetrics.performance}
          unit="%"
          trend="neutral"
          trendValue={0.3}
        />
        <MetricCard
          title="Energy"
          value={mockMetrics.energy}
          unit=" kWh"
          trend="down"
          trendValue={2.5}
        />
        <MetricCard
          title="CO₂ Emissions"
          value={mockMetrics.co2}
          unit=" kg"
          trend="down"
          trendValue={2.1}
        />
      </div>

      {/* Gauges */}
      <div className="grid gap-4 grid-cols-4">
        <Gauge
          title="Quality Index"
          value={mockMetrics.quality}
          min={0}
          max={100}
          thresholds={{ low: 0.6, medium: 0.75, high: 1 }}
        />
        <Gauge
          title="Yield Rate"
          value={mockMetrics.yield}
          min={0}
          max={100}
          unit="%"
          thresholds={{ low: 0.7, medium: 0.85, high: 1 }}
        />
        <Gauge
          title="Performance"
          value={mockMetrics.performance}
          min={0}
          max={100}
          unit="%"
          thresholds={{ low: 0.65, medium: 0.8, high: 1 }}
        />
        <Gauge
          title="Energy Efficiency"
          value={100 - ((mockMetrics.energy - 200) / 100) * 100}
          min={0}
          max={100}
          unit="%"
          thresholds={{ low: 0.6, medium: 0.75, high: 1 }}
        />
      </div>

      {/* Production Trends (Placeholder) */}
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle>Production Performance Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            Recharts visualization will be rendered here
            <br />
            (Energy consumption, Quality trends, Batch performance over time)
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
