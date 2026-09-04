import type { Finding } from '../types'
import { ConfidenceBadge, StatusBadge } from './StatusBadge'

export function FindingList({
  findings,
  limit,
}: {
  findings: Finding[]
  limit?: number
}) {
  const items = limit ? findings.slice(0, limit) : findings
  if (!items.length) {
    return <p className="text-muted text-sm">No findings in this view.</p>
  }
  return (
    <ul className="flex flex-col gap-3">
      {items.map((f) => (
        <li
          key={f.id}
          className="border-b border-surface-800 pb-3 last:border-0"
        >
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <StatusBadge severity={f.severity} />
            <ConfidenceBadge confidence={f.confidence} />
            <span className="text-xs text-muted">{f.category}</span>
          </div>
          <h3 className="text-sm font-semibold text-ink">{f.title}</h3>
          <p className="mt-1 text-sm text-muted">{f.message}</p>
          {f.suggested_action && (
            <p className="mt-1 text-sm text-accent-dim">→ {f.suggested_action}</p>
          )}
          {f.evidence.length > 0 && (
            <details className="mt-2 text-xs text-muted">
              <summary className="cursor-pointer select-none">Evidence</summary>
              <ul className="mt-1 list-disc pl-5 font-mono">
                {f.evidence.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </details>
          )}
        </li>
      ))}
    </ul>
  )
}
