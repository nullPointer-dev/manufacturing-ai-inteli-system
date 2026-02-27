import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { formatNumber } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: number
  unit?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: number
  decimals?: number
}

export function MetricCard({
  title,
  value,
  unit = '',
  trend,
  trendValue,
  decimals = 2,
}: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="h-full"
    >
      <Card className="glass-panel h-full">
        <CardContent className="p-6 flex flex-col justify-between h-full">
          <div>
            <p className="text-lg font-bold mb-2 whitespace-nowrap overflow-hidden text-ellipsis">{title}</p>
            <div className="flex items-baseline gap-2">
              <span className="text-muted-foreground whitespace-nowrap">
                {formatNumber(value, decimals)}{unit}
              </span>
            </div>
            {trend && trendValue !== undefined && (
              <div className={`mt-2 text-xs font-bold whitespace-nowrap ${trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-muted-foreground'}`}>
                {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {formatNumber(Math.abs(trendValue), 1)}% vs baseline
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
