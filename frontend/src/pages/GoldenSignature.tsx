import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Award, TrendingUp, Clock, Trash2, Archive, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { goldenApi } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import { format } from 'date-fns'

export function GoldenSignature() {
  const [view, setView] = useState<'session' | 'archive'>('session')
  const [showClearDialog, setShowClearDialog] = useState(false)
  const queryClient = useQueryClient()

  const { data: registry = {} } = useQuery({
    queryKey: ['golden-registry'],
    queryFn: goldenApi.getRegistry,
  })

  const { data: history = [] } = useQuery({
    queryKey: ['golden-history'],
    queryFn: goldenApi.getHistory,
  })

  const { data: archive = { archived_sessions: [] } } = useQuery({
    queryKey: ['golden-archive'],
    queryFn: goldenApi.getArchive,
  })

  const { data: rejectionData = { rejections: [] } } = useQuery({
    queryKey: ['rejection-history'],
    queryFn: goldenApi.getRejectionHistory,
  })

  const clearSessionMutation = useMutation({
    mutationFn: goldenApi.clearSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['golden-registry'] })
      queryClient.invalidateQueries({ queryKey: ['golden-history'] })
      queryClient.invalidateQueries({ queryKey: ['golden-archive'] })
    },
  })

  const flattenRegistry = () => {
    const entries: Array<{
      mode: string
      scenario: string
      cluster: string
      metrics: any
    }> = []

    Object.entries(registry).forEach(([mode, modeData]) => {
      if (mode === 'custom') {
        Object.entries(modeData as Record<string, any>).forEach(([scenarioKey, scenarioData]) => {
          Object.entries(scenarioData).forEach(([clusterKey, metrics]) => {
            entries.push({
              mode,
              scenario: scenarioKey,
              cluster: clusterKey,
              metrics,
            })
          })
        })
      } else {
        Object.entries(modeData as Record<string, any>).forEach(([clusterKey, metrics]) => {
          entries.push({
            mode,
            scenario: '-',
            cluster: clusterKey,
            metrics,
          })
        })
      }
    })

    return entries
  }

  const registryEntries = flattenRegistry()

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Golden Signature Registry</h1>
          <p className="text-muted-foreground">
            Session-based optimal benchmarks with historical archiving
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={view === 'session' ? 'neon' : 'outline'}
            onClick={() => setView('session')}
          >
            Current Session
          </Button>
          <Button
            variant={view === 'archive' ? 'neon' : 'outline'}
            onClick={() => setView('archive')}
          >
            <Archive className="mr-2 h-4 w-4" />
            Archive
          </Button>
          {registryEntries.length > 0 && view === 'session' && (
            <Button
              variant="destructive"
              onClick={() => setShowClearDialog(true)}
              disabled={clearSessionMutation.isPending}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {clearSessionMutation.isPending ? 'Clearing...' : 'Clear & Archive'}
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="glass-panel border-neon-green/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Signatures</p>
                <p className="text-3xl font-bold text-neon-green">{registryEntries.length}</p>
              </div>
              <Award className="h-10 w-10 text-neon-green opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-violet-500/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Modes</p>
                <p className="text-3xl font-bold text-violet-500">
                  {Object.keys(registry).length}
                </p>
              </div>
              <TrendingUp className="h-10 w-10 text-violet-500 opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-neon-purple/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Recent Updates</p>
                <p className="text-3xl font-bold text-neon-purple">
                  {history.filter((h) => {
                    const date = new Date(h.time)
                    const now = new Date()
                    const hoursDiff = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
                    return hoursDiff < 24
                  }).length}
                </p>
              </div>
              <Clock className="h-10 w-10 text-neon-purple opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel border-red-500/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Human Rejections</p>
                <p className="text-3xl font-bold text-red-400">{rejectionData.rejections.length}</p>
              </div>
              <XCircle className="h-10 w-10 text-red-400 opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Registry Table */}
      {view === 'session' && (
        <>
          <Card className="glass-panel">
            <CardHeader>
              <CardTitle>Active Golden Signatures (Current Session)</CardTitle>
            </CardHeader>
            <CardContent>
              {registryEntries.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Mode</TableHead>
                      <TableHead>Scenario</TableHead>
                      <TableHead className="text-right">Score</TableHead>
                      <TableHead className="text-right">Quality</TableHead>
                      <TableHead className="text-right">Yield</TableHead>
                      <TableHead className="text-right">Energy</TableHead>
                      <TableHead className="text-right">CO₂</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {registryEntries.map((entry, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium capitalize">{entry.mode}</TableCell>
                        <TableCell className="font-mono text-xs">{entry.scenario}</TableCell>
                        <TableCell className="text-right text-neon-green font-mono">
                          {formatNumber(entry.metrics.score, 3)}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {formatNumber(entry.metrics.quality, 2)}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {formatNumber(entry.metrics.yield, 2)}
                        </TableCell>
                        <TableCell className="text-right font-mono text-neon-yellow">
                          {formatNumber(entry.metrics.energy, 1)} kWh
                        </TableCell>
                        <TableCell className="text-right font-mono text-neon-red">
                          {formatNumber(entry.metrics.co2, 1)} kg
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No golden signatures in current session. Run optimizations to create golden benchmarks.
                </div>
              )}
            </CardContent>
          </Card>

          {/* History Timeline */}
          <Card className="glass-panel">
            <CardHeader>
              <CardTitle>Update History (Current Session)</CardTitle>
            </CardHeader>
            <CardContent>
              {history.length > 0 ? (
                <div className="space-y-3">
                  {[...history].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime()).slice(0, 10).map((entry, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="flex items-center gap-4 p-4 rounded-lg border border-border bg-card/50"
                    >
                      <div className="flex-shrink-0">
                        <div className="h-2 w-2 rounded-full bg-neon-green animate-pulse-glow" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-sm capitalize">{entry.mode}</span>
                          {entry.scenario_key && (
                            <span className="text-xs font-mono text-muted-foreground">
                              ({entry.scenario_key})
                            </span>
                          )}
                          <span
                            className={`text-xs px-2 py-0.5 rounded ${
                              entry.type === 'IMPROVED'
                                ? 'bg-neon-green/20 text-neon-green'
                                : 'bg-violet-500/20 text-violet-500'
                            }`}
                          >
                            {entry.type.toLowerCase()}
                          </span>
                        </div>
                        <div className="grid grid-cols-5 gap-3 text-xs">
                          <div>
                            <span className="text-muted-foreground">Score:</span>{' '}
                            <span className="font-mono">{formatNumber(entry.metrics.score, 3)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Quality:</span>{' '}
                            <span className="font-mono">{formatNumber(entry.metrics.quality, 2)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Yield:</span>{' '}
                            <span className="font-mono">{formatNumber(entry.metrics.yield, 2)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Energy:</span>{' '}
                            <span className="font-mono">{formatNumber(entry.metrics.energy, 1)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">CO₂:</span>{' '}
                            <span className="font-mono">{formatNumber(entry.metrics.co2, 1)}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {format(new Date(entry.time), 'MMM dd, HH:mm')}
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No update history available in current session
                </div>
              )}
            </CardContent>
          </Card>
          {/* Rejection Log */}
          {rejectionData.rejections.length > 0 && (
            <Card className="glass-panel border-red-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-400">
                  <XCircle className="h-5 w-5" />
                  Human Rejection Log
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {rejectionData.rejections.slice(0, 8).map((entry, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.04 }}
                      className="flex items-start gap-4 p-4 rounded-lg border border-red-500/20 bg-red-500/5"
                    >
                      <div className="flex-shrink-0 mt-1">
                        <div className="h-2 w-2 rounded-full bg-red-500" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-sm capitalize">{entry.mode}</span>
                          {entry.scenario_key && (
                            <span className="text-xs font-mono text-muted-foreground">({entry.scenario_key})</span>
                          )}
                          <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400">rejected</span>
                        </div>
                        <p className="text-xs text-muted-foreground mb-1">
                          Reason: <span className="text-red-300 font-medium">{entry.reason}</span>
                        </p>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                          <div><span className="text-muted-foreground">Score:</span>{' '}<span className="font-mono">{formatNumber(entry.proposed_metrics.score ?? 0, 3)}</span></div>
                          <div><span className="text-muted-foreground">Quality:</span>{' '}<span className="font-mono">{formatNumber(entry.proposed_metrics.quality ?? 0, 2)}</span></div>
                          <div><span className="text-muted-foreground">Energy:</span>{' '}<span className="font-mono">{formatNumber(entry.proposed_metrics.energy ?? 0, 1)}</span></div>
                          <div><span className="text-muted-foreground">Cluster:</span>{' '}<span className="font-mono">{entry.cluster}</span></div>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground flex-shrink-0">
                        {format(new Date(entry.time), 'MMM dd, HH:mm')}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Archive View */}
      {view === 'archive' && (
        <Card className="glass-panel">
          <CardHeader>
            <CardTitle>Archived Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {archive.archived_sessions && archive.archived_sessions.length > 0 ? (
              <div className="space-y-6">
                {archive.archived_sessions.slice().reverse().map((session: any, idx: number) => (
                  <div key={idx} className="border border-border rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-4">
                      <Archive className="h-5 w-5 text-neon-purple" />
                      <h3 className="font-semibold">Session {archive.archived_sessions.length - idx}</h3>
                      <span className="text-sm text-muted-foreground">
                        {format(new Date(session.timestamp), 'MMM dd, yyyy HH:mm')}
                      </span>
                    </div>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Mode</TableHead>
                          <TableHead>Cluster</TableHead>
                          <TableHead className="text-right">Score</TableHead>
                          <TableHead className="text-right">Quality</TableHead>
                          <TableHead className="text-right">Energy</TableHead>
                          <TableHead className="text-right">CO₂</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {Object.entries(session.golden_signatures).map(([mode, modeData]: [string, any]) => {
                          if (mode === 'custom') {
                            return Object.entries(modeData).map(([scenarioKey, scenarioData]: [string, any]) =>
                              Object.entries(scenarioData).map(([clusterKey, metrics]: [string, any]) => (
                                <TableRow key={`${mode}-${scenarioKey}-${clusterKey}`}>
                                  <TableCell className="capitalize">{mode} ({scenarioKey})</TableCell>
                                  <TableCell>{clusterKey}</TableCell>
                                  <TableCell className="text-right font-mono text-neon-green">
                                    {formatNumber(metrics.score, 3)}
                                  </TableCell>
                                  <TableCell className="text-right font-mono">
                                    {formatNumber(metrics.quality, 2)}
                                  </TableCell>
                                  <TableCell className="text-right font-mono text-neon-yellow">
                                    {formatNumber(metrics.energy, 1)}
                                  </TableCell>
                                  <TableCell className="text-right font-mono text-neon-red">
                                    {formatNumber(metrics.co2, 1)}
                                  </TableCell>
                                </TableRow>
                              ))
                            )
                          } else {
                            return Object.entries(modeData).map(([clusterKey, metrics]: [string, any]) => (
                              <TableRow key={`${mode}-${clusterKey}`}>
                                <TableCell className="capitalize">{mode}</TableCell>
                                <TableCell>{clusterKey}</TableCell>
                                <TableCell className="text-right font-mono text-neon-green">
                                  {formatNumber(metrics.score, 3)}
                                </TableCell>
                                <TableCell className="text-right font-mono">
                                  {formatNumber(metrics.quality, 2)}
                                </TableCell>
                                <TableCell className="text-right font-mono text-neon-yellow">
                                  {formatNumber(metrics.energy, 1)}
                                </TableCell>
                                <TableCell className="text-right font-mono text-neon-red">
                                  {formatNumber(metrics.co2, 1)}
                                </TableCell>
                              </TableRow>
                            ))
                          }
                        })}
                      </TableBody>
                    </Table>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No archived sessions yet. Use "Clear & Archive" to save current session.
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Clear & Archive Confirmation Dialog */}
      <Dialog
        isOpen={showClearDialog}
        onClose={() => setShowClearDialog(false)}
        title="Clear & Archive Session"
        description="Are you sure you want to clear the current session and move all golden signatures to the archive? This action cannot be undone."
        confirmText="Clear & Archive"
        cancelText="Cancel"
        variant="destructive"
        onConfirm={() => clearSessionMutation.mutate()}
      />
    </motion.div>
  )
}
