/** Only place that talks HTTP to the backend. */

import type { AnalysisResult, StubResponse } from '../types'

const BASE = import.meta.env.VITE_API_BASE ?? ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? JSON.stringify(body)
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return res.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string }>('/api/health'),

  analyze: (path: string) =>
    request<AnalysisResult>('/api/analyze', {
      method: 'POST',
      body: JSON.stringify({ path }),
    }),

  getAnalysis: (analysisId: string) =>
    request<AnalysisResult>(`/api/analysis/${analysisId}`),

  listMods: (analysisId: string, q?: string) => {
    const params = new URLSearchParams({ analysis_id: analysisId })
    if (q) params.set('q', q)
    return request<{ analysis_id: string; count: number; mods: AnalysisResult['mods'] }>(
      `/api/mods?${params}`,
    )
  },

  crashAnalyze: (payload: { path?: string; text?: string }) =>
    request<StubResponse>('/api/crash/analyze', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  compare: (pathA: string, pathB: string) =>
    request<StubResponse>('/api/compare', {
      method: 'POST',
      body: JSON.stringify({ path_a: pathA, path_b: pathB }),
    }),

  repairDuplicate: (analysisId: string, confirm = false) =>
    request<StubResponse>('/api/repair/duplicate', {
      method: 'POST',
      body: JSON.stringify({ analysis_id: analysisId, confirm }),
    }),

  serverPack: (analysisId: string) =>
    request<StubResponse>('/api/server-pack', {
      method: 'POST',
      body: JSON.stringify({ analysis_id: analysisId }),
    }),

  report: (analysisId: string, format: 'json' | 'html' = 'json') =>
    request<StubResponse>(`/api/report?analysis_id=${analysisId}&format=${format}`),
}
