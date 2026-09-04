import { Link } from 'react-router-dom'
import { ModTable } from '../components/ModTable'
import { useAnalysis } from '../hooks/useAnalysis'

export function ModsPage() {
  const { result } = useAnalysis()

  if (!result) {
    return (
      <section>
        <h1 className="text-2xl font-semibold">Mods</h1>
        <p className="mt-2 text-muted">
          <Link to="/" className="text-accent underline">
            Analyze a modpack
          </Link>{' '}
          to see the mod table.
        </p>
      </section>
    )
  }

  return (
    <section className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold tracking-tight">Mods</h1>
      <p className="text-sm text-muted">
        Parsed from JAR metadata in {result.summary.pack_name}. Search, filter, and sort the
        real scan — nothing is hardcoded.
      </p>
      <ModTable mods={result.mods} />
    </section>
  )
}
