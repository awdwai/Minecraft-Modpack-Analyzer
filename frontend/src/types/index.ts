/** TypeScript twins of backend models */

export type FindingSeverity = 'critical' | 'warning' | 'info'
export type FindingConfidence = 'confirmed' | 'potential'
export type ModLoader = 'fabric' | 'forge' | 'neoforge' | 'unknown'
export type ModEnvironment = 'client' | 'server' | 'both' | 'unknown'
export type DependencyKind = 'required' | 'optional' | 'conflicts' | 'embedded'

export interface Dependency {
  mod_id: string
  version_constraint?: string | null
  kind: DependencyKind
  side?: string | null
}

export interface Mod {
  mod_id: string
  name: string
  version: string
  loader: ModLoader
  minecraft_version?: string | null
  environment: ModEnvironment
  description?: string | null
  authors: string[]
  dependencies: Dependency[]
  file_path: string
  file_name: string
  file_size: number
  file_hash?: string | null
  parse_ok: boolean
  parse_error?: string | null
}

export interface Finding {
  id: string
  category: string
  severity: FindingSeverity
  confidence: FindingConfidence
  title: string
  message: string
  evidence: string[]
  confidence_reason?: string | null
  suggested_action?: string | null
  related_mod_ids: string[]
  related_files: string[]
}

export interface ScorePenalty {
  reason: string
  amount: number
  category: string
  finding_id?: string | null
}

export interface HealthScore {
  score: number
  category_scores: Record<string, number>
  score_explanation: ScorePenalty[]
}

export interface AnalysisSummary {
  pack_name: string
  path: string
  jar_count: number
  mod_count: number
  parse_failure_count: number
  inferred_minecraft_version?: string | null
  inferred_loader?: ModLoader | null
  client_mod_count: number
  server_mod_count: number
  both_mod_count: number
  finding_counts: Record<string, number>
  has_mods_folder: boolean
  has_config_folder: boolean
  has_logs_folder: boolean
}

export interface GraphNode {
  id: string
  label: string
  mod_id: string
  version: string
  environment: string
  loader: string
  has_error: boolean
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  kind: string
  label?: string | null
}

export interface DependencyGraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  cycles: string[][]
}

export interface AnalysisResult {
  analysis_id: string
  summary: AnalysisSummary
  mods: Mod[]
  findings: Finding[]
  graph: DependencyGraphData
  health: HealthScore
  duration_ms: number
  created_at: string
}

export interface StubResponse {
  implemented: boolean
  message: string
}
