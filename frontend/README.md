# Manufacturing AI Intelligence System - Frontend

## 🚀 Production-Grade React Frontend

Enterprise-level control room UI for AI-driven manufacturing optimization with real-time batch intelligence, multi-objective optimization, and adaptive golden signature management.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Components**: Shadcn/ui + Radix UI
- **Styling**: Tailwind CSS
- **Data Visualization**: Recharts + Plotly.js
- **State Management**: Zustand + React Query
- **Animations**: Framer Motion
- **API Client**: Axios

## Features

### 📊 Control Room Dashboard
- Real-time KPI monitoring (Quality, Yield, Performance, Energy, CO₂)
- Animated metric cards with health indicators
- Golden signature update timeline
- System status overview
- Production performance gauges

### 🧠 Real-Time Prediction
- Multi-target batch prediction
- Quality, Yield, Performance forecasting
- Energy consumption & CO₂ emission estimation
- Interactive parameter input
- Animated result visualization

### 🎯 Multi-Objective Optimization
- NSGA-II optimization engine
- 5 preset scenarios + custom weights
- Automatic & target-based strategies
- Golden signature proposal workflow (approve/reject)
- Pareto frontier visualization
- Real-time parameter configuration

### 🏆 Golden Signature Registry
- Multi-mode signature management
- Custom scenario isolation
- Cluster-aware benchmarking
- Historical update timeline
- Score comparison visualization

### 🔧 Real-Time Batch Correction
- Parameter drift detection
- Severity classification (OK/Moderate/Critical)
- Correction suggestions
- Impact estimation

### ⚠️ Anomaly Detection & Reliability
- Isolation Forest analysis
- Energy pattern intelligence
- Asset reliability monitoring
- Drift indicators

### 🛡️ Model Governance
- Model versioning & history
- Drift detection & retraining
- Performance metrics tracking (MAE, RMSE, MAPE)
- Feature importance visualization
- Continuous learning management

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Setup

The frontend expects the backend API to be available at `http://localhost:8000`. This is configured in `vite.config.ts` as a proxy.

If your backend runs on a different port, update the proxy configuration:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:YOUR_PORT',
      changeOrigin: true,
    },
  },
}
```

## Project Structure

```
src/
├── components/
│   ├── dashboard/          # Dashboard-specific components
│   │   ├── MetricCard.tsx
│   │   ├── Gauge.tsx
│   │   └── GoldenTimeline.tsx
│   ├── layout/             # Layout components
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   └── ui/                 # Base UI components (Shadcn/ui)
├── pages/                  # Main application pages
│   ├── Dashboard.tsx
│   ├── Prediction.tsx
│   ├── Optimization.tsx
│   ├── GoldenSignature.tsx
│   ├── Correction.tsx
│   ├── Anomaly.tsx
│   └── Governance.tsx
├── store/                  # Zustand stores
│   ├── optimizationStore.ts
│   └── systemStore.ts
├── lib/                    # Utilities & API
│   ├── api.ts
│   └── utils.ts
├── types/                  # TypeScript types
│   └── index.ts
├── App.tsx                 # Main app component
└── main.tsx               # Entry point
```

## API Integration

The frontend integrates with the following backend endpoints:

- `POST /api/predict` - Real-time batch prediction
- `POST /api/optimize_auto` - Automatic optimization
- `POST /api/optimize_target` - Target-based optimization
- `POST /api/accept_golden` - Accept golden signature update
- `GET /api/golden` - Get golden registry
- `GET /api/golden_history` - Get golden update history
- `GET /api/model_history` - Get model version history
- `POST /api/check_retrain` - Check drift & retrain
- `GET /api/feature_importance` - Get feature importance
- `GET /api/system_status` - Get system status

## Key Features Explained

### Golden Signature Workflow

1. Run optimization in any mode (balanced, eco, quality, etc.)
2. If the solution exceeds current golden benchmark by >1%, a proposal appears
3. User can **Approve** (updates registry) or **Reject** (keeps current golden)
4. All decisions are logged in golden history
5. Human-in-the-loop workflow for continuous improvement

### Custom Scenario Support

- Mode: `custom`
- Define custom weights via sliders
- System generates unique `scenario_key` (MD5 hash)
- Separate golden signatures per custom scenario
- Full isolation from preset modes

### Context-Aware Optimization

- Backend clusters batches by operational context
- Separate golden signatures per cluster
- Optimization respects cluster boundaries
- Dynamic adaptation to production regimes

## Dark Mode Industrial Theme

The UI features a dark industrial control room aesthetic with:

- Neon accent colors (blue, green, yellow, red, purple)
- Glass-morphism panels with backdrop blur
- Animated metric counters
- Smooth page transitions (Framer Motion)
- Grid background overlay
- Custom scrollbars
- Shadow glows on critical metrics

## Development Guidelines

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation item in `Sidebar.tsx`
4. Update page title mapping in `Header.tsx`

### Creating Reusable Components

- Use Shadcn/ui patterns
- Implement with TypeScript interfaces
- Add Framer Motion animations
- Follow glass-panel styling

### State Management

- **Local state**: `useState` for component-specific data
- **Global UI state**: Zustand stores
- **Server state**: React Query hooks
- **Form state**: React Hook Form (if needed)

## Performance Optimization

- React Query caching with 30s stale time
- Lazy loading for heavy visualizations
- Debounced input handlers
- Optimistic UI updates
- Code splitting by route

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Modern browsers with ES2020 support

## Deployment

```bash
# Build for production
npm run build

# Output will be in /dist folder
# Deploy /dist to any static hosting service
```

Recommended hosting:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Azure Static Web Apps

## Contributing

1. Follow TypeScript strict mode
2. Use functional components
3. Implement proper error boundaries
4. Add loading states for async operations
5. Maintain responsive design
6. Test on multiple screen sizes

## License

Proprietary - Manufacturing AI Intelligence System

## Support

For technical support or feature requests, contact the development team.

---

**Built for Industrial AI Excellence** 🏭⚡
