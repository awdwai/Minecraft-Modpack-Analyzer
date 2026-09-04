import type { HealthScore } from '../types'

export function HealthScorePanel({ health }: { health: HealthScore }) {
  const score = health.score
  const color =
    score >= 80 ? 'text-accent' : score >= 50 ? 'text-warn' : 'text-danger'

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
      <div className="flex flex-col items-center justify-center rounded border border-surface-800 bg-surface-900/50 px-8 py-6">
        <div className={`text-5xl font-semibold tabular-nums ${color}`}>{score}</div>
        <div className="mt-1 text-xs uppercase tracking-widest text-muted">Health</div>
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="mb-2 text-sm font-semibold text-ink">Score explanation</h3>
        {health.score_explanation.length === 0 ? (
          <p className="text-sm text-muted">No penalties applied — started at 100.</p>
        ) : (
          <ul className="max-h-48 space-y-1 overflow-y-auto text-sm">
            {health.score_explanation.map((p, i) => (
              <li key={`${p.finding_id}-${i}`} className="flex justify-between gap-4 text-muted">
                <span className="truncate">{p.reason}</span>
                <span className="shrink-0 font-mono text-danger">−{p.amount}</span>
              </li>
            ))}
          </ul>
        )}
        {Object.keys(health.category_scores).length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(health.category_scores).map(([cat, val]) => (
              <span
                key={cat}
                className="rounded border border-surface-700 bg-surface-800 px-2 py-1 text-xs text-muted"
              >
                {cat}: {val}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
