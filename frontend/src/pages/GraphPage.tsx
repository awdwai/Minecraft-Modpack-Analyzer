import { Link } from 'react-router-dom'
import { GraphCanvas } from '../components/GraphCanvas'
import { useAnalysis } from '../hooks/useAnalysis'

export function GraphPage() {
  const { result } = useAnalysis()

  if (!result) {
    return (
      <section>
        <h1 className="text-2xl font-semibold">Dependency graph</h1>
        <p className="mt-2 text-muted">
          <Link to="/" className="text-accent underline">
            Analyze a modpack
          </Link>{' '}
          to explore dependencies.
        </p>
      </section>
    )
  }

  return (
    <section className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dependency graph</h1>
        <p className="mt-1 text-sm text-muted">
          {result.graph.nodes.length} nodes · {result.graph.edges.length} edges · built from
          declared metadata
        </p>
      </div>
      <GraphCanvas graph={result.graph} />
    </section>
  )
}
