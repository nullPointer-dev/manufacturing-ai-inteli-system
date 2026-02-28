import { ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { Button } from './button'

interface DialogProps {
  isOpen: boolean
  onClose: () => void
  title: string
  description?: string
  children?: ReactNode
  confirmText?: string
  cancelText?: string
  onConfirm?: () => void
  variant?: 'default' | 'destructive'
}

export function Dialog({
  isOpen,
  onClose,
  title,
  description,
  children,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  variant = 'default',
}: DialogProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Dialog */}
          <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ type: 'spring', duration: 0.3 }}
              className="glass-panel border-neon-purple/30 rounded-lg shadow-2xl w-full max-w-md mx-4 pointer-events-auto"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-border/50">
                <h2 className="text-xl font-semibold">{title}</h2>
                <button
                  onClick={onClose}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6">
                {description && (
                  <p className="text-muted-foreground mb-4">{description}</p>
                )}
                {children}
              </div>

              {/* Footer */}
              {onConfirm && (
                <div className="flex items-center justify-end gap-3 p-6 border-t border-border/50">
                  <Button variant="outline" onClick={onClose}>
                    {cancelText}
                  </Button>
                  <Button
                    variant={variant === 'destructive' ? 'destructive' : 'neon'}
                    onClick={() => {
                      onConfirm()
                      onClose()
                    }}
                  >
                    {confirmText}
                  </Button>
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
