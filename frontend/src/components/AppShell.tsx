import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Welcome', end: true },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/mods', label: 'Mods' },
  { to: '/graph', label: 'Graph' },
  { to: '/crash', label: 'Crash' },
  { to: '/compare', label: 'Compare' },
  { to: '/repair', label: 'Repair' },
  { to: '/report', label: 'Report' },
]

export function AppShell({
  children,
  packName,
}: {
  children: ReactNode
  packName?: string | null
}) {
  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-surface-800 bg-surface-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex items-baseline gap-3">
            <span className="font-semibold tracking-tight text-ink">
              Minecraft Modpack Analyzer
            </span>
            {packName && (
              <span className="font-mono text-xs text-muted">{packName}</span>
            )}
          </div>
          <nav className="flex flex-wrap gap-1">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                className={({ isActive }) =>
                  `rounded px-2.5 py-1 text-sm transition-colors ${
                    isActive
                      ? 'bg-surface-800 text-accent'
                      : 'text-muted hover:bg-surface-900 hover:text-ink'
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">{children}</main>
      <footer className="border-t border-surface-800 py-4 text-center text-xs text-muted">
        Read-only analysis · JARs are never executed
      </footer>
    </div>
  )
}
