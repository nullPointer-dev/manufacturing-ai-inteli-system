import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { format } from 'date-fns'
import type { GoldenHistoryEntry } from '@/types'

interface TimelineProps {
  entries: GoldenHistoryEntry[]
}

export function GoldenTimeline({ entries }: TimelineProps) {
  return (
    <Card className="glass-panel">
      <CardHeader>
        <CardTitle>Recent Golden Updates</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative space-y-4">
          {/* Timeline line */}
          <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-border" />

          {entries.slice(0, 5).map((entry, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative flex gap-4 pl-8"
            >
              {/* Timeline dot */}
              <div className="absolute left-0 top-1 h-5 w-5 rounded-full border-2 border-neon-green bg-background flex items-center justify-center">
                <div className="h-2 w-2 rounded-full bg-neon-green animate-pulse-glow" />
              </div>

              <div className="flex-1 rounded-lg border border-border bg-card/50 p-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium">
                      {entry.mode.charAt(0).toUpperCase() + entry.mode.slice(1)} Mode
                      {entry.scenario_key && ` (${entry.scenario_key})`}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Cluster {entry.cluster} • {entry.type}
                    </p>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(entry.time), 'HH:mm')}
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-muted-foreground">Score:</span>{' '}
                    <span className="text-neon-green">{entry.metrics.score.toFixed(3)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Energy:</span>{' '}
                    <span className="text-neon-blue">{entry.metrics.energy.toFixed(1)} kWh</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Quality:</span>{' '}
                    <span className="text-neon-purple">{entry.metrics.quality.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}

          {entries.length === 0 && (
            <div className="text-center text-sm text-muted-foreground py-8">
              No golden signature updates yet
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
