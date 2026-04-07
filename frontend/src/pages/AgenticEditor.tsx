import { Bot, CheckCircle2, AlertTriangle, Wifi, WifiOff, Loader2 } from 'lucide-react'
import { useAgenticEditor } from '@/hooks/useAgenticEditor'
import { usePresets } from '@/hooks/usePresets'
import GridworldEditor from '@/components/editors/GridworldEditor'
import BlocksworldEditor from '@/components/editors/BlocksworldEditor'
import DomainStateViewer from '@/components/editors/DomainStateViewer'
import PDDLEditor, { type PDDLIssue } from '@/components/PDDLEditor'
import PresetSelector from '@/components/PresetSelector'
import { extractIssueLine } from '@/lib/pddlPatch'
import { ApiKeyInput } from '@/contexts/ApiKeyContext'

// ─── Domain detection helpers ────────────────────────────────────────────────

function detectDomain(domainPddl: string): string {
  const src = domainPddl.toLowerCase()
  if (/\(domain\s+blocksworld|\(on-table\s|\(arm-empty\)/.test(src)) return 'blocksworld'
  if (/minigrid|babyai|agentinroom|objectinroom/.test(src)) return 'gridworld'
  if (/gripper-strips|at-robby/.test(src)) return 'grippers'
  if (/\(domain\s+barman|cocktail-part/.test(src)) return 'barman'
  if (/floor-tile|floortile/.test(src)) return 'floortile'
  if (/\(domain\s+storage|storeat/.test(src)) return 'storage'
  if (/\(domain\s+termes|numb\s+-\s+object/.test(src)) return 'termes'
  if (/\(domain\s+tyreworld|inflate/.test(src)) return 'tyreworld'
  return 'custom'
}

// ─── Verification panel ───────────────────────────────────────────────────────

function VerificationPanel({
  valid,
  errors,
  warnings,
}: {
  valid: boolean
  errors: string[]
  warnings: string[]
}) {
  return (
    <div className="rounded-xl border border-lapis-border bg-lapis-card p-4 space-y-3">
      <div className="flex items-center gap-2 text-sm font-semibold">
        {valid ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <AlertTriangle className="w-4 h-4 text-yellow-500" />}
        <span>{valid ? 'Verification passed' : 'Verification requires attention'}</span>
      </div>

      {errors.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-wide text-red-400 mb-2">Errors</p>
          <ul className="space-y-1 text-sm">
            {errors.map((err, idx) => (
              <li key={`${err}-${idx}`} className="text-red-300">{err}</li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-wide text-yellow-300 mb-2">Warnings</p>
          <ul className="space-y-1 text-sm">
            {warnings.map((warn, idx) => (
              <li key={`${warn}-${idx}`} className="text-yellow-200">{warn}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// ─── Visualizer panel ─────────────────────────────────────────────────────────

function DomainVisualizer({
  domain,
  problemPddl,
  onProblemChange,
}: {
  domain: string
  problemPddl: string
  onProblemChange: (updated: string) => void
}) {
  if (domain === 'blocksworld') {
    return (
      <BlocksworldEditor
        problemPddl={problemPddl}
        onChange={onProblemChange}
      />
    )
  }

  if (domain === 'gridworld') {
    return (
      <GridworldEditor
        problemPddl={problemPddl}
        onChange={onProblemChange}
      />
    )
  }

  // For all other known IPC domains, show a read-only state viewer
  const knownDomains = ['grippers', 'barman', 'floortile', 'storage', 'termes', 'tyreworld']
  if (knownDomains.includes(domain)) {
    return (
      <DomainStateViewer
        domainName={domain}
        problemPddl={problemPddl}
      />
    )
  }

  return null
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function AgenticEditor() {
  const {
    state,
    setUserInput,
    sendUserMessage,
    syncFromText,
    syncFromGraphical,
    runVerification,
    loadPreset,
  } = useAgenticEditor()

  const { data: presetsData } = usePresets()
  const presets = presetsData?.presets ?? []

  const domain = detectDomain(state.domainPddl)

  const problemIssues: PDDLIssue[] = [
    ...(state.verification?.errors || []).map((message) => ({
      line: extractIssueLine(state.problemPddl, message) || 1,
      message,
      severity: 'error' as const,
    })),
    ...(state.verification?.warnings || []).map((message) => ({
      line: extractIssueLine(state.problemPddl, message) || 1,
      message,
      severity: 'warning' as const,
    })),
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 xl:grid-cols-5 gap-4">
      {/* Left column: chat + editors */}
      <section className="xl:col-span-3 space-y-4">

        {/* Preset selector */}
        <PresetSelector
          presets={presets}
          selectedPreset={state.selectedPreset}
          onPresetChange={loadPreset}
        />

        {/* Chat / agent panel */}
        <div className="rounded-xl border border-lapis-border bg-lapis-card p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-lapis-accent" />
              <h2 className="text-lg font-semibold">Agentic Editor</h2>
            </div>
            <div className="flex items-center gap-2 text-xs text-lapis-text-secondary">
              {state.connected ? <Wifi className="w-4 h-4 text-green-500" /> : <WifiOff className="w-4 h-4 text-red-400" />}
              <span>{state.connected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>

          <div className="h-48 overflow-y-auto rounded-lg border border-lapis-border bg-lapis-background/40 p-3 space-y-2">
            {state.chat.length === 0 && (
              <p className="text-sm text-lapis-text-secondary">No messages yet. Ask the agent to modify domain/problem PDDL.</p>
            )}
            {state.chat.map((entry, idx) => (
              <div key={`${entry.at}-${idx}`} className={`text-sm ${entry.role === 'agent' ? 'text-lapis-text' : 'text-lapis-accent'}`}>
                <span className="font-semibold mr-2">{entry.role === 'agent' ? 'Agent' : 'You'}:</span>
                <span>{entry.text}</span>
              </div>
            ))}
          </div>

          <ApiKeyInput className="mt-3" />

          <form
            className="mt-3 flex gap-2"
            onSubmit={(event) => {
              event.preventDefault()
              sendUserMessage(state.userInput)
            }}
          >
            <input
              value={state.userInput}
              onChange={(event) => setUserInput(event.target.value)}
              className="flex-1 bg-lapis-bg text-lapis-text placeholder:text-lapis-text-secondary border border-lapis-border rounded-lg px-3 py-2 text-sm"
              placeholder="Example: add an action to unstack a block"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-lapis-accent text-black font-semibold text-sm disabled:opacity-50"
              disabled={state.isLoading || !state.userInput.trim()}
            >
              Send
            </button>
          </form>

          {/* Agent action status */}
          {state.agentAction && (
            <div className="mt-2 flex items-center gap-2 text-xs text-lapis-text-secondary">
              <Loader2 className="w-3 h-3 animate-spin text-lapis-accent" />
              <span>{state.agentAction}</span>
            </div>
          )}
        </div>

        {/* PDDL text editors */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <PDDLEditor
            title="Domain PDDL"
            value={state.domainPddl}
            onChange={(nextValue) => syncFromText(nextValue, state.problemPddl)}
          />

          <PDDLEditor
            title="Problem PDDL"
            value={state.problemPddl}
            onChange={(nextValue) => syncFromText(state.domainPddl, nextValue)}
            issues={problemIssues}
          />
        </div>

        <div className="rounded-xl border border-lapis-border bg-lapis-card p-3 flex items-center justify-between text-xs">
          <span className="text-lapis-text-secondary">Verification Status</span>
          <span className={state.verification?.valid ? 'text-emerald-400' : 'text-yellow-300'}>
            {state.verification?.valid ? 'PASS' : 'CHECK REQUIRED'}
          </span>
          <span className="text-red-300">Errors: {state.verification?.errors.length || 0}</span>
          <span className="text-yellow-200">Warnings: {state.verification?.warnings.length || 0}</span>
        </div>

        {state.error && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
            {state.error}
          </div>
        )}
      </section>

      {/* Right column: verification + visualizer */}
      <section className="xl:col-span-2 space-y-4">
        <div className="rounded-xl border border-lapis-border bg-lapis-card p-4">
          <h3 className="text-sm font-semibold mb-2">Verification</h3>
          <p className="text-xs text-lapis-text-secondary mb-3">
            Run checks against current domain and problem to catch semantic issues early.
          </p>
          <button
            type="button"
            className="px-3 py-2 rounded-lg bg-lapis-accent text-black text-sm font-semibold disabled:opacity-50"
            onClick={runVerification}
            disabled={state.isLoading}
          >
            {state.isLoading ? 'Working...' : 'Run Verification'}
          </button>
        </div>

        {state.verification && (
          <VerificationPanel
            valid={state.verification.valid}
            errors={state.verification.errors}
            warnings={state.verification.warnings}
          />
        )}

        {/* Domain-specific visualizer */}
        <DomainVisualizer
          domain={domain}
          problemPddl={state.problemPddl}
          onProblemChange={(updated) => syncFromGraphical(state.domainPddl, updated)}
        />
      </section>
    </div>
  )
}
