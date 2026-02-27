import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { Prediction } from '@/pages/Prediction'
import { Optimization } from '@/pages/Optimization'
import { GoldenSignature } from '@/pages/GoldenSignature'
import { Correction } from '@/pages/Correction'
import { Anomaly } from '@/pages/Anomaly'
import { Governance } from '@/pages/Governance'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/prediction" element={<Prediction />} />
          <Route path="/optimization" element={<Optimization />} />
          <Route path="/golden-signature" element={<GoldenSignature />} />
          <Route path="/correction" element={<Correction />} />
          <Route path="/anomaly" element={<Anomaly />} />
          <Route path="/governance" element={<Governance />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
