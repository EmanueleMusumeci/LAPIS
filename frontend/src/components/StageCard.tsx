/**
 * StageCard - Expandable card showing pipeline stage status and content.
 */
import { useState } from 'react'
import {
  Wrench,
  Search,
  ClipboardList,
  Cog,
  ChevronDown,
  ChevronRight,
  Clock,
  AlertCircle,
} from 'lucide-react'
import { cn, formatDuration, truncate } from '@/lib/utils'
import type { StageResult, StageStatus } from '@/types'

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
  className?: string
}

export function StageCard({ stage, defaultExpanded = false, className }: StageCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

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

  return (
    <div className={cn('stage-card', stage.status, className)}>
      {/* Header */}
      <div
        className="flex items-center gap-2 cursor-pointer select-none"
        onClick={() => hasContent && setIsExpanded(!isExpanded)}
      >
        {hasContent && (
          <span className="text-lapis-muted">
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </span>
        )}

        <span className="text-lapis-accent">{icon}</span>

        <span className="font-semibold flex-1">{stage.name}</span>

        {stage.domain_amended && (
          <span className="text-xs text-amber-400">amended</span>
        )}
        {stage.problem_amended && (
          <span className="text-xs text-amber-400">amended</span>
        )}

        <span className={cn('badge', badge.className)}>{badge.label}</span>

        {stage.duration > 0 && (
          <span className="flex items-center gap-1 text-xs text-lapis-muted ml-2">
            <Clock className="w-3 h-3" />
            {formatDuration(stage.duration)}
          </span>
        )}
      </div>

      {/* Preview (collapsed) */}
      {!isExpanded && preview && (
        <div
          className={cn(
            'mt-2 font-mono text-xs p-2 rounded bg-lapis-bg/50 text-lapis-text-secondary',
            'max-h-20 overflow-hidden whitespace-pre-wrap',
            stage.status === 'error' && 'text-red-400'
          )}
        >
          {truncate(preview, 200)}
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
                <pre className="pddl-code text-xs max-h-64 overflow-auto">
                  {stage.domain_pddl}
                </pre>
              </div>
            )}

          {/* Adequacy Analysis */}
          {stage.name === 'Domain Adequacy Check' && stage.adequacy_analysis && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">
                Adequacy Analysis
              </div>
              <pre className="bg-lapis-bg/50 p-3 rounded text-xs text-lapis-text-secondary whitespace-pre-wrap">
                {stage.adequacy_analysis}
              </pre>
            </div>
          )}

          {/* CoT Steps */}
          {stage.cot_steps && stage.cot_steps.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">
                Chain of Thought Steps
              </div>
              <div className="space-y-2">
                {stage.cot_steps.map((step) => (
                  <div key={step.step} className="bg-lapis-bg/50 p-2 rounded">
                    <div className="text-xs font-semibold text-lapis-accent mb-1">
                      Step {step.step}: {step.label}
                    </div>
                    <pre className="text-xs text-lapis-text-secondary whitespace-pre-wrap">
                      {step.content}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Problem PDDL */}
          {stage.name === 'Problem Generation' && stage.problem_pddl && (
            <div>
              <div className="text-xs font-semibold text-lapis-muted mb-1">Problem PDDL</div>
              <pre className="pddl-code text-xs max-h-64 overflow-auto">
                {stage.problem_pddl}
              </pre>
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
              <div className="refine-terminal">
                {stage.refinement_history.map((entry) => (
                  <div key={entry.iteration} className="mb-2">
                    <span className="refine-info">
                      ─── Iteration {entry.iteration}/{stage.refinement_history.length}{' '}
                      {entry.success ? '✓' : '✗'}
                    </span>
                    {entry.error && (
                      <div className="refine-err ml-4">Error: {truncate(entry.error, 200)}</div>
                    )}
                    {entry.fix && (
                      <div className="refine-ok ml-4">Fix: {truncate(entry.fix, 200)}</div>
                    )}
                  </div>
                ))}
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
