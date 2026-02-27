import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatNumber } from '@/lib/utils'

interface GaugeProps {
  title: string
  value: number
  min: number
  max: number
  unit?: string
  thresholds?: {
    low: number
    medium: number
    high: number
  }
}

export function Gauge({
  title,
  value,
  min,
  max,
  unit = '',
  thresholds = { low: 0.3, medium: 0.6, high: 1 },
}: GaugeProps) {
  const percentage = ((value - min) / (max - min)) * 100
  const normalized = (value - min) / (max - min)

  let color = '#00f3ff' // blue
  if (normalized < thresholds.low) color = '#ff0055' // red
  else if (normalized < thresholds.medium) color = '#ffed00' // yellow
  else color = '#00ff88' // green

  return (
    <Card className="glass-panel h-full">
      <CardHeader>
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center gap-4">
          <div className="relative h-32 w-32">
            <svg className="h-full w-full -rotate-90 transform">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r="56"
                fill="none"
                stroke="hsl(var(--border))"
                strokeWidth="8"
              />
              {/* Progress circle */}
              <motion.circle
                cx="64"
                cy="64"
                r="56"
                fill="none"
                stroke={color}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 56}`}
                initial={{ strokeDashoffset: 2 * Math.PI * 56 }}
                animate={{
                  strokeDashoffset: 2 * Math.PI * 56 * (1 - percentage / 100),
                }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold" style={{ color }}>
                {formatNumber(value, 1)}
              </span>
              <span className="text-xs text-muted-foreground">{unit}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
