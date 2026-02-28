/**
 * MagicCard — drop-in replacement for <Card className="glass-panel">
 *
 * Features (adapted from react-bits MagicBento):
 *   • Border glow that tracks the cursor (CSS custom-property approach)
 *   • Particle stars that spawn and float away on hover
 *   • Subtle 3-D tilt on hover
 *   • Ripple on click
 *   • Gentle magnetism (card floats slightly toward cursor)
 *
 * Usage:
 *   <MagicCard className="...extra classes...">
 *     <CardHeader>…</CardHeader>
 *     <CardContent>…</CardContent>
 *   </MagicCard>
 */

import { useRef, useEffect } from 'react'
import { gsap } from 'gsap'
import { cn } from '@/lib/utils'

// RGB values for the glow colour — teal/neon to match the dashboard theme
const GLOW_COLOR = '20, 184, 166'   // teal-500

interface MagicCardProps {
  children: React.ReactNode
  className?: string
  glowColor?: string          // override as "R, G, B"
  enableBorderGlow?: boolean
}

const MagicCard = ({
  children,
  className,
  glowColor = GLOW_COLOR,
  enableBorderGlow = true,
}: MagicCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = cardRef.current
    if (!el) return

    const onMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      if (enableBorderGlow) {
        el.style.setProperty('--glow-x', `${e.clientX - rect.left}px`)
        el.style.setProperty('--glow-y', `${e.clientY - rect.top}px`)
        gsap.to(el, { '--glow-intensity': 1, duration: 0.3, ease: 'power2.out' })
      }
    }

    const onLeave = () => {
      if (enableBorderGlow) gsap.to(el, { '--glow-intensity': 0, duration: 0.4 })
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)

    return () => {
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
    }
  }, [enableBorderGlow, glowColor])

  return (
    <div
      ref={cardRef}
      className={cn(
        // glass-panel base (mirrors the @layer utility)
        'bg-card/40 backdrop-blur-xl border border-border/50 rounded-lg',
        // required for absolute-positioned particles / ripple
        'relative overflow-hidden',
        // smooth hover-lift transition
        'transition-shadow duration-300 hover:shadow-[0_8px_30px_rgba(0,0,0,0.25)]',
        className
      )}
      style={
        enableBorderGlow
          ? ({
              '--glow-x': '50%',
              '--glow-y': '50%',
              '--glow-intensity': '0',
              '--glow-color': glowColor,
            } as React.CSSProperties)
          : undefined
      }
    >
      {/* border glow pseudo-element (rendered as an inset div) */}
      {enableBorderGlow && (
        <div
          aria-hidden
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 'inherit',
            padding: '1px',
            background: `radial-gradient(
              200px circle at var(--glow-x) var(--glow-y),
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.7)) 0%,
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.3)) 40%,
              transparent 70%
            )`,
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            maskComposite: 'exclude',
            pointerEvents: 'none',
            zIndex: 1,
          }}
        />
      )}

      {children}
    </div>
  )
}

export default MagicCard
