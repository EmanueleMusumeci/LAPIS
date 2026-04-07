/**
 * DomainStateViewer — read-only display of PDDL init facts and goal.
 * Used for domains that don't have a dedicated graphical editor.
 */
interface DomainStateViewerProps {
  domainName: string
  problemPddl: string
}

function parseFacts(section: string): string[] {
  return Array.from(section.matchAll(/\([^()]+\)/g)).map((m) => m[0].trim())
}

export default function DomainStateViewer({ domainName, problemPddl }: DomainStateViewerProps) {
  const initMatch = problemPddl.match(/\(:init([\s\S]*?)\)\s*\(:goal/i)
  const goalMatch = problemPddl.match(/\(:goal\s*([\s\S]*?)\)\s*\)$/i)

  const initFacts = initMatch ? parseFacts(initMatch[1]) : []
  const goalFacts = goalMatch ? parseFacts(goalMatch[1]) : []

  return (
    <div className="rounded-xl border border-lapis-border bg-lapis-card p-4 space-y-4">
      <div>
        <p className="text-sm font-semibold text-lapis-text capitalize">{domainName} State Viewer</p>
        <p className="text-xs text-lapis-text-secondary">Read-only view of the current problem state.</p>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-lapis-text-secondary mb-1">Init ({initFacts.length} facts)</p>
          <div className="max-h-40 overflow-y-auto rounded border border-lapis-border bg-lapis-background/40 p-2 space-y-1">
            {initFacts.length === 0 && <p className="text-xs text-lapis-text-secondary italic">No init facts parsed.</p>}
            {initFacts.map((fact, i) => (
              <div key={i} className="font-mono text-xs text-lapis-text bg-lapis-bg rounded px-2 py-0.5">{fact}</div>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-lapis-text-secondary mb-1">Goal</p>
          <div className="rounded border border-lapis-border bg-lapis-background/40 p-2 space-y-1">
            {goalFacts.length === 0 && <p className="text-xs text-lapis-text-secondary italic">No goal facts parsed.</p>}
            {goalFacts.map((fact, i) => (
              <div key={i} className="font-mono text-xs text-emerald-300 bg-lapis-bg rounded px-2 py-0.5">{fact}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
