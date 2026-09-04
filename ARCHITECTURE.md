# Architecture (human-first)

Explainable on a whiteboard in under two minutes.

## One-sentence mental model

**Find files → turn JARs into Mods → turn Mods into Findings → show Findings in the UI.**

Everything in the codebase exists to support that pipeline. If a new file does not clearly belong to one of those steps, it is probably in the wrong place.

## The story of one analysis

When a user pastes `C:\Games\ATM10` and clicks Analyze:

1. **UI** sends `{ path }` to `POST /api/analyze`.
2. **API** validates the body; path validation ensures an absolute existing directory.
3. **`services/analyze_service`** runs the recipe and returns one `AnalysisResult`.
4. **Scanner** lists JARs / config / logs without interpreting mods.
5. **Parser** opens each JAR as a ZIP, reads Fabric/Forge/NeoForge metadata, builds a normalized `Mod` (or a parse-error finding later).
6. **Analyzers + graph** emit `Finding`s, a dependency graph, and a health score.
7. **UI** renders the same `AnalysisResult` on Dashboard / Mods / Graph — no second source of truth.

```
User path → API → analyze_service
                 → scanner → ModpackInventory
                 → parser  → list[Mod]
                 → analysis + graph → findings, graph, health
                 → AnalysisResult → in-memory store → UI
```

## Four backend layers

Dependencies only point **downward**. Routes never call parsers directly. Parsers never import FastAPI.

| Layer | Folder | Job | May call | Must not |
|-------|--------|-----|----------|----------|
| 1. Edge | `api/` | HTTP in/out | `services/` | Contain analysis logic |
| 2. Orchestration | `services/` | Run the recipe | scanner, parser, analysis, graph, repair, cache | Know React / raw HTTP details |
| 3. Domain engines | `scanner/`, `parser/`, `analysis/`, `graph/`, `repair/` | One kind of work | `models/`, stdlib, NetworkX | Call each other sideways when avoidable |
| 4. Shared truth | `models/`, `security/`, `cache/` | Shared shapes + safe helpers | almost nothing above | Become a junk drawer |

**Debugging map**

- “Why is Curios missing?” → `analysis/dependency_analyzer.py`
- “Why is this JAR empty?” → `parser/`
- “Wrong JSON field in the UI?” → `api/` + `models/` + `frontend/src/types`

## Shared language

- **`Mod`** — one JAR after parsing (loader quirks stay in the parser)
- **`Dependency`** — needs / optionally wants / conflicts with a mod id + version rule
- **`Finding`** — one explainable issue (severity + evidence + confidence + suggested action)
- **`AnalysisResult`** — the whole answer for one run

**Confidence rule**

- Explicit metadata → may be **confirmed**
- Inference / heuristics → must say **potential**, with confidence reason
- Never show a red conflict without evidence the user can read

## Frontend

| Page | Job |
|------|-----|
| Welcome | Enter absolute path |
| Dashboard | Score + top findings |
| Mods | Searchable table from `result.mods` |
| Graph | React Flow from `result.graph` |
| Crash / Compare / Repair / Report | Honest stubs until Phases 5–7 |

Pages render; `services/api.ts` fetches; components do not call `fetch` themselves.

## How to extend without making a mess

1. Need a new field? Update `models/` first (and TS types).
2. “Read files”? → `scanner/` or `parser/`.
3. “Judge the pack”? → `analysis/`, called from `analyze_service`.
4. “Change files”? → `repair/` + backup + confirm; never from an analyzer.
5. Expose with a thin route in `api/`.
6. Show on one page.

If a tiny tweak forces edits in five layers, the design drifted — pull logic back into the service or model.

## Security

- Analysis is **read-only**
- Paths must be absolute existing directories
- Repairs (Phase 6) require confirm + backup under `.mpa-backups/`
- **Never** execute JARs, scripts, or Minecraft from this app

## Health score

Documented in [README.md](README.md). Implemented in `analysis/health_analyzer.py`. The UI shows `score_explanation[]` so the number is never opaque.
