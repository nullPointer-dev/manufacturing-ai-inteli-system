# External UI Assets Library

This folder contains all external frontend assets (text effects, background effects, and interactive components) used in the Clash Royale Deck Analyzer project.

**Created:** February 27, 2026  
**Source:** `frontend/src/components/ui/`  
**Total Components:** 13

---

## 📋 Component Inventory

### Text Effects

#### 1. **AnimatedShinyText.tsx**
- **Purpose:** Animated shimmering text effect
- **Features:** Configurable shimmer width, custom styling
- **Use Case:** Highlighting important text with subtle animation
- **Props:** `children`, `className`, `shimmerWidth`

#### 2. **AuroraText.tsx**
- **Purpose:** Gradient text with aurora-like color transitions
- **Features:** Blue → Purple → Pink gradient, pulse animation
- **Use Case:** Eye-catching headings and call-to-action text
- **Props:** `children`, `className`

#### 3. **MorphingText.tsx**
- **Purpose:** Text morphing/transformation animation
- **Features:** Smooth transitions between text states
- **Use Case:** Dynamic text changes, rotating messages
- **Props:** Varies based on implementation

#### 4. **ShinyText.tsx**
- **Purpose:** Text with metallic/shiny appearance
- **Features:** Reflective shine effect
- **Use Case:** Premium features, special badges
- **Props:** `children`, `className`

#### 5. **TextType.tsx**
- **Purpose:** Typewriter effect for text
- **Features:** Character-by-character typing animation
- **Use Case:** Hero section on home page ("Build [Powerful/Strategic/...] Decks")
- **Props:** Text array, speed, loop settings

---

### Background Effects

#### 6. **Aurora.tsx**
- **Purpose:** WebGL-based aurora borealis background effect
- **Technology:** OGL (WebGL library)
- **Features:** 
  - GLSL shaders (vertex + fragment)
  - Simplex noise for organic movement
  - 3-color gradient system
  - Time-based animation
  - Responsive to screen resolution
- **Performance:** GPU-accelerated
- **Use Case:** Immersive background for hero sections
- **Shaders:** Custom GLSL with 212 lines of code

#### 7. **Particles.tsx**
- **Purpose:** 3D particle system background
- **Technology:** OGL (OpenGL wrapper)
- **Features:**
  - Configurable particle count, spread, speed
  - Custom colors and sizes
  - Camera distance control
  - WebGL-rendered
- **Use Case:** 
  - Home page background
  - Deck builder page backdrop
- **Performance:** Optimized for 60fps

#### 8. **RippleGrid.tsx**
- **Purpose:** Grid with interactive ripple effects
- **Features:** Responsive grid, mouse interaction
- **Use Case:** Interactive backgrounds, section dividers
- **Props:** Grid configuration, ripple settings

---

### Interactive Components

#### 9. **InteractiveHoverButton.tsx**
- **Purpose:** Button with advanced hover interactions
- **Features:**
  - Smooth hover transitions
  - Custom animations
  - Visual feedback
- **Use Case:** Primary CTA buttons, important actions
- **Props:** `children`, `className`, hover config

#### 10. **PillNav.tsx**
- **Purpose:** Pill-shaped navigation component
- **Features:**
  - Smooth tab switching
  - Active state indicator
  - Rounded pill design
- **Use Case:** Navigation menus, tab selectors
- **Props:** Navigation items, active state

#### 11. **Shuffle.tsx**
- **Purpose:** Card shuffle animation effect
- **Features:** Smooth card transitions, stacking effects
- **Use Case:** Animated card displays, feature showcases
- **Props:** Animation timing, card content

---

### Card/Container Effects

#### 12. **SpotlightCard.tsx**
- **Purpose:** Card component with spotlight hover effect
- **Features:**
  - Gradient spotlight follows cursor
  - Smooth lighting transitions
  - 3D depth effect
- **Use Case:** Feature cards, deck cards, highlight boxes
- **Props:** `children`, `className`, spotlight config

#### 13. **StarBorder.tsx**
- **Purpose:** Animated star/sparkle border effect
- **Features:**
  - Animated border particles
  - Customizable colors
  - Smooth animations
- **Use Case:** Premium cards, special features, badges
- **Props:** `children`, `className`, animation settings

---

## 🎨 Technology Stack

### Core Technologies
- **React 18.3.0** - Component framework
- **TypeScript 5** - Type safety
- **Tailwind CSS 3.4.0** - Utility styling
- **Framer Motion 11.0.0** - Animation library
- **GSAP 3.13.0** - Advanced animations

### WebGL/3D
- **OGL** - Lightweight WebGL library
- **GLSL Shaders** - Custom vertex/fragment shaders
- **GPU Acceleration** - Hardware-accelerated rendering

---

## 📊 Usage Statistics

### Component Usage in Project

**Home Page (`src/app/page.tsx`):**
- TextType (hero typewriter)
- Particles (3D background)
- SpotlightCard (feature cards)
- AuroraText (gradient headings)

**Deck Builder (`src/app/deck-builder/page.tsx`):**
- Particles (animated background)
- SpotlightCard (deck cards)
- InteractiveHoverButton (analyze button)

**General UI:**
- ShinyText (badges, premium labels)
- StarBorder (special highlights)
- PillNav (navigation)

---

## 🔧 Integration Notes

### Dependencies
All components require:
```json
{
  "react": "^18.3.0",
  "typescript": "^5",
  "tailwindcss": "^3.4.0"
}
```

### OGL Components Require:
```json
{
  "ogl": "latest"
}
```

### Import Paths
Original project imports:
```typescript
import { Particles } from '@/components/ui/Particles';
import { TextType } from '@/components/ui/TextType';
```

### Client-Side Only
All components use `'use client'` directive (Next.js 14 requirement)

---

## 🚀 Performance Characteristics

### Lightweight Components
- AnimatedShinyText: ~30 lines, CSS-only
- AuroraText: ~20 lines, CSS gradients
- ShinyText: ~40 lines, CSS effects

### Medium Weight
- InteractiveHoverButton: ~100 lines
- SpotlightCard: ~150 lines
- TextType: ~80 lines

### Heavy Components (GPU-intensive)
- **Aurora.tsx**: 212 lines, WebGL shaders, GPU-rendered
- **Particles.tsx**: 200+ lines, 3D particle system
- RippleGrid: ~150 lines, Canvas-based

### Optimization Tips
1. Use Particles/Aurora sparingly (1-2 per page)
2. Lazy-load heavy components
3. Consider disabling on mobile for performance
4. Use CSS-only effects when possible

---

## 📝 Customization Guide

### Color Schemes
Most components support Tailwind classes:
```typescript
<AuroraText className="text-blue-600" />
<SpotlightCard className="bg-gray-900" />
```

### Animation Timing
Adjustable via props or Tailwind utilities:
```typescript
<TextType speed={50} />
<Shuffle duration="animate-[duration-300]" />
```

### WebGL Config
Aurora and Particles accept configuration objects for colors, amplitudes, particle counts, etc.

---

## 🎯 Use Case Recommendations

### Landing Pages
- **Hero Section:** TextType + Particles/Aurora
- **Features:** SpotlightCard grid
- **CTAs:** InteractiveHoverButton

### Interactive Pages
- **Backgrounds:** Particles (less intensive than Aurora)
- **Cards:** SpotlightCard with StarBorder
- **Navigation:** PillNav

### Text Emphasis
- **Headings:** AuroraText, ShinyText
- **Subtext:** AnimatedShinyText
- **Dynamic Text:** MorphingText, TextType

---

## 🔍 Code Quality

### Type Safety
- All components fully TypeScript-typed
- Proper interface definitions
- React.FC or explicit return types

### Accessibility
- Semantic HTML
- Keyboard navigation support (where applicable)
- ARIA labels (where needed)

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- WebGL 2.0 required for Aurora/Particles
- Fallbacks recommended for older browsers

---

## 📦 Backup Information

**Backup Date:** February 27, 2026  
**Original Location:** `frontend/src/components/ui/`  
**Backup Location:** `external_ui_assets/`  
**Files Backed Up:** 13 TypeScript React components  
**Total Size:** ~3,000 lines of code

---

## 🔗 Related Documentation

- **Main Project Docs:** `PROJECT_STRUCTURE_DOCUMENTATION.md`
- **Frontend Readme:** `frontend/README.md`
- **Component Usage:** Check `frontend/src/app/` for live examples

---

## ⚠️ Important Notes

1. **License:** Verify licensing if reusing in other projects
2. **Attribution:** Some effects may be adapted from open-source libraries
3. **Performance:** Test on target devices before deploying multiple GPU-intensive effects
4. **Updates:** These are snapshots; original files in `frontend/src/components/ui/` may be updated

---

## 🛠️ Maintenance

### To Update This Backup
```powershell
Copy-Item -Path "frontend\src\components\ui\*.tsx" -Destination "external_ui_assets\" -Force
```

### To Restore Components
```powershell
Copy-Item -Path "external_ui_assets\*.tsx" -Destination "frontend\src\components\ui\" -Force
```

---

**END OF DOCUMENTATION**
