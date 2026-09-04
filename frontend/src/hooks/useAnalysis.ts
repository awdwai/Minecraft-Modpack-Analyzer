import { createContext, useContext } from 'react'
import type { AnalysisResult } from '../types'

export interface AnalysisApi {
  result: AnalysisResult | null
  loading: boolean
  error: string | null
  path: string
  setPath: (p: string) => void
  analyze: (modpackPath: string) => Promise<AnalysisResult>
  clear: () => void
  setError: (e: string | null) => void
}

export const AnalysisContext = createContext<AnalysisApi | null>(null)

export function useAnalysis(): AnalysisApi {
  const ctx = useContext(AnalysisContext)
  if (!ctx) throw new Error('useAnalysis must be used within AnalysisProvider')
  return ctx
}
