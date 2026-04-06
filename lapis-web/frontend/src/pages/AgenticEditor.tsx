import { Bot, CheckCircle2, AlertTriangle, Wifi, WifiOff } from 'lucide-react'
import { useAgenticEditor } from '@/hooks/useAgenticEditor'
import BlocksworldEditor from '@/components/editors/BlocksworldEditor'
import GridworldEditor from '@/components/editors/GridworldEditor'
import PDDLEditor, { type PDDLIssue } from '@/components/PDDLEditor'
import A2UIRenderer from '@/components/A2UIRenderer'
import { extractIssueLine, upsertInitPredicate } from '@/lib/pddlPatch'

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

export default function AgenticEditor() {
  const {
    state,
    setUserInput,
    sendUserMessage,
    syncFromText,
    syncFromGraphical,
    runVerification,
  } = useAgenticEditor()

  const lowerDomain = state.domainPddl.toLowerCase()
  const isBlocksworld = /blocksworld|blocks-world|\(on\s+\?/.test(lowerDomain)
  const isGridworld = /minigrid|babyai|agentinroom|objectinroom/.test(lowerDomain)

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

  const applyGraphicalPredicate = (predicate: string) => {
    const updatedProblem = upsertInitPredicate(state.problemPddl, predicate)
    syncFromGraphical(state.domainPddl, updatedProblem)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 xl:grid-cols-5 gap-4">
      <section className="xl:col-span-3 space-y-4">
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
        </div>

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
            {state.isLoading ? 'Verifying...' : 'Run Verification'}
          </button>
        </div>

        {state.verification && (
          <VerificationPanel
            valid={state.verification.valid}
            errors={state.verification.errors}
            warnings={state.verification.warnings}
          />
        )}

        {isBlocksworld && (
          <BlocksworldEditor
            problemPddl={state.problemPddl}
            onChange={(updatedProblemPddl) => syncFromGraphical(state.domainPddl, updatedProblemPddl)}
          />
        )}

        {isGridworld && (
          <GridworldEditor
            problemPddl={state.problemPddl}
            onChange={(updatedProblemPddl) => syncFromGraphical(state.domainPddl, updatedProblemPddl)}
          />
        )}

        {state.uiBlueprint && !isBlocksworld && !isGridworld && (
          <A2UIRenderer
            blueprint={state.uiBlueprint}
            onApplyPredicate={applyGraphicalPredicate}
          />
        )}

        {!isBlocksworld && !isGridworld && (
          <div className="rounded-xl border border-dashed border-lapis-border bg-lapis-card/40 p-4">
            <p className="text-sm font-semibold mb-1 text-lapis-text">Visual editor unavailable for this domain</p>
            <p className="text-xs text-lapis-text-secondary">
              Supported right now: Blocksworld and Gridworld/BabyAI style problems.
            </p>
          </div>
        )}
      </section>
    </div>
  )
}
