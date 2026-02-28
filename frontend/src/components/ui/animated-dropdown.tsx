import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Search } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'

interface AnimatedDropdownProps {
  value: string
  onChange: (value: string) => void
  options: Array<{ value: string; label: string }>
  placeholder?: string
  disabled?: boolean
}

export function AnimatedDropdown({
  value,
  onChange,
  options,
  placeholder = '-- Select an option --',
  disabled = false,
}: AnimatedDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)

  const filteredOptions = options.filter((option) =>
    option.label.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const selectedOption = options.find((opt) => opt.value === value)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSearchTerm('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (optionValue: string) => {
    onChange(optionValue)
    setIsOpen(false)
    setSearchTerm('')
  }

  return (
    <div ref={dropdownRef} className="relative w-full">
      {/* Dropdown Button */}
      <motion.button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className="w-full px-4 py-3 rounded-lg bg-secondary/50 border border-border focus:outline-none focus:ring-2 focus:ring-primary text-left flex items-center justify-between transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:bg-secondary/70"
        whileHover={!disabled ? { scale: 1.01 } : {}}
        whileTap={!disabled ? { scale: 0.99 } : {}}
      >
        <span className={selectedOption ? 'text-foreground' : 'text-muted-foreground'}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="h-5 w-5" />
        </motion.div>
      </motion.button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute z-50 w-full mt-2 bg-card/95 backdrop-blur-xl border border-border rounded-lg shadow-2xl overflow-hidden"
          >
            {/* Search Input */}
            <div className="p-3 border-b border-border bg-secondary/30">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search batches..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-background/50 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  autoFocus
                />
              </div>
            </div>

            {/* Options List */}
            <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
              {filteredOptions.length > 0 ? (
                <div className="p-1">
                  {filteredOptions.map((option, index) => (
                    <motion.div
                      key={option.value}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.03, duration: 0.2 }}
                    >
                      <button
                        type="button"
                        onClick={() => handleSelect(option.value)}
                        className={`w-full px-4 py-3 text-left rounded-md transition-all ${
                          option.value === value
                            ? 'bg-primary/20 text-primary font-medium'
                            : 'hover:bg-secondary/50 text-foreground'
                        }`}
                      >
                        {option.label}
                      </button>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-muted-foreground">
                  <p className="text-sm">No batches found</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
