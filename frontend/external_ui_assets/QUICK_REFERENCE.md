# Quick Component Reference Guide

## 🎯 Choose the Right Effect

### Need Text Animation?
```
Simple shine effect → AnimatedShinyText.tsx
Gradient glow → AuroraText.tsx
Metallic look → ShinyText.tsx
Typewriter effect → TextType.tsx
Text morphing → MorphingText.tsx
```

### Need Background Effect?
```
Aurora waves (heavy) → Aurora.tsx (212 lines, WebGL)
Floating particles → Particles.tsx (7.5KB, 3D)
Interactive grid → RippleGrid.tsx (9.8KB, Canvas)
```

### Need Button/Interactive Element?
```
Fancy button → InteractiveHoverButton.tsx
Navigation tabs → PillNav.tsx (16KB)
```

### Need Card/Container Effect?
```
Spotlight glow → SpotlightCard.tsx
Sparkle border → StarBorder.tsx
Card shuffle → Shuffle.tsx
```

---

## 📊 Performance Impact

### Lightweight (Use freely)
- ✅ AnimatedShinyText
- ✅ AuroraText 
- ✅ ShinyText
- ✅ TextType

### Medium (Use 2-3 per page)
- ⚠️ InteractiveHoverButton
- ⚠️ SpotlightCard
- ⚠️ StarBorder
- ⚠️ Shuffle

### Heavy (Use 1 per page max)
- 🔴 Aurora (WebGL shaders)
- 🔴 Particles (3D rendering)
- 🔴 RippleGrid (Canvas animation)

---

## 🎨 Typical Combinations

### Landing Hero Section
```typescript
<div className="relative">
  <Particles /> {/* Background */}
  <h1><TextType words={["Powerful", "Strategic"]} /></h1>
  <p><AuroraText>Premium Features</AuroraText></p>
  <InteractiveHoverButton>Get Started</InteractiveHoverButton>
</div>
```

### Feature Card Grid
```typescript
<SpotlightCard>
  <StarBorder>
    <h3><ShinyText>Premium</ShinyText></h3>
    <p><AnimatedShinyText>Advanced analytics</AnimatedShinyText></p>
  </StarBorder>
</SpotlightCard>
```

### Navigation
```typescript
<PillNav items={["Home", "Builder", "Cards"]} />
```

---

## 📁 File Size Reference

| Component | Size | Complexity |
|-----------|------|------------|
| PillNav.tsx | 16 KB | High |
| RippleGrid.tsx | 9.8 KB | High |
| Particles.tsx | 7.5 KB | High |
| Aurora.tsx | 6.1 KB | Very High |
| TextType.tsx | 5.6 KB | Medium |
| SpotlightCard.tsx | 1.9 KB | Low |
| StarBorder.tsx | 1.7 KB | Low |
| Shuffle.tsx | 1.7 KB | Medium |
| InteractiveHoverButton.tsx | 870 B | Low |
| ShinyText.tsx | 800 B | Low |
| MorphingText.tsx | 632 B | Low |
| AnimatedShinyText.tsx | 528 B | Very Low |
| AuroraText.tsx | 439 B | Very Low |

---

## 🚀 Quick Start

1. **Copy component** to your project
2. **Install dependencies**: `npm install ogl` (for Aurora/Particles)
3. **Add 'use client'** directive (if Next.js)
4. **Import and use**:
   ```typescript
   import { Particles } from './path/to/Particles';
   ```

---

## ⚡ Performance Tips

1. **Lazy load heavy components**:
   ```typescript
   const Particles = dynamic(() => import('@/components/ui/Particles'), { ssr: false });
   ```

2. **Disable on mobile**:
   ```typescript
   {!isMobile && <Particles />}
   ```

3. **Use CSS alternatives** when possible:
   - Instead of Aurora → CSS gradients
   - Instead of Particles → CSS animations
   - Instead of RippleGrid → CSS hover effects

---

## 🔗 Dependencies

### All Components
- `react@^18.3.0`
- `typescript@^5`
- `tailwindcss@^3.4.0`

### Aurora + Particles Only
- `ogl` (WebGL library)

### Optional
- `framer-motion` (enhanced animations)
- `gsap` (timeline animations)

---

**Last Updated:** February 27, 2026
