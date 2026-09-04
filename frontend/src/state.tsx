import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { api } from './services/api'
import { AnalysisContext } from './hooks/useAnalysis'
import type { AnalysisResult } from './types'

const STORAGE_KEY = 'mpa.analysisId'
const PATH_KEY = 'mpa.lastPath'

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [path, setPath] = useState(() => localStorage.getItem(PATH_KEY) ?? '')

  useEffect(() => {
    const id = localStorage.getItem(STORAGE_KEY)
    if (!id) return
    api
      .getAnalysis(id)
      .then((r) => setResult(r))
      .catch(() => localStorage.removeItem(STORAGE_KEY))
  }, [])

  const analyze = useCallback(async (modpackPath: string) => {
    setLoading(true)
    setError(null)
    try {
      const r = await api.analyze(modpackPath)
      setResult(r)
      setPath(modpackPath)
      localStorage.setItem(STORAGE_KEY, r.analysis_id)
      localStorage.setItem(PATH_KEY, modpackPath)
      return r
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
      throw e
    } finally {
      setLoading(false)
    }
  }, [])

  const clear = useCallback(() => {
    setResult(null)
    localStorage.removeItem(STORAGE_KEY)
  }, [])

  return (
    <AnalysisContext.Provider
      value={{ result, loading, error, path, setPath, analyze, clear, setError }}
    >
      {children}
    </AnalysisContext.Provider>
  )
}
