import { Link } from 'react-router-dom'
import { FindingList } from '../components/FindingList'
import { HealthScorePanel } from '../components/HealthScorePanel'
import { useAnalysis } from '../hooks/useAnalysis'

export function DashboardPage() {
  const { result } = useAnalysis()

  if (!result) {
    return (
      <section>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="mt-2 text-muted">
          No analysis loaded.{' '}
          <Link to="/" className="text-accent underline">
            Analyze a modpack
          </Link>{' '}
          first.
        </p>
      </section>
    )
  }

  const { summary, health, findings } = result
  const top = [...findings]
    .sort((a, b) => {
      const order = { critical: 0, warning: 1, info: 2 }
      return order[a.severity] - order[b.severity]
    })
    .slice(0, 8)

  return (
    <section className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{summary.pack_name}</h1>
        <p className="mt-1 font-mono text-xs text-muted">{summary.path}</p>
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <Meta label="Minecraft" value={summary.inferred_minecraft_version ?? '—'} />
          <Meta label="Loader" value={summary.inferred_loader ?? '—'} />
          <Meta label="JARs" value={String(summary.jar_count)} />
          <Meta label="Parsed mods" value={String(summary.mod_count)} />
          <Meta label="Client-only" value={String(summary.client_mod_count)} />
          <Meta label="Both" value={String(summary.both_mod_count)} />
          <Meta label="Server-only" value={String(summary.server_mod_count)} />
          <Meta label="Duration" value={`${result.duration_ms} ms`} />
        </div>
      </div>

      <HealthScorePanel health={health} />

      <div>
        <div className="mb-3 flex items-baseline justify-between gap-2">
          <h2 className="text-lg font-semibold">Top findings</h2>
          <span className="text-xs text-muted">
            critical {summary.finding_counts.critical ?? 0} · warning{' '}
            {summary.finding_counts.warning ?? 0} · info {summary.finding_counts.info ?? 0}
          </span>
        </div>
        <FindingList findings={top} />
      </div>
    </section>
  )
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded border border-surface-800 bg-surface-900/50 px-2.5 py-1">
      <span className="text-muted">{label}: </span>
      <span className="font-medium">{value}</span>
    </span>
  )
}
