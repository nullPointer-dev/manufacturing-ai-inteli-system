/**
 * card.tsx — enhanced with border glow that tracks the cursor.
 *
 * When a <Card> receives a className containing "glass-panel" the component
 * automatically shows a teal border glow that follows the cursor.
 *
 * All CardHeader / CardContent / etc. sub-components are unchanged.
 */

import * as React from 'react'
import { useRef, useEffect } from 'react'
import { gsap } from 'gsap'
import { cn } from '@/lib/utils'

// ─── teal accent that matches the dashboard neon theme ───────────────────────
const GLOW = '20, 184, 166'

// ─── merge multiple refs onto one DOM element ────────────────────────────────
const mergeRefs = <T,>(...refs: React.Ref<T>[]) =>
  (el: T | null) =>
    refs.forEach(r => {
      if (typeof r === 'function') r(el)
      else if (r) (r as React.MutableRefObject<T | null>).current = el
    })

// ─── attach border glow effect to a div ref (only when isMagic is true) ──────
const useMagicEffects = (
  innerRef: React.RefObject<HTMLDivElement | null>,
  isMagic: boolean
) => {
  useEffect(() => {
    const el = innerRef.current
    if (!el || !isMagic) return

    el.style.position = 'relative'
    el.style.setProperty('--glow-x', '50%')
    el.style.setProperty('--glow-y', '50%')
    el.style.setProperty('--glow-intensity', '0')

    // Border glow inset layer
    const glowEl = document.createElement('div')
    glowEl.dataset.magicGlow = '1'
    glowEl.style.cssText = `
      position:absolute;inset:0;border-radius:inherit;
      padding:1px;pointer-events:none;z-index:1;
      background:radial-gradient(
        220px circle at var(--glow-x) var(--glow-y),
        rgba(${GLOW}, calc(var(--glow-intensity) * 0.65)) 0%,
        rgba(${GLOW}, calc(var(--glow-intensity) * 0.25)) 40%,
        transparent 70%
      );
      -webkit-mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite:xor;
      mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      mask-composite:exclude;
    `
    el.appendChild(glowEl)

    const onMove = (e: MouseEvent) => {
      const r = el.getBoundingClientRect()
      el.style.setProperty('--glow-x', `${e.clientX - r.left}px`)
      el.style.setProperty('--glow-y', `${e.clientY - r.top}px`)
      gsap.to(el, { '--glow-intensity': 1, duration: 0.3, ease: 'power2.out' })
    }

    const onLeave = () => {
      gsap.to(el, { '--glow-intensity': 0, duration: 0.4 })
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)

    return () => {
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
      glowEl.parentNode?.removeChild(glowEl)
    }
  }, [innerRef, isMagic])
}

// ─── Card ─────────────────────────────────────────────────────────────────────
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    const innerRef = useRef<HTMLDivElement>(null)
    useMagicEffects(innerRef, Boolean(className?.includes('glass-panel')))

    return (
      <div
        ref={mergeRefs(innerRef, ref)}
        className={cn('rounded-lg border bg-card text-card-foreground shadow-sm', className)}
        {...props}
      />
    )
  }
)
Card.displayName = 'Card'

// ─── sub-components (unchanged) ───────────────────────────────────────────────
const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />
  )
)
CardHeader.displayName = 'CardHeader'

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn('text-2xl font-semibold leading-none tracking-tight', className)} {...props} />
  )
)
CardTitle.displayName = 'CardTitle'

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn('text-sm text-muted-foreground', className)} {...props} />
  )
)
CardDescription.displayName = 'CardDescription'

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
  )
)
CardContent.displayName = 'CardContent'

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex items-center p-6 pt-0', className)} {...props} />
  )
)
CardFooter.displayName = 'CardFooter'

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
