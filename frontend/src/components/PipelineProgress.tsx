/**
 * PipelineProgress - Horizontal breadcrumb showing pipeline stage progress.
 *
 * States:
 * - pending (○) - grey text
 * - running (●) - blue pulsing pill
 * - done (✓) - green pill
 * - error (✗) - red pill
 * - skipped (⏭) - violet pill
 */
import { Check, Circle, X, SkipForward, ChevronRight, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { StageResult, StageStatus } from '@/types'

// Canonical stage order in the LAPIS pipeline
const STAGE_ORDER = [
  'NL Input',
  'Domain Generation',
  'Domain Adequacy Check',
  'Problem Generation',
  'Planning + Refinement',
  'Complete',
]

interface PipelineProgressProps {
  stages: StageResult[]
  className?: string
}

function getStageIcon(status: StageStatus | 'pending') {
  switch (status) {
    case 'done':
      return <Check className="w-3 h-3" />
    case 'running':
      return <Loader2 className="w-3 h-3 animate-spin" />
    case 'error':
      return <X className="w-3 h-3" />
    case 'skipped':
      return <SkipForward className="w-3 h-3" />
    default:
      return <Circle className="w-3 h-3" />
  }
}

function getStageClass(status: StageStatus | 'pending'): string {
  switch (status) {
    case 'done':
      return 'pip-done'
    case 'running':
      return 'pip-active'
    case 'error':
      return 'pip-error'
    case 'skipped':
      return 'bg-violet-500/20 text-violet-300 border border-violet-500/40 rounded-full px-3 py-1 text-xs font-semibold'
    default:
      return 'pip-pending'
  }
}

export function PipelineProgress({ stages, className }: PipelineProgressProps) {
  if (stages.length === 0) {
    return null
  }

  // Build status map from stages
  const statusMap = new Map<string, StageStatus>()
  let activeStage: string | null = null

  for (const stage of stages) {
    statusMap.set(stage.name, stage.status)
    if (stage.status === 'running') {
      activeStage = stage.name
    }
  }

  // If no stage is running but some are done, mark as complete
  const allDone = stages.every((s) => s.status === 'done' || s.status === 'skipped')
  if (allDone && stages.length > 0) {
    activeStage = 'Complete'
    statusMap.set('Complete', 'done')
  }

  // Mark NL Input as done if we have any stages
  statusMap.set('NL Input', 'done')

  return (
    <div className={cn('flex items-center flex-wrap gap-1 py-2 mb-3', className)}>
      {STAGE_ORDER.map((stageName, index) => {
        const status = statusMap.get(stageName) || 'pending'
        const isActive = stageName === activeStage

        return (
          <div key={stageName} className="flex items-center">
            <span
              className={cn(
                'flex items-center gap-1.5 transition-all duration-200',
                getStageClass(isActive ? 'running' : status)
              )}
            >
              {getStageIcon(isActive ? 'running' : status)}
              <span className="whitespace-nowrap">{stageName}</span>
            </span>

            {index < STAGE_ORDER.length - 1 && (
              <ChevronRight className="w-4 h-4 text-slate-600 mx-1" />
            )}
          </div>
        )
      })}
    </div>
  )
}

export default PipelineProgress
