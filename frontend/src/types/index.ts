/**
 * Type definitions for the LAPIS frontend.
 * Mirrors the Pydantic models from the backend.
 */

export type StageStatus = 'pending' | 'running' | 'done' | 'error' | 'skipped'

export interface RefinementEntry {
  iteration: number
  error: string
  fix: string
  success: boolean
  domain_pddl_before: string
  problem_pddl_before: string
  domain_pddl_after: string
  problem_pddl_after: string
}

export interface CoTStep {
  step: number
  label: string
  content: string
}

export interface StageResult {
  name: string
  status: StageStatus
  duration: number
  domain_pddl: string
  problem_pddl: string
  adequacy_analysis: string
  domain_amended: boolean
  problem_amended: boolean
  schema_block: string
  val_log: string
  plan_actions: string[]
  refinement_history: RefinementEntry[]
  error_msg: string
  cot_steps: CoTStep[]
}

export interface RunResult {
  success: boolean
  stages: StageResult[]
  final_domain_pddl: string
  final_problem_pddl: string
  plan_actions: string[]
  plan_file_path: string
  domain_file_path: string
  problem_file_path: string
  plan_animation_url: string  // URL to plan animation GIF
  plan_step_images: string[]  // URLs to individual step images
  total_time: number
  refinements: number
  method: PipelineMethod
  error_msg: string
}

export type PipelineMethod = 'lapis' | 'lapis_noadq' | 'llmpp' | 'gt_lapis' | 'sim_val'

export interface PipelineConfig {
  domain_nl: string
  problem_nl: string
  method: PipelineMethod
  domain_name: string
  model_id: string
  planner_name: string
  planner_timeout: number
  max_refinements: number
  skip_adequacy: boolean
  semantic_checks: boolean
  refine_domain: boolean
  extractor_type: string
  api_key?: string
}

export interface Preset {
  id: string
  label: string
  domain: string
  problem_id: string
  domain_nl: string
  problem_nl: string
}

export interface PresetList {
  presets: Preset[]
  domains: string[]
}

// WebSocket message types
export type WSMessageType = 'connected' | 'stage_update' | 'complete' | 'error' | 'run_started'

export interface WSMessage {
  type: WSMessageType
  run_id?: string
  data?: StageResult | RunResult
  message?: string
}

// Model Race types
export interface BenchmarkResult {
  domain: string
  problem_id: string
  method: string
  method_label: string
  model: string
  success: boolean
  val_valid: boolean
  plan_length: number
  refinements: number
  total_time: number
  error_msg: string
}

export interface BenchmarkSummary {
  domain: string
  method: string
  method_label: string
  model: string
  total_runs: number
  successful_runs: number
  success_rate: number   // planning success rate
  val_rate: number       // VAL validation rate
  gt_executability?: number | null  // GT simulator rate (Sim-LAPIS² only)
  avg_plan_length: number
  avg_refinements: number
  avg_time: number
}

export interface ModelRaceData {
  summaries: BenchmarkSummary[]
  results: BenchmarkResult[]
  domains: string[]
  methods: string[]
  models: string[]
}

// API response types
export interface ModelInfo {
  models: Record<string, string>
  planners: string[]
}

export interface HealthStatus {
  status: string
  mock_mode: boolean
  debug: boolean
}

export interface VerificationPayload {
  valid: boolean
  errors: string[]
  warnings: string[]
  asp_notes?: string[]
  source?: 'text' | 'graphical'
}

export interface EditorUpdateData {
  domain: string
  problem: string
  source: 'agent' | 'text' | 'graphical'
  verification?: VerificationPayload
}

export interface AgentMessageData {
  response: string
  domain: string
  problem: string
  verification?: VerificationPayload
}

export type EditorWSMessageType =
  | 'INIT_SESSION'
  | 'UPDATE'
  | 'USER_MESSAGE'
  | 'AGENT_MESSAGE'
  | 'PDDL_UPDATE'
  | 'VERIFY_REQUEST'
  | 'VERIFY_RESULTS'

export type ExtendedWSMessageType = WSMessageType | EditorWSMessageType

export interface ExtendedWSMessage {
  type: ExtendedWSMessageType
  run_id?: string
  data?: StageResult | RunResult | AgentMessageData | VerificationPayload | EditorUpdateData
  message?: string
}
