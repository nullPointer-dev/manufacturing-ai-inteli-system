import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function NotFound() {
  const navigate = useNavigate()
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center min-h-[60vh] gap-6 text-center"
    >
      <h1 className="text-8xl font-bold text-teal-500/30">404</h1>
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Page not found</h2>
        <p className="text-muted-foreground">
          The page you are looking for does not exist.
        </p>
      </div>
      <Button variant="neon" onClick={() => navigate('/')}>
        <Home className="mr-2 h-4 w-4" />
        Back to Dashboard
      </Button>
    </motion.div>
  )
}
