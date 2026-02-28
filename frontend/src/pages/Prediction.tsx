import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { predictionApi } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import type { PredictionOutput } from '@/types'

export function Prediction() {
  const [formData, setFormData] = useState({
    Batch_Size: 1000,
    Machine_Speed: 50,
    Compression_Force: 15,
    Tablet_Weight: 500,
    Friability: 0.5,
    Disintegration_Time: 5,
    avg_temperature: 25,
    avg_pressure: 1.5,
    avg_power_consumption: 50,
    total_process_time: 120,
  })

  const [prediction, setPrediction] = useState<PredictionOutput | null>(null)

  const predictMutation = useMutation({
    mutationFn: predictionApi.predict,
    onSuccess: (data) => {
      console.log('Prediction response:', data)
      setPrediction(data.prediction)
    },
    onError: (error) => {
      console.error('Prediction error:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    predictMutation.mutate(formData)
  }

  const handleInputChange = (key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [key]: parseFloat(value) || 0,
    }))
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold mb-2">Real-Time Batch Prediction</h1>
        <p className="text-muted-foreground">
          Input batch parameters to predict Quality, Yield, Performance, Energy, and CO₂ emissions
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Input Form */}
        <Card className="glass-panel">
          <CardHeader>
            <CardTitle>Batch Parameters</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(formData).map(([key, value]) => (
                  <div key={key} className="space-y-2">
                    <Label htmlFor={key} className="text-xs">
                      {key.replace(/_/g, ' ')}
                    </Label>
                    <Input
                      id={key}
                      type="number"
                      step="any"
                      value={value}
                      onChange={(e) => handleInputChange(key, e.target.value)}
                      className="h-9"
                    />
                  </div>
                ))}
              </div>

              <Button
                type="submit"
                variant="neon"
                className="w-full"
                disabled={predictMutation.isPending}
              >
                <Brain className="mr-2 h-4 w-4" />
                {predictMutation.isPending ? 'Predicting...' : 'Predict Batch Performance'}
              </Button>

              {predictMutation.isError && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400">
                  Error: {predictMutation.error instanceof Error ? predictMutation.error.message : 'Failed to predict'}
                </div>
              )}
            </form>
          </CardContent>
        </Card>

        {/* Prediction Results */}
        <AnimatePresence mode="wait">
          {prediction ? (
            <motion.div
              key="results"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4 self-start"
            >
              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle>Quality Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex flex-col items-center justify-center py-4">
                    <p className="text-sm text-muted-foreground mb-2">Overall Quality</p>
                    <p className="text-5xl font-bold">
                      {formatNumber(prediction.Quality, 2)}
                    </p>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Hardness</p>
                      <p className="text-sm font-semibold">{formatNumber(prediction.Hardness, 2)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Dissolution</p>
                      <p className="text-sm font-semibold">{formatNumber(prediction.Dissolution_Rate, 2)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Uniformity</p>
                      <p className="text-sm font-semibold">{formatNumber(prediction.Content_Uniformity, 2)}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Yield</p>
                      <p className="text-sm font-semibold">{formatNumber(prediction.Yield, 2)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Performance</p>
                      <p className="text-sm font-semibold">{formatNumber(prediction.Performance, 2)}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-panel">
                <CardHeader>
                  <CardTitle>Energy & Emissions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Energy Consumption</span>
                    <span className="text-sm font-semibold">
                      {formatNumber(prediction.Energy, 2)} kWh
                    </span>
                  </div>
                  <div className="flex justify-between items-center pt-3 border-t border-border">
                    <span className="text-sm text-muted-foreground">CO₂ Emissions</span>
                    <span className="text-sm font-semibold">
                      {formatNumber(prediction.CO2, 2)} kg
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-panel bg-primary/10 border-primary">
                <CardContent className="p-4">
                  <p className="text-sm">
                    <span className="font-semibold">AI Insight:</span> This batch configuration shows{' '}
                    {prediction.Quality > 80 ? 'excellent' : prediction.Quality > 60 ? 'good' : 'moderate'}{' '}
                    quality potential with{' '}
                    {prediction.Energy < 250 ? 'optimal' : 'elevated'} energy consumption.
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ) : (
            <motion.div
              key="placeholder"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center h-full"
            >
              <Card className="glass-panel w-full">
                <CardContent className="p-12 text-center">
                  <Brain className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                  <p className="text-muted-foreground">
                    Enter batch parameters and click Predict to see AI-powered performance forecasts
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
