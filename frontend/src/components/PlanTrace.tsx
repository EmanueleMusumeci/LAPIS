/**
 * PlanTrace - Interactive plan step-through component.
 *
 * Features:
 * - Slider navigation (1 to N steps)
 * - Prev/Next buttons
 * - Current action banner
 * - Full action list with active highlighting
 * - Blocksworld state simulator at each step
 * - Generic PDDL state viewer for other domains
 */
import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import * as Slider from '@radix-ui/react-slider'
import { cn } from '@/lib/utils'
import {
  normalizeAction,
  parseBWInitState,
  computeStateSequence,
  rebuildBWInit,
} from '@/lib/blocksworldSim'
import BlocksworldEditor from '@/components/editors/BlocksworldEditor'

interface PlanTraceProps {
  actions: string[]
  stepImages?: string[]   // Optional: URL to image for each step
  animationUrl?: string   // Optional: URL to full animation GIF
  /** Optional: problem PDDL for state simulation */
  problemPddl?: string
  /** Optional: domain name for choosing the right simulator */
  domainName?: string
  className?: string
}

// ─── Blocksworld inline simulator ────────────────────────────────────────────

function BlocksworldSim({
  problemPddl,
  actions,
  step,
}: {
  problemPddl: string
  actions: string[]
  step: number
}) {
  const stateSequence = useMemo(() => {
    const init = parseBWInitState(problemPddl)
    return computeStateSequence(init, actions)
  }, [problemPddl, actions])

  const stateAtStep = stateSequence[step] ?? stateSequence[stateSequence.length - 1]
  const problemAtStep = rebuildBWInit(problemPddl, stateAtStep)

  return (
    <div className="rounded-lg border border-lapis-border overflow-hidden">
      <BlocksworldEditor problemPddl={problemAtStep} onChange={() => {}} readOnly />
    </div>
  )
}

// ─── Generic PDDL fact viewer ─────────────────────────────────────────────────

function GenericStateBanner({ action, domainName }: { action: string; domainName: string }) {
  const norm = normalizeAction(action)
  const clean = norm.replace(/^\(|\)$/g, '').trim()
  const parts = clean.split(/\s+/)
  const name = parts[0] || ''
  const params = parts.slice(1)

  return (
    <div className="rounded-lg border border-lapis-border bg-lapis-card/60 p-3 text-sm">
      <span className="text-xs text-lapis-text-secondary uppercase tracking-wide mr-2">{domainName}</span>
      <span className="font-mono text-lapis-accent font-semibold">{name}</span>
      {params.length > 0 && (
        <span className="font-mono text-lapis-text-secondary ml-2">{params.join(' ')}</span>
      )}
    </div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export function PlanTrace({ actions, stepImages, animationUrl, problemPddl, domainName, className }: PlanTraceProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [showAnimation, setShowAnimation] = useState(false)

  // Normalize all actions once
  const normalizedActions = useMemo(() => actions.map(normalizeAction), [actions])

  const n = normalizedActions.length
  const hasImages = stepImages && stepImages.length === n
  const currentImage = hasImages ? stepImages[currentStep] : null

  if (n === 0) {
    return (
      <div className={cn('text-center text-lapis-muted py-4', className)}>
        No plan actions to display.
      </div>
    )
  }

  const handlePrev = () => setCurrentStep((prev) => Math.max(0, prev - 1))
  const handleNext = () => setCurrentStep((prev) => Math.min(n - 1, prev + 1))

  const currentAction = normalizedActions[currentStep]

  // Parse normalized action for display
  const clean = currentAction.replace(/^\(|\)$/g, '').trim()
  const parts = clean.split(/\s+/)
  const name = parts[0] || ''
  const params = parts.slice(1)

  const showBWSim = domainName === 'blocksworld' && problemPddl
  const showGenericBanner = !showBWSim && domainName && domainName !== 'custom'

  return (
    <div className={cn('space-y-4', className)}>
      {/* Animation Toggle */}
      {animationUrl && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-lapis-muted">Plan Visualization</span>
          <button
            onClick={() => setShowAnimation(!showAnimation)}
            className="px-3 py-1 text-xs rounded-lg bg-lapis-card border border-lapis-border hover:border-lapis-accent text-lapis-text transition-colors"
          >
            {showAnimation ? 'Show Step-by-Step' : 'Show Full Animation'}
          </button>
        </div>
      )}

      {/* Full Animation GIF */}
      {showAnimation && animationUrl && (
        <div className="border border-lapis-border rounded-lg overflow-hidden bg-lapis-bg">
          <img src={animationUrl} alt="Plan animation" className="w-full h-auto" />
        </div>
      )}

      {/* Step-by-step view */}
      {!showAnimation && (
        <>
          {/* Blocksworld simulator */}
          {showBWSim && (
            <BlocksworldSim
              problemPddl={problemPddl!}
              actions={normalizedActions}
              step={currentStep}
            />
          )}

          {/* Step image (if provided and no blocksworld sim) */}
          {!showBWSim && currentImage && (
            <div className="border border-lapis-border rounded-lg overflow-hidden bg-lapis-bg">
              <img src={currentImage} alt={`Step ${currentStep + 1}`} className="w-full h-auto" />
            </div>
          )}

          {/* Generic domain state banner */}
          {showGenericBanner && (
            <GenericStateBanner action={currentAction} domainName={domainName!} />
          )}

          {/* Navigation Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={handlePrev}
              disabled={currentStep === 0}
              className={cn(
                'p-2 rounded-lg transition-colors',
                currentStep === 0
                  ? 'bg-lapis-border text-lapis-muted cursor-not-allowed'
                  : 'bg-lapis-card hover:bg-lapis-accent/20 text-lapis-text'
              )}
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <div className="flex-1">
              <Slider.Root
                value={[currentStep]}
                onValueChange={([value]) => setCurrentStep(value)}
                min={0}
                max={n - 1}
                step={1}
                className="relative flex items-center select-none touch-none w-full h-5"
              >
                <Slider.Track className="bg-lapis-border relative grow rounded-full h-2">
                  <Slider.Range className="absolute bg-lapis-accent rounded-full h-full" />
                </Slider.Track>
                <Slider.Thumb
                  className={cn(
                    'block w-5 h-5 bg-lapis-accent rounded-full shadow-lg',
                    'hover:bg-lapis-accent/80 focus:outline-none focus:ring-2 focus:ring-lapis-accent/50',
                    'transition-colors cursor-pointer'
                  )}
                />
              </Slider.Root>
            </div>

            <button
              onClick={handleNext}
              disabled={currentStep === n - 1}
              className={cn(
                'p-2 rounded-lg transition-colors',
                currentStep === n - 1
                  ? 'bg-lapis-border text-lapis-muted cursor-not-allowed'
                  : 'bg-lapis-card hover:bg-lapis-accent/20 text-lapis-text'
              )}
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            <span className="text-sm text-lapis-muted min-w-[60px] text-right">
              {currentStep + 1} / {n}
            </span>
          </div>

          {/* Current Action Banner */}
          <div className="plan-current-action">
            <span className="text-lapis-muted text-sm">Step {currentStep + 1}</span>
            <span className="text-lapis-accent font-semibold">{name}</span>
            {params.length > 0 && (
              <span className="text-lapis-text-secondary">{params.join(' ')}</span>
            )}
          </div>

          {/* Action List */}
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {normalizedActions.map((action, i) => {
              const isActive = i === currentStep
              const isPast = i < currentStep
              const aClean = action.replace(/^\(|\)$/g, '').trim()
              const aParts = aClean.split(/\s+/)

              return (
                <div
                  key={i}
                  onClick={() => setCurrentStep(i)}
                  className={cn(
                    'plan-step cursor-pointer transition-all duration-150',
                    isActive && 'plan-step-active',
                    isPast && 'opacity-60'
                  )}
                >
                  <span
                    className={cn(
                      'w-8 text-right text-sm',
                      isActive ? 'text-lapis-accent font-semibold' : 'text-lapis-muted'
                    )}
                  >
                    {i + 1}.
                  </span>
                  <span className={cn('font-mono', isActive && 'text-lapis-accent')}>
                    ({aParts[0]}
                    {aParts.slice(1).length > 0 && <span className="text-lapis-text-secondary"> {aParts.slice(1).join(' ')}</span>})
                  </span>
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}

export default PlanTrace
