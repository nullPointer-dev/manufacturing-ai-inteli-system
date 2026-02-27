import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(value: number, decimals: number = 2): string {
  return value.toFixed(decimals)
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`
}

export function getHealthColor(value: number, min: number, max: number, invert: boolean = false): string {
  const normalized = (value - min) / (max - min)
  const score = invert ? 1 - normalized : normalized
  
  if (score > 0.7) return 'text-neon-green'
  if (score > 0.4) return 'text-neon-yellow'
  return 'text-neon-red'
}

export function getSeverityColor(severity: 'OK' | 'Moderate' | 'Critical'): string {
  switch (severity) {
    case 'OK':
      return 'text-neon-green'
    case 'Moderate':
      return 'text-neon-yellow'
    case 'Critical':
      return 'text-neon-red'
    default:
      return 'text-foreground'
  }
}

export function calculateROI(
  annualSavings: number,
  implementationCost: number,
  annualMaintenance: number
): { roi: number; payback: number | null; netAnnual: number } {
  const netAnnual = annualSavings - annualMaintenance
  const roi = (netAnnual / implementationCost) * 100
  const payback = netAnnual > 0 ? implementationCost / netAnnual : null
  
  return { roi, payback, netAnnual }
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}
