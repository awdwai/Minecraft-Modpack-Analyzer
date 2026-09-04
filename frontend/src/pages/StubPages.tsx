import { StubPage } from '../components/StubPage'

export function CrashPage() {
  return (
    <StubPage
      title="Crash log analysis"
      description="Phase 5 will parse crash reports and latest.log with confidence-tagged diagnosis. No fake crash findings are shown here."
    />
  )
}

export function ComparePage() {
  return (
    <StubPage
      title="Compare modpacks"
      description="Phase 5 will diff two absolute pack paths (added/removed/updated mods). The POST /api/compare stub is wired but does not fabricate diffs."
    />
  )
}

export function RepairPage() {
  return (
    <StubPage
      title="Repair tools"
      description="Phase 6 will preview and apply safe fixes (duplicate removal) only after confirm + backup under .mpa-backups/. Analysis remains read-only."
    />
  )
}

export function ReportPage() {
  return (
    <StubPage
      title="Export report"
      description="Phase 5 will export JSON/HTML reports from a stored analysis_id. Until then, use GET /api/analysis/{id} for the raw result."
    />
  )
}
