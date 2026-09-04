# Minecraft Modpack Analyzer

Local web app that analyzes a Minecraft modpack folder on disk: **find JARs → parse metadata into Mods → emit Findings → show them in the UI**.

Analysis is **read-only**. JARs, scripts, and Minecraft are **never executed**.

## What it does (Phases 1–4)

- Paste an **absolute** path to a modpack folder
- Scan `mods/` for JARs; inventory `config/` and logs if present
- Parse **Fabric** (`fabric.mod.json`), **Forge** (`META-INF/mods.toml`, legacy `mcmod.info`), and **NeoForge** metadata
- Detect missing required deps, optional deps, version conflicts, duplicates, cycles, client-only mods
- Documented **health score** (start 100, subtract listed penalties)
- Interactive **dependency graph** (React Flow)

Phases 5–7 (crash analysis, compare, repair, reports) are **honest stubs** — routes and pages exist but do not fabricate results.

## Requirements

- Python **3.12+**
- Node.js **20+** (for the Vite frontend)

## Install & run

### Windows (easiest)

1. Double-click **`start.bat`** in the repo root.
2. It creates the backend venv if needed, installs deps, then opens two consoles (API on **8000**, UI on **5173**) and the browser at http://127.0.0.1:5173.
3. To stop: close those consoles, or double-click **`stop.bat`** (kills listeners on 8000/5173).

Requires Python **3.12+** and Node.js **20+** on your PATH.

### Backend (manual)

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r ../requirements.txt
uvicorn app.main:app --reload --port 8000
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

### Frontend (manual)

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173 (proxies `/api` to the backend)

## Tests

```bash
cd backend
# with venv activated and deps installed
pytest -q
```

Fixture mini-packs live under `backend/fixtures/modpacks/` (built automatically by tests via `build_fixtures.py`).

## Health score

Start at **100**, subtract, clamp to **0–100**:

| Finding | Penalty | Cap (count) |
|---------|---------|-------------|
| Critical missing required dependency | −15 | 5 |
| Confirmed metadata conflict | −10 | 10 |
| Version conflict (unsatisfiable) | −8 | 10 |
| Duplicate mod ID / multi-version | −5 | 10 |
| Client-only on server context (warning) | −4 | 10 |
| Potential / uncertain conflict-like | −2 | 10 |
| Parse failure (corrupt JAR) | −1 | 20 |
| Informational | 0 | — |

Each applied penalty appears in `health.score_explanation[]`.

## API (user jobs)

| Method | Path | Job |
|--------|------|-----|
| GET | `/api/health` | Backend up? |
| POST | `/api/analyze` | Analyze absolute folder path |
| GET | `/api/analysis/{id}` | Stored result |
| GET | `/api/mods?analysis_id=` | Mod list |
| GET | `/api/dependencies?analysis_id=` | Graph + dep findings |
| GET | `/api/conflicts?analysis_id=` | Conflict findings |
| POST | `/api/crash/analyze` | Stub (Phase 5) |
| POST | `/api/compare` | Stub (Phase 5) |
| POST | `/api/repair/duplicate` | Stub (Phase 6) |
| POST | `/api/server-pack` | Stub (Phase 6) |
| GET | `/api/report` | Stub (Phase 5) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the human-first layered design and extension checklist.

## Limitations

- No Electron / native installer
- No live Minecraft or Spark profiling
- No Modrinth/CurseForge network lookups
- Repair / server-pack / crash / compare / export are stubs
- In-memory analysis store (lost on backend restart)
- Large packs (thousands of JARs) are supported but the graph layout is simple
