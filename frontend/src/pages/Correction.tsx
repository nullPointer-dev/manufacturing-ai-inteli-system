import { motion } from 'framer-motion'
import { AlertTriangle, Wrench, AlertCircle, CheckCircle, TrendingDown, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AnimatedDropdown } from '@/components/ui/animated-dropdown'
import { useState, useEffect } from 'react'
import { correctionApi } from '@/lib/api'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface Batch {
  Batch_ID: string
  Quality_Score: number
  Yield_Percentage: number
  Performance_Index: number
}

interface AnalysisResult {
  Parameter: string
  Current: number
  'Golden Mean': number
  'Drift (σ)': number
  Severity: string
  Suggestion: string
  'Predicted Impact': number
  Beneficial?: boolean
}

export function Correction() {
  const [batches, setBatches] = useState<Batch[]>([])
  const [selectedBatch, setSelectedBatch] = useState<string>('')
  const [analysis, setAnalysis] = useState<AnalysisResult[] | null>(null)
  const [batchInfo, setBatchInfo] = useState<any>(null)
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [batchesLoading, setBatchesLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadBatches()
  }, [])

  const loadBatches = async () => {
    try {
      setBatchesLoading(true)
      setError(null)
      const response = await correctionApi.getBatches()
      console.log('Batches response:', response)
      console.log('Number of batches:', response.batches?.length)
      setBatches(response.batches)
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || err?.message || 'Failed to load batches'
      setError(errorMsg)
      console.error('Error loading batches:', err)
      console.error('Error details:', errorMsg)
    } finally {
      setBatchesLoading(false)
    }
  }

  const analyzeBatch = async (batchId: string) => {
    if (!batchId) return
    
    setLoading(true)
    setError(null)
    setAnalysis(null)
    
    try {
      const response = await correctionApi.analyzeBatch(batchId)
      
      if (response.status === 'error') {
        setError('Analysis failed')
        return
      }
      
      setAnalysis(response.analysis)
      setBatchInfo(response.batch_info)
      setSummary(response.summary)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to analyze batch')
      console.error('Error analyzing batch:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleBatchChange = (batchId: string) => {
    setSelectedBatch(batchId)
    if (batchId) {
      analyzeBatch(batchId)
    } else {
      setAnalysis(null)
      setBatchInfo(null)
      setSummary(null)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical':
        return 'text-red-500'
      case 'Moderate':
        return 'text-yellow-500'
      case 'OK':
        return 'text-green-500'
      default:
        return 'text-gray-500'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'Critical':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'Moderate':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'OK':
        return <CheckCircle className="h-4 w-4 text-green-500" />
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
        <h1 className="text-3xl font-bold mb-2">Real-Time Batch Correction</h1>
        <p className="text-muted-foreground">
          Compare batch parameters against golden ranges and receive correction suggestions
        </p>
      </div>

      {/* Batch Selection */}
      <Card className="glass-panel min-h-[320px]">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">Select Batch for Analysis</CardTitle>
        </CardHeader>
        <CardContent className="pb-8">
          <div className="space-y-6">
            <AnimatedDropdown
              value={selectedBatch}
              onChange={handleBatchChange}
              options={batches.map((batch) => ({
                value: batch.Batch_ID,
                label: `Batch ${batch.Batch_ID} (Quality: ${batch.Quality_Score.toFixed(2)})`,
              }))}
              placeholder="-- Select a Batch --"
              disabled={loading}
              loading={batchesLoading}
            />
            {loading && (
              <div className="text-center">
                <span className="text-sm text-muted-foreground">Analyzing batch...</span>
              </div>
            )}
          </div>
          
          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
              <p className="text-red-500 text-sm">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Batch Info Summary */}
      {batchInfo && summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glass-panel">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">Quality Score</p>
                <p className="text-2xl font-bold">{batchInfo.quality?.toFixed(2)}</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="glass-panel">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">Drift Analysis</p>
                <div className="flex justify-center gap-2 mt-2">
                  <div className="text-center">
                    <p className="text-lg font-bold text-red-500">{summary.critical}</p>
                    <p className="text-xs text-muted-foreground">Critical</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-yellow-500">{summary.moderate}</p>
                    <p className="text-xs text-muted-foreground">Moderate</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-green-500">{summary.ok}</p>
                    <p className="text-xs text-muted-foreground">OK</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="glass-panel">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">Energy</p>
                <p className="text-2xl font-bold">{batchInfo.energy?.toFixed(0)} kWh</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="glass-panel">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-1">CO2</p>
                <p className="text-2xl font-bold">{batchInfo.co2?.toFixed(0)} kg</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Parameter Drift Analysis */}
      {analysis && analysis.length > 0 && (
        <Card className="glass-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wrench className="h-5 w-5" />
              Parameter Drift Analysis & Correction Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-border overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-secondary/50">
                    <TableHead>Status</TableHead>
                    <TableHead>Parameter</TableHead>
                    <TableHead className="text-right">Current</TableHead>
                    <TableHead className="text-right">Golden Mean</TableHead>
                    <TableHead className="text-right">Drift (σ)</TableHead>
                    <TableHead>Suggestion</TableHead>
                    <TableHead className="text-right">Impact</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {analysis
                    .sort((a, b) => {
                      const severityOrder = { Critical: 0, Moderate: 1, OK: 2 }
                      const rankA = severityOrder[a.Severity as keyof typeof severityOrder] ?? 3
                      const rankB = severityOrder[b.Severity as keyof typeof severityOrder] ?? 3
                      if (rankA !== rankB) return rankA - rankB
                      return Math.abs(b['Drift (σ)']) - Math.abs(a['Drift (σ)'])
                    })
                    .map((row, idx) => (
                      <TableRow key={idx} className="hover:bg-secondary/30">
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getSeverityIcon(row.Severity)}
                            <span className={`text-xs font-medium ${getSeverityColor(row.Severity)}`}>
                              {row.Severity}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="font-medium">{row.Parameter}</TableCell>
                        <TableCell className="text-right font-mono">{row.Current.toFixed(2)}</TableCell>
                        <TableCell className="text-right font-mono text-primary">{row['Golden Mean'].toFixed(2)}</TableCell>
                        <TableCell className="text-right">
                          <span className={`font-mono ${getSeverityColor(row.Severity)}`}>
                            {row['Drift (σ)'].toFixed(2)}σ
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {row.Beneficial === false ? (
                              <AlertTriangle className="h-4 w-4 text-yellow-500 shrink-0" />
                            ) : row.Current > row['Golden Mean'] ? (
                              <TrendingDown className="h-4 w-4 text-blue-500 shrink-0" />
                            ) : row.Current < row['Golden Mean'] ? (
                              <TrendingUp className="h-4 w-4 text-blue-500 shrink-0" />
                            ) : null}
                            <span className={`text-sm ${row.Beneficial === false ? 'text-yellow-500/80 italic' : ''}`}>
                              {row.Suggestion}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <span className={`font-mono text-sm ${
                            row['Predicted Impact'] > 0 ? 'text-green-500' : 
                            row['Predicted Impact'] < 0 ? 'text-red-500' : 
                            'text-gray-500'
                          }`}>
                            {row['Predicted Impact'] !== 0 
                              ? `${row['Predicted Impact'] > 0 ? '+' : ''}${row['Predicted Impact'].toFixed(3)}`
                              : 'N/A'
                            }
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Analysis State */}
      {!analysis && !loading && selectedBatch && (
        <Card className="glass-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wrench className="h-5 w-5" />
              Parameter Drift Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <AlertTriangle className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <p>Select a batch to see parameter drift analysis</p>
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  )
}

