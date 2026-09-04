import type { ReactNode } from 'react'
import type { FindingConfidence, FindingSeverity } from '../types'

const severityClass: Record<FindingSeverity, string> = {
  critical: 'bg-danger/15 text-danger border-danger/30',
  warning: 'bg-warn/15 text-warn border-warn/30',
  info: 'bg-info/15 text-info border-info/30',
}

export function StatusBadge({
  severity,
  children,
}: {
  severity: FindingSeverity
  children?: ReactNode
}) {
  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium uppercase tracking-wide ${severityClass[severity]}`}
    >
      {children ?? severity}
    </span>
  )
}

export function ConfidenceBadge({ confidence }: { confidence: FindingConfidence }) {
  const cls =
    confidence === 'confirmed'
      ? 'text-accent border-accent/30 bg-accent/10'
      : 'text-muted border-surface-700 bg-surface-800'
  return (
    <span className={`inline-flex rounded border px-2 py-0.5 text-xs ${cls}`}>{confidence}</span>
  )
}
