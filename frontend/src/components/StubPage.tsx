/** Honest placeholder for Phase 5–7 features. */

export function StubPage({
  title,
  description,
}: {
  title: string
  description: string
}) {
  return (
    <section className="max-w-xl">
      <p className="mb-2 text-xs uppercase tracking-widest text-muted">Coming later</p>
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      <p className="mt-3 text-muted">{description}</p>
      <div className="mt-6 rounded border border-dashed border-surface-700 bg-surface-900/40 p-4 text-sm text-muted">
        This page is an honest stub — it does not fabricate analysis results. The matching
        API route returns <code className="text-accent">implemented: false</code>.
      </div>
    </section>
  )
}
