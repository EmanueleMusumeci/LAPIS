/**
 * API client for the LAPIS backend.
 */
import type {
  PresetList,
  Preset,
  PipelineConfig,
  ModelRaceData,
  ModelInfo,
  HealthStatus,
} from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || ''

/**
 * Generic fetch wrapper with error handling.
 */
async function fetchJson<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// ─── Presets ─────────────────────────────────────────────────────────────────

export async function getPresets(): Promise<PresetList> {
  return fetchJson<PresetList>('/api/presets')
}

export async function getPreset(domain: string, problemId: string): Promise<Preset> {
  return fetchJson<Preset>(`/api/presets/${domain}/${problemId}`)
}

export async function getPresetPddl(domain: string, problemId: string): Promise<{ domain_pddl: string; problem_pddl: string }> {
  return fetchJson<{ domain_pddl: string; problem_pddl: string }>(`/api/presets/${domain}/${problemId}/pddl`)
}

export async function getDomains(): Promise<string[]> {
  return fetchJson<string[]>('/api/domains')
}

export async function getDomainProblems(domain: string): Promise<string[]> {
  return fetchJson<string[]>(`/api/domains/${domain}/problems`)
}

// ─── Pipeline ────────────────────────────────────────────────────────────────

export async function startPipeline(config: PipelineConfig): Promise<{ run_id: string }> {
  return fetchJson<{ run_id: string }>('/api/run', {
    method: 'POST',
    body: JSON.stringify(config),
  })
}

export async function getPipelineStatus(runId: string) {
  return fetchJson(`/api/status/${runId}`)
}

export async function cancelPipeline(runId: string) {
  return fetchJson(`/api/cancel/${runId}`, { method: 'POST' })
}

// ─── Results ─────────────────────────────────────────────────────────────────

export async function getResults(filters?: {
  domain?: string
  method?: string
  model?: string
}): Promise<ModelRaceData> {
  const params = new URLSearchParams()
  if (filters?.domain) params.set('domain', filters.domain)
  if (filters?.method) params.set('method', filters.method)
  if (filters?.model) params.set('model', filters.model)

  const query = params.toString()
  return fetchJson<ModelRaceData>(`/api/results${query ? `?${query}` : ''}`)
}

// Alias for Model Race page
export const fetchModelRaceData = getResults

// ─── Planner ─────────────────────────────────────────────────────────────────

export async function runPlanner(params: {
  domain_pddl: string
  problem_pddl: string
  planner?: string
  timeout?: number
}): Promise<{ success: boolean; plan: string[]; error: string }> {
  return fetchJson('/api/plan', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ─── System ──────────────────────────────────────────────────────────────────

export async function getModels(): Promise<ModelInfo> {
  return fetchJson<ModelInfo>('/api/models')
}

export async function getHealth(): Promise<HealthStatus> {
  return fetchJson<HealthStatus>('/health')
}

// ─── WebSocket ───────────────────────────────────────────────────────────────

export function createPipelineWebSocket(): WebSocket {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const envWsUrl = import.meta.env.VITE_WS_URL?.trim()

  const normalizeWsUrl = (raw: string): string => {
    const hasScheme = /^[a-z]+:\/\//i.test(raw)
    const withScheme = hasScheme ? raw : `${wsProtocol}//${raw}`
    const parsed = new URL(withScheme)

    // Convert accidental http(s) schemes to ws(s) for WebSocket compatibility.
    if (parsed.protocol === 'http:') parsed.protocol = 'ws:'
    if (parsed.protocol === 'https:') parsed.protocol = 'wss:'

    const basePath = parsed.pathname.replace(/\/+$/, '')
    parsed.pathname = basePath.endsWith('/ws/pipeline') ? basePath : `${basePath}/ws/pipeline`
    return parsed.toString()
  }

  const fullUrl = envWsUrl
    ? normalizeWsUrl(envWsUrl)
    : `${wsProtocol}//${window.location.host}/ws/pipeline`

  console.log('[LAPIS] WebSocket connection:', {
    VITE_WS_URL: envWsUrl,
    fullUrl,
    windowLocation: window.location.host,
  })
  return new WebSocket(fullUrl)
}
