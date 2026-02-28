import { ReactNode, useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Info } from 'lucide-react'

interface TooltipProps {
  content: string
  children?: ReactNode
  showIcon?: boolean
}

export function Tooltip({ content, children, showIcon = true }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const iconRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isVisible && iconRef.current) {
      const rect = iconRef.current.getBoundingClientRect()
      setPosition({
        top: rect.top - 8, // 8px above the icon
        left: rect.left + rect.width / 2,
      })
    }
  }, [isVisible])

  const handleMouseEnter = () => setIsVisible(true)
  const handleMouseLeave = () => setIsVisible(false)

  return (
    <>
      <div
        ref={iconRef}
        className="inline-flex items-center flex-shrink-0 cursor-help"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {children || (
          showIcon && (
            <Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors flex-shrink-0" />
          )
        )}
      </div>

      {isVisible &&
        createPortal(
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, y: 5, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 5, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="fixed z-[9999] pointer-events-none"
              style={{
                top: `${position.top}px`,
                left: `${position.left}px`,
                transform: 'translateX(-50%)',
              }}
            >
              <div className="bg-gray-950/95 backdrop-blur-sm border border-teal-500/50 px-4 py-3 rounded-lg shadow-2xl max-w-xs whitespace-normal">
                <p className="text-xs text-gray-100 leading-relaxed">{content}</p>
                <div
                  className="absolute"
                  style={{
                    bottom: '-5px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                  }}
                >
                  <div className="w-0 h-0 border-l-[5px] border-r-[5px] border-t-[5px] border-l-transparent border-r-transparent border-t-gray-950/95" />
                </div>
              </div>
            </motion.div>
          </AnimatePresence>,
          document.body
        )}
    </>
  )
}
