import { useMemo, useState, useCallback, type MouseEvent } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { DependencyGraphData, GraphNode } from '../types'

export function GraphCanvas({ graph }: { graph: DependencyGraphData }) {
  const [selected, setSelected] = useState<GraphNode | null>(null)
  const [q, setQ] = useState('')
  const [kindFilter, setKindFilter] = useState('all')
  const [envFilter, setEnvFilter] = useState('all')
  const [errorsOnly, setErrorsOnly] = useState(false)

  const { nodes, edges } = useMemo(() => {
    const needle = q.trim().toLowerCase()
    const visibleIds = new Set(
      graph.nodes
        .filter((n) => {
          if (errorsOnly && !n.has_error) return false
          if (envFilter !== 'all' && n.environment !== envFilter) return false
          if (!needle) return true
          return (
            n.label.toLowerCase().includes(needle) ||
            n.mod_id.toLowerCase().includes(needle)
          )
        })
        .map((n) => n.id),
    )

    if (needle) {
      for (const e of graph.edges) {
        if (visibleIds.has(e.source) || visibleIds.has(e.target)) {
          visibleIds.add(e.source)
          visibleIds.add(e.target)
        }
      }
    }

    const filteredEdges = graph.edges.filter((e) => {
      if (!visibleIds.has(e.source) || !visibleIds.has(e.target)) return false
      if (kindFilter !== 'all' && e.kind !== kindFilter) return false
      return true
    })

    const list = graph.nodes.filter((n) => visibleIds.has(n.id))
    const count = Math.max(list.length, 1)
    const flowNodes: Node[] = list.map((node, i) => {
      const angle = (2 * Math.PI * i) / count
      const radius = 40 + Math.min(count, 40) * 12
      return {
        id: node.id,
        position: { x: Math.cos(angle) * radius + 400, y: Math.sin(angle) * radius + 300 },
        data: { label: `${node.label}\n${node.version}`, meta: node },
        style: {
          background: node.has_error ? '#3a1a1a' : '#1a2330',
          color: '#e8eef5',
          border: `1px solid ${node.has_error ? '#e85d5d' : '#3dd68c55'}`,
          borderRadius: 8,
          fontSize: 11,
          padding: 8,
          whiteSpace: 'pre-line',
          textAlign: 'center' as const,
          width: 140,
        },
      }
    })

    const edgeColor: Record<string, string> = {
      required: '#3dd68c',
      optional: '#5ba4e6',
      conflicts: '#e85d5d',
    }

    const flowEdges: Edge[] = filteredEdges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.label ?? e.kind,
      style: { stroke: edgeColor[e.kind] ?? '#8b9bb0' },
      markerEnd: { type: MarkerType.ArrowClosed, color: edgeColor[e.kind] ?? '#8b9bb0' },
      labelStyle: { fill: '#8b9bb0', fontSize: 10 },
    }))

    return { nodes: flowNodes, edges: flowEdges }
  }, [graph, q, kindFilter, envFilter, errorsOnly])

  const onNodeClick = useCallback((_: MouseEvent, node: Node) => {
    const meta = (node.data as { meta?: GraphNode }).meta
    setSelected(meta ?? null)
  }, [])

  return (
    <div className="flex h-[min(70vh,640px)] flex-col gap-3 lg:flex-row">
      <div className="flex min-h-[420px] flex-1 flex-col gap-2">
        <div className="flex flex-wrap gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search / highlight…"
            className="rounded border border-surface-700 bg-surface-900 px-3 py-1.5 text-sm outline-none focus:border-accent"
          />
          <select
            value={kindFilter}
            onChange={(e) => setKindFilter(e.target.value)}
            className="rounded border border-surface-700 bg-surface-900 px-2 py-1.5 text-sm"
          >
            <option value="all">All edge kinds</option>
            <option value="required">Required</option>
            <option value="optional">Optional</option>
            <option value="conflicts">Conflicts</option>
          </select>
          <select
            value={envFilter}
            onChange={(e) => setEnvFilter(e.target.value)}
            className="rounded border border-surface-700 bg-surface-900 px-2 py-1.5 text-sm"
          >
            <option value="all">All envs</option>
            <option value="client">Client</option>
            <option value="server">Server</option>
            <option value="both">Both</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-muted">
            <input
              type="checkbox"
              checked={errorsOnly}
              onChange={(e) => setErrorsOnly(e.target.checked)}
            />
            Missing / errors only
          </label>
        </div>
        <div className="min-h-0 flex-1 overflow-hidden rounded border border-surface-800 bg-surface-950">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodeClick={onNodeClick}
            fitView
            minZoom={0.2}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#243041" gap={18} />
            <Controls />
            <MiniMap
              nodeColor={(n) =>
                (n.data as { meta?: GraphNode }).meta?.has_error ? '#e85d5d' : '#3dd68c'
              }
              maskColor="rgba(0,0,0,0.6)"
            />
          </ReactFlow>
        </div>
        {graph.cycles.length > 0 && (
          <p className="text-xs text-warn">
            {graph.cycles.length} dependency cycle(s) detected — see findings on Dashboard.
          </p>
        )}
      </div>

      <aside className="w-full shrink-0 rounded border border-surface-800 bg-surface-900/60 p-4 lg:w-72">
        <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted">
          Node detail
        </h3>
        {!selected ? (
          <p className="text-sm text-muted">Select a node to inspect.</p>
        ) : (
          <dl className="space-y-2 text-sm">
            <div>
              <dt className="text-xs text-muted">Name</dt>
              <dd>{selected.label}</dd>
            </div>
            <div>
              <dt className="text-xs text-muted">Mod ID</dt>
              <dd className="font-mono">{selected.mod_id}</dd>
            </div>
            <div>
              <dt className="text-xs text-muted">Version</dt>
              <dd className="font-mono">{selected.version}</dd>
            </div>
            <div>
              <dt className="text-xs text-muted">Loader</dt>
              <dd>{selected.loader}</dd>
            </div>
            <div>
              <dt className="text-xs text-muted">Environment</dt>
              <dd>{selected.environment}</dd>
            </div>
            {selected.has_error && (
              <p className="text-danger">Missing from pack (declared dependency only).</p>
            )}
          </dl>
        )}
      </aside>
    </div>
  )
}
