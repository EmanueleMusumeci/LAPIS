import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  Bot, CheckCircle2, AlertTriangle, XCircle, Wifi, WifiOff, Loader2,
  ChevronDown, ChevronRight, Play, Wrench, Brain,
  KeyRound, AlertOctagon, ChevronUp,
} from 'lucide-react'
import { useAgenticEditor } from '@/hooks/useAgenticEditor'
import { usePresets } from '@/hooks/usePresets'
import PDDLEditor, { type PDDLIssue } from '@/components/PDDLEditor'
import PresetSelector from '@/components/PresetSelector'
import PlanTrace from '@/components/PlanTrace'
import { extractIssueLine } from '@/lib/pddlPatch'
import { useApiKey } from '@/contexts/ApiKeyContext'
import { runPlanner, simulateSteps, simulateFrames, type SimStepsResult, type SimFramesResult } from '@/lib/api'
import { cn } from '@/lib/utils'

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

// ─── API key popover ──────────────────────────────────────────────────────────

function ApiKeyDropdown() {
  const { apiKey, setApiKey } = useApiKey()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        title={apiKey ? 'API key set' : 'No API key set'}
        className={cn(
          'flex items-center gap-1 px-2 py-1 rounded-lg border text-xs transition-colors',
          apiKey
            ? 'border-lapis-border text-lapis-muted hover:border-lapis-accent/40 hover:text-lapis-text'
            : 'border-amber-500/50 bg-amber-500/10 text-amber-400 hover:border-amber-500/80',
        )}
      >
        <KeyRound className="w-3.5 h-3.5" />
        {!apiKey && <AlertOctagon className="w-3 h-3" />}
        {apiKey ? (
          <span className="font-mono">{apiKey.slice(0, 8)}…</span>
        ) : (
          <span>No key</span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1.5 z-50 w-72 rounded-xl border border-lapis-border bg-lapis-card shadow-xl p-3 space-y-2">
          <label className="flex items-center gap-1.5 text-xs font-medium text-lapis-muted">
            <KeyRound className="w-3 h-3" />
            API Key
            <span className="font-normal text-lapis-text-secondary">(Anthropic or OpenAI)</span>
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-ant-… or sk-…"
            autoComplete="off"
            autoFocus
            className="w-full px-3 py-2 rounded-lg bg-lapis-bg border border-lapis-border text-lapis-text text-sm font-mono placeholder:text-lapis-text-secondary focus:outline-none focus:border-lapis-accent"
          />
          {apiKey ? (
            <p className="text-xs text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              Key set ({apiKey.startsWith('sk-ant') ? 'Anthropic' : 'OpenAI'})
            </p>
          ) : (
            <p className="text-xs text-amber-400 flex items-center gap-1">
              <AlertOctagon className="w-3 h-3" />
              Required to run the agent
            </p>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Chat message types ───────────────────────────────────────────────────────

function ThinkingBubble({ text }: { text: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="my-1">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-lapis-muted hover:text-lapis-text-secondary transition-colors"
      >
        <Brain className="w-3 h-3 flex-shrink-0" />
        {open ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        Thinking
      </button>
      {open && (
        <div className="mt-1 ml-5 rounded border border-lapis-border bg-lapis-bg/40 p-2 text-xs text-lapis-text-secondary font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
          {text}
        </div>
      )}
    </div>
  )
}

function ToolUseBubble({ name, content }: { name: string; content: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="my-1">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-lapis-muted hover:text-lapis-text-secondary transition-colors"
      >
        <Wrench className="w-3 h-3 flex-shrink-0" />
        {open ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        Tool: <span className="font-mono">{name}</span>
      </button>
      {open && (
        <div className="mt-1 ml-5 rounded border border-lapis-border bg-lapis-bg/40 p-2 text-xs text-lapis-text-secondary font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
          {content}
        </div>
      )}
    </div>
  )
}

function parseAgentBlocks(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  let remaining = text

  const Md = ({ text: t, k }: { text: string; k: number }) => (
    <div key={k} className="prose prose-invert prose-sm max-w-none text-lapis-text">
      <ReactMarkdown>{t}</ReactMarkdown>
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
      if (remaining.trim()) nodes.push(<Md key={nodes.length} text={remaining} k={nodes.length} />)
      break
    }
    if (firstTag > 0) {
      const prose = remaining.slice(0, firstTag)
      if (prose.trim()) nodes.push(<Md key={nodes.length} text={prose} k={nodes.length} />)
    }
    if (firstTag === thinkStart) {
      const end = remaining.indexOf('</thinking>', thinkStart)
      if (end === -1) { nodes.push(<Md key={nodes.length} text={remaining.slice(thinkStart)} k={nodes.length} />); break }
      nodes.push(<ThinkingBubble key={nodes.length} text={remaining.slice(thinkStart + '<thinking>'.length, end)} />)
      remaining = remaining.slice(end + '</thinking>'.length)
    } else {
      const nameMatch = remaining.slice(toolStart).match(/^<tool_use\s+name="([^"]*)"[^>]*>/)
      const toolName = nameMatch ? nameMatch[1] : 'unknown'
      const end = remaining.indexOf('</tool_use>', toolStart)
      if (end === -1) { nodes.push(<Md key={nodes.length} text={remaining.slice(toolStart)} k={nodes.length} />); break }
      const tagLen = nameMatch ? nameMatch[0].length : '<tool_use>'.length
      nodes.push(<ToolUseBubble key={nodes.length} name={toolName} content={remaining.slice(toolStart + tagLen, end)} />)
      remaining = remaining.slice(end + '</tool_use>'.length)
    }
  }
  return nodes
}

function ChatBubble({ role, text }: { role: 'user' | 'agent'; text: string }) {
  const isUser = role === 'user'
  return (
    <div className={cn('flex gap-2', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser && (
        <div className="w-6 h-6 rounded-full bg-lapis-accent/20 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Bot className="w-3.5 h-3.5 text-lapis-accent" />
        </div>
      )}
      <div className={cn(
        'max-w-[82%] rounded-2xl px-3 py-2 text-sm',
        isUser
          ? 'bg-lapis-accent/20 text-lapis-text rounded-tr-sm'
          : 'bg-lapis-card border border-lapis-border text-lapis-text rounded-tl-sm',
      )}>
        {isUser ? <span>{text}</span> : <div className="space-y-1">{parseAgentBlocks(text)}</div>}
      </div>
    </div>
  )
}

// ─── Collapsible panel card ───────────────────────────────────────────────────
/**
 * Generic collapsible card for the bottom tool strip.
 * Collapsed: shows header + a fixed-height tinted preview area.
 * Expanded: shows full content.
 */
interface PanelCardProps {
  title: string
  icon: React.ReactNode
  badges?: React.ReactNode[]
  preview?: string   // short text shown in collapsed preview
  defaultOpen?: boolean
  className?: string
  children: React.ReactNode
}

function PanelCard({ title, icon, badges = [], preview, defaultOpen = false, className, children }: PanelCardProps) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className={cn('rounded-xl border border-lapis-border bg-lapis-card overflow-hidden', className)}>
      {/* Header */}
      <button
        type="button"
        className="w-full flex items-center gap-2 px-4 py-3 text-sm font-semibold text-lapis-text hover:bg-lapis-bg/30 transition-colors"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="text-lapis-accent">{icon}</span>
        <span className="flex-1 text-left">{title}</span>
        {badges.map((b, i) => <span key={i}>{b}</span>)}
        {open ? <ChevronUp className="w-4 h-4 text-lapis-muted" /> : <ChevronDown className="w-4 h-4 text-lapis-muted" />}
      </button>

      {/* Collapsed preview */}
      {!open && preview && (
        <div className="relative mx-4 mb-3 rounded-lg border border-lapis-border bg-lapis-bg/40 overflow-hidden h-24">
          <pre className="p-2 text-xs font-mono text-lapis-text-secondary whitespace-pre-wrap leading-5">{preview}</pre>
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-lapis-card to-transparent" />
        </div>
      )}

      {/* Expanded content */}
      {open && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  )
}

// ─── Verification card ────────────────────────────────────────────────────────

function VerificationCard({
  verification,
  isLoading,
  onRun,
  onFixWithAgent,
}: {
  verification: { valid: boolean; errors: string[]; warnings: string[] } | null
  isLoading: boolean
  onRun: () => void
  onFixWithAgent: (msg: string) => void
}) {
  const hasResult = verification !== null
  const errors = verification?.errors ?? []
  const warnings = verification?.warnings ?? []

  const handleFix = () => {
    const parts: string[] = ['Please fix the following PDDL issues:']
    if (errors.length > 0) parts.push('Errors:\n' + errors.map((e) => `- ${e}`).join('\n'))
    if (warnings.length > 0) parts.push('Warnings:\n' + warnings.map((w) => `- ${w}`).join('\n'))
    onFixWithAgent(parts.join('\n\n'))
  }

  const preview = hasResult
    ? [
        errors.length > 0 ? `Errors (${errors.length}):\n` + errors.slice(0, 3).map((e) => `  • ${e}`).join('\n') : null,
        warnings.length > 0 ? `Warnings (${warnings.length}):\n` + warnings.slice(0, 2).map((w) => `  • ${w}`).join('\n') : null,
        errors.length === 0 && warnings.length === 0 ? 'All checks passed.' : null,
      ].filter(Boolean).join('\n\n')
    : undefined

  const badges = [
    hasResult && (
      <span key="status" className={cn(
        'flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border font-medium',
        verification!.valid
          ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400'
          : 'border-yellow-500/40 bg-yellow-500/10 text-yellow-400',
      )}>
        {verification!.valid
          ? <><CheckCircle2 className="w-3 h-3" /> Pass</>
          : <><AlertTriangle className="w-3 h-3" /> Issues</>
        }
      </span>
    ),
    hasResult && errors.length > 0 && (
      <span key="errors" className="text-xs px-2 py-0.5 rounded-full border border-red-500/40 bg-red-500/10 text-red-400 font-medium">
        {errors.length} error{errors.length !== 1 ? 's' : ''}
      </span>
    ),
    hasResult && warnings.length > 0 && (
      <span key="warnings" className="text-xs px-2 py-0.5 rounded-full border border-yellow-500/40 bg-yellow-500/10 text-yellow-400 font-medium">
        {warnings.length} warn
      </span>
    ),
    <span key="semantic" className="text-xs px-1.5 py-0.5 rounded border border-lapis-border text-lapis-muted">
      semantic
    </span>,
    <span key="val" className="text-xs px-1.5 py-0.5 rounded border border-lapis-border text-lapis-muted">
      VAL
    </span>,
  ].filter(Boolean) as React.ReactNode[]

  return (
    <PanelCard
      title="Verification"
      icon={<CheckCircle2 className="w-4 h-4" />}
      badges={badges}
      preview={preview}
      defaultOpen={hasResult && !verification!.valid}
    >
      <div className="space-y-3 pt-1">
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-lapis-accent text-black text-sm font-semibold disabled:opacity-50"
            onClick={onRun}
            disabled={isLoading}
          >
            {isLoading ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Running…</> : 'Run Verification'}
          </button>
          {hasResult && errors.length + warnings.length > 0 && (
            <button
              type="button"
              onClick={handleFix}
              className="flex items-center gap-1.5 px-2 py-2 rounded-lg bg-lapis-accent/20 text-lapis-accent text-xs font-medium hover:bg-lapis-accent/30 transition-colors"
            >
              <Bot className="w-3 h-3" />
              Fix with Agent
            </button>
          )}
        </div>

        {hasResult && (
          <>
            {errors.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-red-400 mb-1.5 flex items-center gap-1">
                  <XCircle className="w-3 h-3" /> Errors
                </p>
                <ul className="space-y-1">
                  {errors.map((err, i) => (
                    <li key={i} className="text-sm text-red-300 font-mono bg-red-500/5 rounded px-2 py-1">{err}</li>
                  ))}
                </ul>
              </div>
            )}
            {warnings.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-yellow-400 mb-1.5 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Warnings
                </p>
                <ul className="space-y-1">
                  {warnings.map((warn, i) => (
                    <li key={i} className="text-sm text-yellow-200 font-mono bg-yellow-500/5 rounded px-2 py-1">{warn}</li>
                  ))}
                </ul>
              </div>
            )}
            {errors.length === 0 && warnings.length === 0 && (
              <p className="text-sm text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> All checks passed.
              </p>
            )}
          </>
        )}
      </div>
    </PanelCard>
  )
}

// ─── Planner card ─────────────────────────────────────────────────────────────

type PlannerStatus = 'idle' | 'running' | 'simulating' | 'done' | 'error'

function PlannerCard({
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
      if (!res.success) { setError(res.error || 'Planner failed'); setStatus('error'); return }
      setPlan(res.plan)
      if (res.plan.length > 0) {
        setStatus('simulating')
        if (domainName !== 'custom') {
          try {
            const frames = await simulateFrames({ domain_pddl: domainPddl, problem_pddl: problemPddl, plan: res.plan, domain_name: domainName })
            if (frames.success && frames.frames.length > 0) setSimFrames(frames)
          } catch { /* fall through */ }
        }
        try {
          const sim = await simulateSteps({ domain_pddl: domainPddl, problem_pddl: problemPddl, plan: res.plan })
          if (sim.success) setSimSteps(sim)
        } catch { /* non-fatal */ }
      }
      setStatus('done')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setStatus('error')
    }
  }

  const busyLabel = status === 'running' ? 'Planning…' : status === 'simulating' ? 'Simulating…' : null

  const planPreview = plan.length > 0
    ? plan.slice(0, 6).map((a, i) => `${String(i + 1).padStart(2)}. ${a}`).join('\n') + (plan.length > 6 ? `\n    … +${plan.length - 6} more` : '')
    : undefined

  const badges = [
    plan.length > 0 && (
      <span key="steps" className="text-xs px-2 py-0.5 rounded-full border border-lapis-accent/40 bg-lapis-accent/10 text-lapis-accent font-medium">
        {plan.length} step{plan.length !== 1 ? 's' : ''}
      </span>
    ),
    (simFrames?.success || simSteps?.success) && (
      <span key="sim" className="text-xs px-1.5 py-0.5 rounded border border-violet-500/40 bg-violet-500/10 text-violet-400">
        simulated
      </span>
    ),
    status === 'error' && (
      <span key="err" className="text-xs px-2 py-0.5 rounded-full border border-red-500/40 bg-red-500/10 text-red-400 font-medium">
        error
      </span>
    ),
  ].filter(Boolean) as React.ReactNode[]

  return (
    <PanelCard
      title="Planner + Trace"
      icon={<Play className="w-4 h-4" />}
      badges={badges}
      preview={planPreview}
      defaultOpen={status === 'done' || status === 'error'}
    >
      <div className="space-y-4 pt-1">
        <div className="flex items-center gap-2">
          <select
            className="bg-lapis-bg border border-lapis-border rounded px-2 py-1.5 text-xs text-lapis-text"
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
            {busyLabel
              ? <><Loader2 className="w-3 h-3 animate-spin" /> {busyLabel}</>
              : <><Play className="w-3 h-3" /> {plan.length > 0 ? 'Re-run' : 'Run Planner'}</>
            }
          </button>
        </div>

        {status === 'error' && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-200">{error}</div>
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
    </PanelCard>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function AgenticEditor() {
  const {
    state,
    setUserInput,
    sendUserMessage,
    syncFromText,
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

  const chatEndRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state.chat, state.agentAction])

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-4">

      {/* Preset selector */}
      <PresetSelector
        presets={presets}
        selectedPreset={state.selectedPreset}
        onPresetChange={loadPreset}
      />

      {/* Top row: chat | PDDL editors */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">

        {/* Chat */}
        <div className="xl:col-span-2 rounded-xl border border-lapis-border bg-lapis-card flex flex-col">
          {/* Chat header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-lapis-border">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-lapis-accent" />
              <h2 className="text-base font-semibold">Agent Chat</h2>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 text-xs text-lapis-text-secondary">
                {state.connected
                  ? <Wifi className="w-3.5 h-3.5 text-green-500" />
                  : <WifiOff className="w-3.5 h-3.5 text-red-400" />}
                <span>{state.connected ? 'Connected' : 'Disconnected'}</span>
              </div>
              <ApiKeyDropdown />
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3" style={{ maxHeight: '420px' }}>
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
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-lapis-border p-3 space-y-2">
            <form
              className="flex gap-2"
              onSubmit={(e) => { e.preventDefault(); sendUserMessage(state.userInput) }}
            >
              <input
                value={state.userInput}
                onChange={(e) => setUserInput(e.target.value)}
                className="flex-1 bg-lapis-bg text-lapis-text placeholder:text-lapis-text-secondary border border-lapis-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-lapis-accent"
                placeholder="e.g. add an unstack action, change the goal…"
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
              <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-200">
                {state.error}
              </div>
            )}
          </div>
        </div>

        {/* PDDL editors */}
        <div className="xl:col-span-3 grid grid-cols-1 lg:grid-cols-2 gap-4 content-start">
          <PDDLEditor
            title="Domain PDDL"
            value={state.domainPddl}
            onChange={(v) => syncFromText(v, state.problemPddl)}
          />
          <PDDLEditor
            title="Problem PDDL"
            value={state.problemPddl}
            onChange={(v) => syncFromText(state.domainPddl, v)}
            issues={problemIssues}
          />
        </div>
      </div>

      {/* Bottom row: verification + planner */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        <div className="xl:col-span-2">
          <VerificationCard
            verification={state.verification ?? null}
            isLoading={state.isLoading}
            onRun={runVerification}
            onFixWithAgent={sendUserMessage}
          />
        </div>

        <div className="xl:col-span-3">
          <PlannerCard
            domainPddl={state.domainPddl}
            problemPddl={state.problemPddl}
            domainName={domain}
          />
        </div>
      </div>
    </div>
  )
}
