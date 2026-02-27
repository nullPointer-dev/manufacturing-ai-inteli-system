import { motion } from 'framer-motion'
import { AlertTriangle, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function Anomaly() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold mb-2">Anomaly Detection & Reliability</h1>
        <p className="text-muted-foreground">
          Energy pattern analysis and asset reliability monitoring
        </p>
      </div>

      <Card className="glass-panel">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Reliability State Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="py-12">
          <div className="text-center text-muted-foreground">
            <AlertTriangle className="h-16 w-16 mx-auto mb-4 opacity-50" />
            <p>Anomaly detection and energy intelligence module</p>
            <p className="text-sm mt-2">Isolation Forest analysis and reliability scoring</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
