/**
 * StageCard - Expandable card showing pipeline stage status and content.
 */
import { useState, useMemo } from 'react'
import {
  Wrench,
  Search,
  ClipboardList,
  Cog,
  ChevronDown,
  ChevronRight,
  Clock,
  AlertCircle,
  Diff,
} from 'lucide-react'
import { cn, formatDuration, truncate } from '@/lib/utils'
import type { StageResult, StageStatus } from '@/types'

// ─── Line-level diff ──────────────────────────────────────────────────────────

interface DiffLine {
  type: 'same' | 'added' | 'removed'
  text: string
}

function computeLineDiff(before: string, after: string): DiffLine[] {
  const bLines = before.split('\n')
  const aLines = after.split('\n')

  // Simple LCS-based diff (Patience-style via DP)
  const m = bLines.length
  const n = aLines.length

  // Build LCS table
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0))
  for (let i = m - 1; i >= 0; i--) {
    for (let j = n - 1; j >= 0; j--) {
      if (bLines[i] === aLines[j]) {
        dp[i][j] = dp[i + 1][j + 1] + 1
      } else {
        dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1])
      }
    }
  }

  const result: DiffLine[] = []
  let i = 0, j = 0
  while (i < m || j < n) {
    if (i < m && j < n && bLines[i] === aLines[j]) {
      result.push({ type: 'same', text: bLines[i] })
      i++; j++
    } else if (j < n && (i >= m || dp[i + 1]?.[j] <= dp[i]?.[j + 1])) {
      result.push({ type: 'added', text: aLines[j] })
      j++
    } else {
      result.push({ type: 'removed', text: bLines[i] })
      i++
    }
  }
  return result
}

function PddlDiff({ before, after }: { before: string; after: string }) {
  const lines = useMemo(() => computeLineDiff(before, after), [before, after])
  const hasChanges = lines.some((l) => l.type !== 'same')

  if (!hasChanges) {
    return <p className="text-xs text-lapis-text-secondary italic">No changes</p>
  }

  return (
    <div className="font-mono text-xs max-h-72 overflow-auto rounded bg-lapis-bg border border-lapis-border p-2 space-y-0">
      {lines.map((line, i) => (
        <div
          key={i}
          className={cn(
            'whitespace-pre px-1 leading-5',
            line.type === 'added' && 'bg-emerald-900/30 text-emerald-300',
            line.type === 'removed' && 'bg-red-900/30 text-red-300 line-through opacity-70',
            line.type === 'same' && 'text-lapis-text-secondary',
          )}
        >
          <span className="select-none mr-1 opacity-50">
            {line.type === 'added' ? '+' : line.type === 'removed' ? '−' : ' '}
          </span>
          {line.text || ' '}
        </div>
      ))}
    </div>
  )
}

const STAGE_ICONS: Record<string, React.ReactNode> = {
  'Domain Generation': <Wrench className="w-4 h-4" />,
  'Domain Adequacy Check': <Search className="w-4 h-4" />,
  'Problem Generation': <ClipboardList className="w-4 h-4" />,
  'Planning + Refinement': <Cog className="w-4 h-4" />,
}

const STATUS_BADGES: Record<StageStatus, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'badge-pending' },
  running: { label: 'Running', className: 'badge-running' },
  done: { label: 'Done', className: 'badge-done' },
  error: { label: 'Error', className: 'badge-error' },
  skipped: { label: 'Skipped', className: 'badge-skipped' },
}

interface StageCardProps {
  stage: StageResult
  defaultExpanded?: boolean
  /** PDDL from the preceding stage, used to show a diff toggle */
  prevDomainPddl?: string
  prevProblemPddl?: string
  className?: string
}

export function StageCard({ stage, defaultExpanded = false, prevDomainPddl, prevProblemPddl, className }: StageCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const [showDomainDiff, setShowDomainDiff] = useState(false)
  const [showProblemDiff, setShowProblemDiff] = useState(false)
  const [showRefineDiff, setShowRefineDiff] = useState<number | null>(null)

  const icon = STAGE_ICONS[stage.name] || <Cog className="w-4 h-4" />
  const badge = STATUS_BADGES[stage.status]

  // Generate preview text based on stage type and status
  const getPreview = (): string => {
    if (stage.status === 'error') {
      return stage.error_msg || 'Unknown error'
    }

    if (stage.status === 'running') {
      return stage.adequacy_analysis || 'Processing...'
    }

    if (stage.status === 'done' || stage.status === 'skipped') {
      if (stage.name === 'Domain Generation' || stage.name === 'Domain Adequacy Check') {
        return stage.domain_pddl || ''
      }
      if (stage.name === 'Problem Generation') {
        return stage.problem_pddl || ''
      }
      if (stage.name === 'Planning + Refinement') {
        return stage.plan_actions.slice(0, 4).join('\n') || ''
      }
    }

    return ''
  }

  const preview = getPreview()
  const hasContent = preview.length > 0 || stage.domain_pddl || stage.problem_pddl || stage.plan_actions.length > 0

  // Compute whether a diff is available (for header badge)
  const hasDomainDiff = !!(prevDomainPddl && prevDomainPddl !== stage.domain_pddl && stage.domain_pddl)
  const hasProblemDiff = !!(prevProblemPddl && prevProblemPddl !== stage.problem_pddl && stage.problem_pddl)

  return (
    <div className={cn('stage-card', stage.status, className)}>
      {/* Header */}
      <div className="flex items-center gap-2 select-none">
        {/* Expand toggle */}
        <div
          className="flex items-center gap-2 flex-1 cursor-pointer"
          onClick={() => hasContent && setIsExpanded(!isExpanded)}
        >
          {hasContent && (
            <span className="text-lapis-muted">
              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </span>
          )}
          <span className="text-lapis-accent">{icon}</span>
          <span className="font-semibold">{stage.name}</span>
        </div>

        {/* Diff button — always visible in header when a diff exists */}
        {(hasDomainDiff || hasProblemDiff) && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              if (hasDomainDiff) setShowDomainDiff((v) => !v)
              if (hasProblemDiff) setShowProblemDiff((v) => !v)
              // Ensure card is expanded when diff is shown
              if (!isExpanded) setIsExpanded(true)
            }}
            title="Show diff vs previous stage"
            className={cn(
              'flex items-center gap-1 text-xs px-2 py-0.5 rounded border transition-colors flex-shrink-0',
              (showDomainDiff || showProblemDiff)
                ? 'border-lapis-accent/60 bg-lapis-accent/10 text-lapis-accent'
                : 'border-lapis-border text-lapis-text-secondary hover:border-lapis-accent/40 hover:text-lapis-text',
            )}
          >
            <Diff className="w-3 h-3" />
            Diff
          </button>
        )}

        {stage.domain_amended && (
          <span className="text-xs px-1.5 py-0.5 rounded border border-amber-500/40 bg-amber-500/10 text-amber-400">amended</span>
        )}
        {stage.problem_amended && (
          <span className="text-xs px-1.5 py-0.5 rounded border border-amber-500/40 bg-amber-500/10 text-amber-400">amended</span>
        )}

        <span className={cn('badge', badge.className)}>{badge.label}</span>

        {stage.duration > 0 && (
          <span className="flex items-center gap-1 text-xs text-lapis-muted">
            <Clock className="w-3 h-3" />
            {formatDuration(stage.duration)}
          </span>
        )}
      </div>

      {/* Preview (collapsed) — larger, shows more PDDL */}
      {!isExpanded && preview && (
        <div className="relative mt-2 overflow-hidden rounded border border-lapis-border/50 bg-lapis-bg/40">
          <pre className={cn(
            'font-mono text-xs p-2.5 whitespace-pre-wrap leading-5',
            stage.status === 'error' ? 'text-red-400' : 'text-lapis-text-secondary',
          )}>
            {truncate(preview, 600)}
          </pre>
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-lapis-card to-transparent pointer-events-none" />
        </div>
      )}

      {/* Expanded content */}
      {isExpanded && hasContent && (
        <div className="mt-3 space-y-3">
          {/* Domain PDDL */}
          {(stage.name === 'Domain Generation' || stage.name === 'Domain Adequacy Check') &&
            stage.domain_pddl && (
              <div>
                <div className="text-xs font-semibold text-lapis-muted mb-1">Domain PDDL</div>
                {showDomainDiff && prevDomainPddl ? (
                  <PddlDiff before={prevDomainPddl} after={stage.domain_pddl} />
                ) : (
                  <pre className="pddl-code text-xs max-h-64 overflow-auto">{stage.domain_pddl}</pre>
                )}
              </div>
            )}

          {/* Adequacy Analysis */}
          {stage.name === 'Domain Adequacy Check' && stage.adequacy_analysis && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">Adequacy Analysis</div>
              <pre className="bg-lapis-bg/50 p-3 rounded text-xs text-lapis-text-secondary whitespace-pre-wrap">
                {stage.adequacy_analysis}
              </pre>
            </div>
          )}

          {/* CoT Steps */}
          {stage.cot_steps && stage.cot_steps.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">Chain of Thought Steps</div>
              <div className="space-y-2">
                {stage.cot_steps.map((step) => (
                  <div key={step.step} className="bg-lapis-bg/50 p-2 rounded">
                    <div className="text-xs font-semibold text-lapis-accent mb-1">
                      Step {step.step}: {step.label}
                    </div>
                    <pre className="text-xs text-lapis-text-secondary whitespace-pre-wrap">{step.content}</pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Problem PDDL */}
          {stage.name === 'Problem Generation' && stage.problem_pddl && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">Problem PDDL</div>
              {showProblemDiff && prevProblemPddl ? (
                <PddlDiff before={prevProblemPddl} after={stage.problem_pddl} />
              ) : (
                <pre className="pddl-code text-xs max-h-64 overflow-auto">{stage.problem_pddl}</pre>
              )}
            </div>
          )}

          {/* Schema Block */}
          {stage.schema_block && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">Schema Block</div>
              <pre className="bg-lapis-bg/50 p-3 rounded text-xs text-lapis-text-secondary whitespace-pre-wrap">
                {stage.schema_block}
              </pre>
            </div>
          )}

          {/* Plan Actions */}
          {stage.name === 'Planning + Refinement' && stage.plan_actions.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">
                Plan ({stage.plan_actions.length} actions)
              </div>
              <div className="space-y-1">
                {stage.plan_actions.map((action, i) => (
                  <div key={i} className="plan-step">
                    <span className="text-lapis-muted w-8 text-right">{i + 1}.</span>
                    <span>{action}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* VAL Log */}
          {stage.val_log && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">VAL Validation</div>
              <pre className="bg-lapis-bg/50 p-3 rounded text-xs text-lapis-text-secondary whitespace-pre-wrap">
                {stage.val_log}
              </pre>
            </div>
          )}

          {/* Refinement History */}
          {stage.refinement_history && stage.refinement_history.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">
                Refinement History
              </div>
              <div className="refine-terminal space-y-3">
                {stage.refinement_history.map((entry) => {
                  const hasDomainDiff = entry.domain_pddl_before && entry.domain_pddl_after && entry.domain_pddl_before !== entry.domain_pddl_after
                  const hasProblemDiff = entry.problem_pddl_before && entry.problem_pddl_after && entry.problem_pddl_before !== entry.problem_pddl_after
                  const isShowingDiff = showRefineDiff === entry.iteration

                  return (
                    <div key={entry.iteration} className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="refine-info">
                          ─── Iteration {entry.iteration}/{stage.refinement_history.length}{' '}
                          {entry.success ? '✓' : '✗'}
                        </span>
                        {(hasDomainDiff || hasProblemDiff) && (
                          <button
                            type="button"
                            onClick={() => setShowRefineDiff(isShowingDiff ? null : entry.iteration)}
                            className={cn(
                              'flex items-center gap-1 text-xs px-2 py-0.5 rounded border transition-colors',
                              isShowingDiff
                                ? 'border-lapis-accent/60 bg-lapis-accent/10 text-lapis-accent'
                                : 'border-lapis-border/60 text-lapis-text-secondary hover:border-lapis-accent/40'
                            )}
                          >
                            <Diff className="w-3 h-3" />
                            {isShowingDiff ? 'Hide diff' : 'Diff'}
                          </button>
                        )}
                      </div>
                      {entry.error && (
                        <div className="refine-err ml-4">Error: {truncate(entry.error, 200)}</div>
                      )}
                      {entry.fix && (
                        <div className="refine-ok ml-4">Fix: {truncate(entry.fix, 200)}</div>
                      )}
                      {isShowingDiff && (
                        <div className="ml-4 space-y-2">
                          {hasDomainDiff && (
                            <div>
                              <p className="text-xs text-lapis-text-secondary mb-1">Domain changes:</p>
                              <PddlDiff before={entry.domain_pddl_before} after={entry.domain_pddl_after} />
                            </div>
                          )}
                          {hasProblemDiff && (
                            <div>
                              <p className="text-xs text-lapis-text-secondary mb-1">Problem changes:</p>
                              <PddlDiff before={entry.problem_pddl_before} after={entry.problem_pddl_after} />
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Error Message */}
          {stage.status === 'error' && stage.error_msg && (
            <div className="flex items-start gap-2 p-3 rounded bg-red-500/10 border border-red-500/30">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <pre className="text-xs text-red-400 whitespace-pre-wrap">{stage.error_msg}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default StageCard
