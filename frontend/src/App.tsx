import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { useAnalysis } from './hooks/useAnalysis'
import { DashboardPage } from './pages/DashboardPage'
import { GraphPage } from './pages/GraphPage'
import { ModsPage } from './pages/ModsPage'
import {
  ComparePage,
  CrashPage,
  RepairPage,
  ReportPage,
} from './pages/StubPages'
import { WelcomePage } from './pages/WelcomePage'
import { AnalysisProvider } from './state'

function Shell() {
  const { result } = useAnalysis()
  return (
    <AppShell packName={result?.summary.pack_name}>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/mods" element={<ModsPage />} />
        <Route path="/graph" element={<GraphPage />} />
        <Route path="/crash" element={<CrashPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/repair" element={<RepairPage />} />
        <Route path="/report" element={<ReportPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AnalysisProvider>
        <Shell />
      </AnalysisProvider>
    </BrowserRouter>
  )
}
