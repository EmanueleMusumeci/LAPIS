import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  Bot, CheckCircle2, AlertTriangle, Wifi, WifiOff, Loader2,
  ChevronDown, ChevronRight, Play, Wrench, Brain,
} from 'lucide-react'
import { useAgenticEditor } from '@/hooks/useAgenticEditor'
import { usePresets } from '@/hooks/usePresets'
import GridworldEditor from '@/components/editors/GridworldEditor'
import BlocksworldEditor from '@/components/editors/BlocksworldEditor'
import PDDLEditor, { type PDDLIssue } from '@/components/PDDLEditor'
import PresetSelector from '@/components/PresetSelector'
import PlanTrace from '@/components/PlanTrace'
import { extractIssueLine } from '@/lib/pddlPatch'
import { ApiKeyInput } from '@/contexts/ApiKeyContext'
import { runPlanner, simulateSteps, simulateFrames, type SimStepsResult, type SimFramesResult } from '@/lib/api'

// ─── Domain detection ─────────────────────────────────────────────────────────

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

// ─── Chat message types ───────────────────────────────────────────────────────

interface ThinkingBubbleProps {
  text: string
}

function ThinkingBubble({ text }: ThinkingBubbleProps) {
  const [open, setOpen] = useState(false)
  return (
    <div className="flex items-start gap-2 my-1">
      <Brain className="w-3.5 h-3.5 text-lapis-muted mt-0.5 flex-shrink-0" />
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="text-xs text-lapis-muted hover:text-lapis-text-secondary flex items-center gap-1 transition-colors"
      >
        {open ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        Thinking
      </button>
      {open && (
        <div className="mt-1 ml-5 rounded border border-lapis-border bg-lapis-background/30 p-2 text-xs text-lapis-text-secondary font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
          {text}
        </div>
      )}
    </div>
  )
}

interface ToolUseBubbleProps {
  name: string
  content: string
}

function ToolUseBubble({ name, content }: ToolUseBubbleProps) {
  const [open, setOpen] = useState(false)
  return (
    <div className="flex items-start gap-2 my-1">
      <Wrench className="w-3.5 h-3.5 text-lapis-muted mt-0.5 flex-shrink-0" />
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="text-xs text-lapis-muted hover:text-lapis-text-secondary flex items-center gap-1 transition-colors"
      >
        {open ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        Tool: <span className="font-mono">{name}</span>
      </button>
      {open && (
        <div className="mt-1 ml-5 rounded border border-lapis-border bg-lapis-background/30 p-2 text-xs text-lapis-text-secondary font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
          {content}
        </div>
      )}
    </div>
  )
}

// ─── Chat bubble ──────────────────────────────────────────────────────────────

interface ChatBubbleProps {
  role: 'user' | 'agent'
  text: string
}

/**
 * Parse text for special blocks:
 * - <thinking>...</thinking> → collapsed ThinkingBubble
 * - <tool_use name="...">...</tool_use> → collapsed ToolUseBubble
 */
function parseAgentBlocks(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  let remaining = text

  const Md = ({ text, k }: { text: string; k: number }) => (
    <div key={k} className="prose prose-invert prose-sm max-w-none text-lapis-text">
      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  )

  while (remaining.length > 0) {
    const thinkStart = remaining.indexOf('<thinking>')
    const toolStart = remaining.indexOf('<tool_use')

    const firstTag = Math.min(
      thinkStart === -1 ? Infinity : thinkStart,
      toolStart === -1 ? Infinity : toolStart,
    )

    if (firstTag === Infinity) {
      if (remaining.trim()) {
        nodes.push(<Md key={nodes.length} text={remaining} k={nodes.length} />)
      }
      break
    }

    if (firstTag > 0) {
      const prose = remaining.slice(0, firstTag)
      if (prose.trim()) nodes.push(<Md key={nodes.length} text={prose} k={nodes.length} />)
    }

    if (firstTag === thinkStart) {
      const end = remaining.indexOf('</thinking>', thinkStart)
      if (end === -1) {
        nodes.push(<Md key={nodes.length} text={remaining.slice(thinkStart)} k={nodes.length} />)
        break
      }
      const inner = remaining.slice(thinkStart + '<thinking>'.length, end)
      nodes.push(<ThinkingBubble key={nodes.length} text={inner} />)
      remaining = remaining.slice(end + '</thinking>'.length)
    } else {
      const nameMatch = remaining.slice(toolStart).match(/^<tool_use\s+name="([^"]*)"[^>]*>/)
      const toolName = nameMatch ? nameMatch[1] : 'unknown'
      const end = remaining.indexOf('</tool_use>', toolStart)
      if (end === -1) {
        nodes.push(<Md key={nodes.length} text={remaining.slice(toolStart)} k={nodes.length} />)
        break
      }
      const tagLen = nameMatch ? nameMatch[0].length : '<tool_use>'.length
      const inner = remaining.slice(toolStart + tagLen, end)
      nodes.push(<ToolUseBubble key={nodes.length} name={toolName} content={inner} />)
      remaining = remaining.slice(end + '</tool_use>'.length)
    }
  }

  return nodes
}

function ChatBubble({ role, text }: ChatBubbleProps) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-2`}>
      {!isUser && (
        <div className="w-6 h-6 rounded-full bg-lapis-accent/20 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Bot className="w-3.5 h-3.5 text-lapis-accent" />
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm ${
          isUser
            ? 'bg-lapis-accent/20 text-lapis-text rounded-tr-sm'
            : 'bg-lapis-card border border-lapis-border text-lapis-text rounded-tl-sm'
        }`}
      >
        {isUser ? (
          <span>{text}</span>
        ) : (
          <div className="space-y-1">{parseAgentBlocks(text)}</div>
        )}
      </div>
    </div>
  )
}

// ─── Verification panel ───────────────────────────────────────────────────────

function VerificationPanel({
  valid,
  errors,
  warnings,
  onFixWithAgent,
}: {
  valid: boolean
  errors: string[]
  warnings: string[]
  onFixWithAgent?: (msg: string) => void
}) {
  const hasIssues = errors.length > 0 || warnings.length > 0

  const handleFix = () => {
    if (!onFixWithAgent) return
    const parts: string[] = ['Please fix the following PDDL issues:']
    if (errors.length > 0) {
      parts.push('Errors:\n' + errors.map((e) => `- ${e}`).join('\n'))
    }
    if (warnings.length > 0) {
      parts.push('Warnings:\n' + warnings.map((w) => `- ${w}`).join('\n'))
    }
    onFixWithAgent(parts.join('\n\n'))
  }

  return (
    <div className="rounded-xl border border-lapis-border bg-lapis-card p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold">
          {valid ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <AlertTriangle className="w-4 h-4 text-yellow-500" />}
          <span>{valid ? 'Verification passed' : 'Verification requires attention'}</span>
        </div>
        {hasIssues && onFixWithAgent && (
          <button
            type="button"
            onClick={handleFix}
            className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-lapis-accent/20 text-lapis-accent text-xs font-medium hover:bg-lapis-accent/30 transition-colors"
          >
            <Bot className="w-3 h-3" />
            Fix with Agent
          </button>
        )}
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

// ─── Planner panel ────────────────────────────────────────────────────────────

type PlannerStatus = 'idle' | 'running' | 'simulating' | 'done' | 'error'

function PlannerPanel({
  domainPddl,
  problemPddl,
  domainName,
}: {
  domainPddl: string
  problemPddl: string
  domainName: string
}) {
  const [planner, setPlanner] = useState('up_fd')
  const [status, setStatus] = useState<PlannerStatus>('idle')
  const [plan, setPlan] = useState<string[]>([])
  const [simSteps, setSimSteps] = useState<SimStepsResult | null>(null)
  const [simFrames, setSimFrames] = useState<SimFramesResult | null>(null)
  const [error, setError] = useState('')

  const handleRun = async () => {
    setStatus('running')
    setError('')
    setPlan([])
    setSimSteps(null)
    setSimFrames(null)
    try {
      const res = await runPlanner({ domain_pddl: domainPddl, problem_pddl: problemPddl, planner })
      if (!res.success) {
        setError(res.error || 'Planner failed')
        setStatus('error')
        return
      }
      setPlan(res.plan)

      if (res.plan.length > 0) {
        setStatus('simulating')
        // Try graphical frames first (available for all IPC domains)
        if (domainName !== 'custom') {
          try {
            const frames = await simulateFrames({
              domain_pddl: domainPddl,
              problem_pddl: problemPddl,
              plan: res.plan,
              domain_name: domainName,
            })
            if (frames.success && frames.frames.length > 0) {
              setSimFrames(frames)
            }
          } catch {
            // Frames not available — fall through to state-diff
          }
        }
        // Also get state diffs as fallback / supplementary
        try {
          const sim = await simulateSteps({ domain_pddl: domainPddl, problem_pddl: problemPddl, plan: res.plan })
          if (sim.success) setSimSteps(sim)
        } catch {
          // Non-fatal
        }
      }
      setStatus('done')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setStatus('error')
    }
  }

  const busyLabel = status === 'running' ? 'Planning...' : status === 'simulating' ? 'Simulating...' : null

  return (
    <div className="rounded-xl border border-lapis-border bg-lapis-card p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Classical Planner</h3>
        <div className="flex items-center gap-2">
          <select
            className="bg-lapis-bg border border-lapis-border rounded px-2 py-1 text-xs text-lapis-text"
            value={planner}
            onChange={(e) => setPlanner(e.target.value)}
            disabled={!!busyLabel}
          >
            <option value="up_fd">Fast Downward</option>
            <option value="pyperplan">Pyperplan</option>
          </select>
          <button
            type="button"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-lapis-accent text-black text-xs font-semibold disabled:opacity-50"
            onClick={handleRun}
            disabled={!!busyLabel}
          >
            {busyLabel ? (
              <><Loader2 className="w-3 h-3 animate-spin" /> {busyLabel}</>
            ) : (
              <><Play className="w-3 h-3" /> {plan.length > 0 ? 'Re-run' : 'Run Planner'}</>
            )}
          </button>
        </div>
      </div>

      {status === 'error' && (
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-200">
          {error}
        </div>
      )}

      {status === 'done' && plan.length === 0 && (
        <p className="text-xs text-lapis-text-secondary">Planner returned an empty plan (goal already satisfied?).</p>
      )}

      {status === 'done' && plan.length > 0 && (
        <PlanTrace
          actions={plan}
          problemPddl={problemPddl}
          domainName={domainName}
          simSteps={simSteps ?? undefined}
          simFrames={simFrames ?? undefined}
        />
      )}
    </div>
  )
}

// ─── Domain visualizer (only for domains with interactive editors) ────────────

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

  // Scroll chat to bottom when new messages arrive
  const chatRef = (el: HTMLDivElement | null) => {
    if (el) el.scrollTop = el.scrollHeight
  }

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

        {/* Chat panel */}
        <div className="rounded-xl border border-lapis-border bg-lapis-card p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-lapis-accent" />
              <h2 className="text-lg font-semibold">Agent Chat</h2>
            </div>
            <div className="flex items-center gap-2 text-xs text-lapis-text-secondary">
              {state.connected ? <Wifi className="w-4 h-4 text-green-500" /> : <WifiOff className="w-4 h-4 text-red-400" />}
              <span>{state.connected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>

          {/* Chat history */}
          <div
            ref={chatRef}
            className="h-64 overflow-y-auto rounded-lg border border-lapis-border bg-lapis-background/40 p-3 space-y-3"
          >
            {state.chat.length === 0 && (
              <p className="text-sm text-lapis-text-secondary text-center mt-8">
                Ask the agent to modify domain or problem PDDL.
              </p>
            )}
            {state.chat.map((entry, idx) => (
              <ChatBubble key={`${entry.at}-${idx}`} role={entry.role} text={entry.text} />
            ))}
            {state.agentAction && (
              <div className="flex items-center gap-2 text-xs text-lapis-text-secondary pl-8">
                <Loader2 className="w-3 h-3 animate-spin text-lapis-accent" />
                <span>{state.agentAction}</span>
              </div>
            )}
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
              placeholder="e.g. add an unstack action, change the goal to on a b"
              disabled={!state.connected}
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-lapis-accent text-black font-semibold text-sm disabled:opacity-50"
              disabled={state.isLoading || !state.userInput.trim() || !state.connected}
            >
              Send
            </button>
          </form>

          {state.error && (
            <div className="mt-2 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-200">
              {state.error}
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
      </section>

      {/* Right column: verification + planner + visualizer */}
      <section className="xl:col-span-2 space-y-4">
        {/* Verification */}
        <div className="rounded-xl border border-lapis-border bg-lapis-card p-4">
          <h3 className="text-sm font-semibold mb-2">Verification</h3>
          <p className="text-xs text-lapis-text-secondary mb-3">
            Check domain and problem for semantic issues.
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
            onFixWithAgent={sendUserMessage}
          />
        )}

        {/* Classical planner + step-through */}
        <PlannerPanel
          domainPddl={state.domainPddl}
          problemPddl={state.problemPddl}
          domainName={domain}
        />

        {/* Domain-specific visualizer (editable) */}
        <DomainVisualizer
          domain={domain}
          problemPddl={state.problemPddl}
          onProblemChange={(updated) => syncFromGraphical(state.domainPddl, updated)}
        />
      </section>
    </div>
  )
}
