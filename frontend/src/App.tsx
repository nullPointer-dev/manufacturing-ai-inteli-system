import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import { Dashboard } from '@/pages/Dashboard'
import { Prediction } from '@/pages/Prediction'
import { Optimization } from '@/pages/Optimization'
import { GoldenSignature } from '@/pages/GoldenSignature'
import { Correction } from '@/pages/Correction'
import { Anomaly } from '@/pages/Anomaly'
import { Governance } from '@/pages/Governance'
import { IndustrialValidation } from '@/pages/IndustrialValidation'
import { NotFound } from '@/pages/NotFound'

function App() {
  return (
    <Router>
      <ErrorBoundary>
        <Layout>
          <Routes>
            <Route path="/" element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
            <Route path="/prediction" element={<ErrorBoundary><Prediction /></ErrorBoundary>} />
            <Route path="/optimization" element={<ErrorBoundary><Optimization /></ErrorBoundary>} />
            <Route path="/golden-signature" element={<ErrorBoundary><GoldenSignature /></ErrorBoundary>} />
            <Route path="/correction" element={<ErrorBoundary><Correction /></ErrorBoundary>} />
            <Route path="/anomaly" element={<ErrorBoundary><Anomaly /></ErrorBoundary>} />
            <Route path="/governance" element={<ErrorBoundary><Governance /></ErrorBoundary>} />
            <Route path="/industrial-validation" element={<ErrorBoundary><IndustrialValidation /></ErrorBoundary>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </ErrorBoundary>
    </Router>
  )
}

export default App
