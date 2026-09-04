"""NetworkX dependency graph builder."""

from __future__ import annotations

import networkx as nx

from app.models.analysis_result import DependencyGraphData, GraphEdge, GraphNode
from app.models.dependency import DependencyKind
from app.models.mod import Mod


def build_dependency_graph(mods: list[Mod]) -> DependencyGraphData:
    g = nx.DiGraph()
    ok_mods = [m for m in mods if m.parse_ok]
    seen: dict[str, Mod] = {}
    for mod in ok_mods:
        key = mod.mod_id.lower()
        if key not in seen:
            seen[key] = mod
            g.add_node(key, mod=mod)

    edge_id = 0
    edges: list[GraphEdge] = []
    for mod in ok_mods:
        src = mod.mod_id.lower()
        if src not in g:
            continue
        for dep in mod.dependencies:
            if dep.kind == DependencyKind.EMBEDDED:
                continue
            tgt = dep.mod_id.lower()
            if tgt not in g:
                g.add_node(tgt, missing=True, mod_id=dep.mod_id)
            kind = dep.kind.value
            eid = f"e{edge_id}"
            edge_id += 1
            g.add_edge(src, tgt, kind=kind, constraint=dep.version_constraint)
            edges.append(
                GraphEdge(
                    id=eid,
                    source=src,
                    target=tgt,
                    kind=kind,
                    label=dep.version_constraint,
                )
            )

    nodes: list[GraphNode] = []
    for node_id, data in g.nodes(data=True):
        mod: Mod | None = data.get("mod")
        if mod:
            nodes.append(
                GraphNode(
                    id=node_id,
                    label=mod.name,
                    mod_id=mod.mod_id,
                    version=mod.version,
                    environment=mod.environment.value,
                    loader=mod.loader.value,
                    has_error=False,
                )
            )
        else:
            nodes.append(
                GraphNode(
                    id=node_id,
                    label=str(data.get("mod_id") or node_id),
                    mod_id=str(data.get("mod_id") or node_id),
                    version="?",
                    environment="unknown",
                    loader="unknown",
                    has_error=True,
                )
            )

    cycles: list[list[str]] = []
    try:
        cycles = [list(c) for c in nx.simple_cycles(g)]
        cycles = cycles[:50]
    except Exception:  # noqa: BLE001
        cycles = []

    return DependencyGraphData(nodes=nodes, edges=edges, cycles=cycles)
