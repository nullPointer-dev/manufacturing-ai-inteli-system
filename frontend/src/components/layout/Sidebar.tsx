import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Brain,
  Target,
  Award,
  Wrench,
  AlertTriangle,
  Shield,
  Activity,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Control Room' },
  { to: '/prediction', icon: Brain, label: 'Prediction' },
  { to: '/optimization', icon: Target, label: 'Optimization' },
  { to: '/golden-signature', icon: Award, label: 'Golden Signature' },
  { to: '/correction', icon: Wrench, label: 'Real-Time Correction' },
  { to: '/anomaly', icon: AlertTriangle, label: 'Anomaly & Reliability' },
  { to: '/governance', icon: Shield, label: 'Model Governance' },
]

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      className="w-64 border-r border-border bg-card/50 backdrop-blur-xl"
    >
      <div className="flex h-16 items-center gap-2 border-b border-border px-6">
        <Activity className="h-8 w-8 text-neon-blue animate-pulse-glow" />
        <div>
          <h1 className="text-lg font-bold">Manufacturing AI</h1>
          <p className="text-xs text-muted-foreground">Intelligence System</p>
        </div>
      </div>

      <nav className="space-y-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="h-5 w-5" />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="ml-auto h-2 w-2 rounded-full bg-neon-green"
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 border-t border-border bg-card/80 p-4">
        <div className="text-xs text-muted-foreground">
          <div className="mb-1 flex items-center justify-between">
            <span>System Status</span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-neon-green animate-pulse-glow" />
              Online
            </span>
          </div>
          <div className="text-[10px] opacity-50">v1.0.0 • 2026.02.27</div>
        </div>
      </div>
    </motion.aside>
  )
}
