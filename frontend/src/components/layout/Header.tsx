import { useLocation } from 'react-router-dom'
import { Bell, Settings, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useSystemStore } from '@/store/systemStore'
import { format } from 'date-fns'

const pageTitles: Record<string, string> = {
  '/': 'Control Room Dashboard',
  '/prediction': 'Real-Time Prediction',
  '/optimization': 'Multi-Objective Optimization',
  '/golden-signature': 'Golden Signature Registry',
  '/correction': 'Real-Time Batch Correction',
  '/anomaly': 'Anomaly Detection & Reliability',
  '/governance': 'Model Governance & Drift Monitor',
}

export function Header() {
  const location = useLocation()
  const { lastUpdate } = useSystemStore()

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card/30 backdrop-blur-xl px-6">
      <div>
        <h2 className="text-xl font-bold">{pageTitles[location.pathname] || 'System'}</h2>
        {lastUpdate && (
          <p className="text-xs text-muted-foreground">
            Last updated: {format(new Date(lastUpdate), 'HH:mm:ss')}
          </p>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm">
          <Bell className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="sm">
          <Settings className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="sm">
          <User className="h-5 w-5" />
        </Button>
      </div>
    </header>
  )
}
