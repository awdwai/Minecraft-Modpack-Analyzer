import { useNavigate } from 'react-router-dom'
import type { FormEvent } from 'react'
import { useAnalysis } from '../hooks/useAnalysis'

export function WelcomePage() {
  const { path, setPath, analyze, loading, error, setError } = useAnalysis()
  const navigate = useNavigate()

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await analyze(path.trim())
      navigate('/dashboard')
    } catch {
      /* error already set */
    }
  }

  return (
    <section className="mx-auto max-w-2xl pt-6">
      <p className="mb-3 text-xs uppercase tracking-[0.2em] text-accent">Local · Read-only</p>
      <h1 className="text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
        Minecraft Modpack Analyzer
      </h1>
      <p className="mt-4 max-w-xl text-lg text-muted">
        Paste an absolute path to a modpack folder. We find JARs, parse Fabric / Forge /
        NeoForge metadata, and surface dependency findings — without running Minecraft or
        executing mods.
      </p>

      <ul className="mt-8 space-y-2 text-sm text-muted">
        <li>• Real metadata from JARs on disk — no fabricated results</li>
        <li>• Missing deps, duplicates, version conflicts, client-only mods</li>
        <li>• Interactive dependency graph + documented health score</li>
      </ul>

      <form onSubmit={onSubmit} className="mt-10 flex flex-col gap-3">
        <label htmlFor="path" className="text-sm font-medium text-ink">
          Absolute modpack path
        </label>
        <input
          id="path"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder="C:\Games\All the Mods 10"
          className="rounded border border-surface-700 bg-surface-900 px-4 py-3 font-mono text-sm outline-none focus:border-accent"
          required
        />
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={loading || !path.trim()}
            className="rounded bg-accent px-5 py-2.5 text-sm font-semibold text-surface-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Analyzing…' : 'Analyze'}
          </button>
          <span className="text-xs text-muted">Backend must be running on port 8000</span>
        </div>
        {error && (
          <p className="rounded border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
            {error}
          </p>
        )}
      </form>
    </section>
  )
}
