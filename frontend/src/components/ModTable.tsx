import { useMemo, useState } from 'react'
import type { Mod } from '../types'

export function ModTable({ mods }: { mods: Mod[] }) {
  const [q, setQ] = useState('')
  const [loader, setLoader] = useState('all')
  const [env, setEnv] = useState('all')
  const [sort, setSort] = useState<'name' | 'id' | 'version'>('name')

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase()
    let list = mods.filter((m) => {
      if (loader !== 'all' && m.loader !== loader) return false
      if (env !== 'all' && m.environment !== env) return false
      if (!needle) return true
      return (
        m.name.toLowerCase().includes(needle) ||
        m.mod_id.toLowerCase().includes(needle) ||
        m.file_name.toLowerCase().includes(needle)
      )
    })
    list = [...list].sort((a, b) => {
      if (sort === 'id') return a.mod_id.localeCompare(b.mod_id)
      if (sort === 'version') return a.version.localeCompare(b.version, undefined, { numeric: true })
      return a.name.localeCompare(b.name)
    })
    return list
  }, [mods, q, loader, env, sort])

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-3">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search mods…"
          className="min-w-[220px] flex-1 rounded border border-surface-700 bg-surface-900 px-3 py-2 text-sm outline-none focus:border-accent"
        />
        <select
          value={loader}
          onChange={(e) => setLoader(e.target.value)}
          className="rounded border border-surface-700 bg-surface-900 px-3 py-2 text-sm"
        >
          <option value="all">All loaders</option>
          <option value="fabric">Fabric</option>
          <option value="forge">Forge</option>
          <option value="neoforge">NeoForge</option>
          <option value="unknown">Unknown</option>
        </select>
        <select
          value={env}
          onChange={(e) => setEnv(e.target.value)}
          className="rounded border border-surface-700 bg-surface-900 px-3 py-2 text-sm"
        >
          <option value="all">All environments</option>
          <option value="client">Client</option>
          <option value="server">Server</option>
          <option value="both">Both</option>
        </select>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as typeof sort)}
          className="rounded border border-surface-700 bg-surface-900 px-3 py-2 text-sm"
        >
          <option value="name">Sort: name</option>
          <option value="id">Sort: id</option>
          <option value="version">Sort: version</option>
        </select>
      </div>

      <p className="text-xs text-muted">
        Showing {filtered.length} of {mods.length} JARs
      </p>

      <div className="overflow-x-auto rounded border border-surface-800">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead className="bg-surface-900 text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">ID</th>
              <th className="px-3 py-2 font-medium">Version</th>
              <th className="px-3 py-2 font-medium">Loader</th>
              <th className="px-3 py-2 font-medium">Env</th>
              <th className="px-3 py-2 font-medium">File</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((m) => (
              <tr
                key={m.file_path}
                className={`border-t border-surface-800 ${m.parse_ok ? '' : 'bg-danger/5'}`}
              >
                <td className="px-3 py-2 font-medium">
                  {m.name}
                  {!m.parse_ok && (
                    <span className="ml-2 text-xs text-danger">parse error</span>
                  )}
                </td>
                <td className="px-3 py-2 font-mono text-xs text-muted">{m.mod_id}</td>
                <td className="px-3 py-2 font-mono text-xs">{m.version}</td>
                <td className="px-3 py-2 text-xs">{m.loader}</td>
                <td className="px-3 py-2 text-xs">{m.environment}</td>
                <td className="px-3 py-2 font-mono text-xs text-muted">{m.file_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
